import threading
import queue
import sys
import shutil 
import os
from PyQt5 import QtWidgets

# Project Imports
from utils import audio_feedback
import utils.noise_filter as noise_filter
import processing.signal_analyst as signal_analyst
import reader.serial_reader as serial_reader  
import reader.mock_reader as mock_reader  
import reader.csv_reader as csv_reader # NEW IMPORT
import ui.gui_window as gui_window
import utils.config_loader as config_loader
import ui.launcher as launcher 

CONFIG = {}

def clean_models_if_needed():
    """If user requested a re-train, delete the old brains."""
    if CONFIG.get("force_retrain", False):
        if os.path.exists("models"):
            print("PURGING OLD MODELS (Force Retrain Selected)...")
            shutil.rmtree("models")
            os.makedirs("models")

def data_worker(data_queue, stop_event):
    #  Hardware/Mock/CSV Initialization
    mode = 'MOCK'
    
    # PRIORITY 1: CSV Playback
    if CONFIG.get("use_csv_input", False) and CONFIG.get("csv_file_path"):
        print(f"Starting CSV Playback Mode: {CONFIG['csv_file_path']}")
        mode = 'CSV'
        source = csv_reader.CsvReader(CONFIG['csv_file_path'])
        
    # PRIORITY 2: Hardware / Mock
    else:
        detected_port = None
        if not CONFIG["force_mock_mode"]:
            if CONFIG["serial_port"] != "AUTO":
                 detected_port = CONFIG["serial_port"]
            else:
                 detected_port = serial_reader.find_available_port()

        if detected_port:
            print(f"Hardware found on {detected_port}")
            mode = 'SERIAL'
            source = serial_reader.connect_serial(detected_port)
        else:
            print(f"Starting Mock Mode: 1 Root, 1 Stem, {CONFIG['leaf_sensor_count']} Leaves")
            mode = 'MOCK'
            source = mock_reader.MockReader(leaf_count=CONFIG['leaf_sensor_count'])

    #  Filter & Model Initialization
    total = CONFIG["total_sensors"]
    window_size = CONFIG["filter_window_size"]
    
    filters = [noise_filter.MovingAverageFilter(window_size) for _ in range(total)]
    
    brains = []
    for i in range(total):
        if i == 0: s_id = "root"
        elif i == 1: s_id = "stem"
        else: s_id = f"leaf_{i-1}"
        brains.append(signal_analyst.SignalAnalyst(sensor_id=s_id))

    # Audio Engine Initialization
    audio_enabled = CONFIG.get("enable_audio", False)
    synth = audio_feedback.AudioSynthesizer() 
    
    if audio_enabled:
        synth.start()
    
    #  Main Data Loop
    while not stop_event.is_set():
        if mode == 'SERIAL':
            t, voltages = serial_reader.read_line(source) 
        elif mode == 'CSV':
            t, voltages = source.read_line()
        else:
            t, voltages = source.read_line()

        if not voltages or len(voltages) != total: 
            continue
            
        processed_voltages = []
        sensor_statuses = []

        for i in range(total):
            smooth_v = filters[i].apply(voltages[i])
            processed_voltages.append(smooth_v)
            status = brains[i].update(smooth_v)
            sensor_statuses.append(status)
        
        # Audio Update 
        if audio_enabled:
            highest_activity = max(processed_voltages)
            synth.update_voltage(highest_activity)

        packet = {
            'time': t, 
            'voltages': processed_voltages, 
            'statuses': sensor_statuses
        }
        data_queue.put(packet)
    
    # Cleanup
    if audio_enabled:
        synth.stop()


def main():
    global CONFIG
    
    app = QtWidgets.QApplication(sys.argv)
    
    current_config = config_loader.load_config()
    
    launch_dialog = launcher.PlantBioLauncher(current_config)
    if launch_dialog.exec_() == QtWidgets.QDialog.Accepted:
        
        CONFIG = launch_dialog.config
        CONFIG = config_loader.calculate_derived(CONFIG) # Recalculate totals
        config_loader.save_config(CONFIG)
        
        clean_models_if_needed()

        data_queue = queue.Queue()
        stop_event = threading.Event()

        worker = threading.Thread(target=data_worker, args=(data_queue, stop_event))
        worker.daemon = True 
        worker.start()

        window = gui_window.PlantMonitorWindow(
            data_queue, 
            stop_event, 
            leaf_count=CONFIG["leaf_sensor_count"], 
            total_sensors=CONFIG["total_sensors"]
        )
        window.show()
        
        sys.exit(app.exec_())
    else:
        print("Launcher canceled. Exiting.")
        sys.exit(0)

if __name__ == "__main__":
    main()