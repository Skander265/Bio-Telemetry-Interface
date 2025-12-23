from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
import numpy as np
from utils import logger

class PlantMonitorWindow(QtWidgets.QMainWindow):
    def __init__(self, data_queue, stop_event, leaf_count, total_sensors):
        super().__init__()
        self.data_queue = data_queue
        self.stop_event = stop_event
        self.leaf_count = leaf_count
        self.total_sensors = total_sensors
        
        self.logger = logger.EventLogger()
        self.alarm_count = 0

        self.setWindowTitle(f"Bio-Telemetry Interface - Live Monitor")
        self.resize(1200, 900)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QLabel { color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
            QWidget { background-color: #121212; }
        """)
        
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        self.status_container = QtWidgets.QFrame()
        self.status_container.setStyleSheet("background-color: #1e1e1e; border-radius: 5px; border: 1px solid #333;")
        status_layout = QtWidgets.QHBoxLayout(self.status_container)
        
        self.status_label = QtWidgets.QLabel("STATUS: ACTIVE MONITORING")
        self.status_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #00FF99; border: none; background: transparent;")
        
        status_layout.addWidget(self.status_label)
        main_layout.addWidget(self.status_container)

        pg.setConfigOption('background', '#1e1e1e')
        pg.setConfigOption('foreground', '#888888')

        self.curves = [] 
        self.data_buffers = [np.zeros(500) for _ in range(self.total_sensors)]
        
        self.root_plot = pg.PlotWidget(title="<span style='color: #FFaa00; font-size: 14pt'>ROOT SYSTEM (Channel 1)</span>")
        self.setup_plot_style(self.root_plot)
        root_curve = self.root_plot.plot(pen=pg.mkPen(color='#FFaa00', width=3, style=QtCore.Qt.SolidLine))
        self.curves.append(root_curve)
        main_layout.addWidget(self.root_plot)

        self.stem_plot = pg.PlotWidget(title="<span style='color: #00CCFF; font-size: 14pt'>MAIN STEM (Channel 2)</span>")
        self.setup_plot_style(self.stem_plot)
        stem_curve = self.stem_plot.plot(pen=pg.mkPen(color='#00CCFF', width=3, style=QtCore.Qt.SolidLine))
        self.curves.append(stem_curve)
        main_layout.addWidget(self.stem_plot)

        self.leaf_plot = pg.PlotWidget(title=f"<span style='color: #00FF99; font-size: 14pt'>LEAF NETWORK ({self.leaf_count} Nodes)</span>")
        self.setup_plot_style(self.leaf_plot)
        
        for i in range(self.leaf_count):
            leaf_curve = self.leaf_plot.plot(pen=pg.mkPen(color=(0, 255, 153, 150), width=2)) 
            self.curves.append(leaf_curve)
            
        main_layout.addWidget(self.leaf_plot)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(16)

    def setup_plot_style(self, plot_widget):
        """Helper to apply consistent dark styling to plots"""
        plot_widget.setYRange(0, 5)
        plot_widget.showGrid(x=True, y=True, alpha=0.2)
        plot_widget.getAxis('left').setPen('#555555')
        plot_widget.getAxis('bottom').setPen('#555555')
        plot_widget.setStyleSheet("border: 1px solid #333; border-radius: 5px;")

    def update_gui(self):
        while not self.data_queue.empty():
            packet = self.data_queue.get()
            voltages = packet['voltages']
            statuses = packet['statuses']

            for i in range(self.total_sensors):
                self.data_buffers[i] = np.roll(self.data_buffers[i], -1)
                self.data_buffers[i][-1] = voltages[i]
                
                self.check_status(i, statuses[i])

        for i in range(self.total_sensors):
            self.curves[i].setData(self.data_buffers[i])

    def check_status(self, idx, status_dict):
        event_type = status_dict.get("type", "UNKNOWN")
        
        
        if event_type == "ALARM":
            location = self.get_location_name(idx)
            self.status_label.setText(f"ANOMALY DETECTED: {location}")
            self.status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FF0055; background: transparent;")
            self.logger.log_event(f"ALARM_{location}", status_dict['peak'], status_dict['duration'])
            
        elif event_type == "LEARNING" or event_type == "CALIBRATING":
            msg = status_dict.get("message", "Calibrating...")
            self.status_label.setText(f"NEURAL TRAINING: {msg}")
            self.status_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFD700; background: transparent;")
            
        elif event_type == "CALIBRATION_COMPLETE" and "ANOMALY" not in self.status_label.text():
            self.status_label.setText("SYSTEM ARMED & SECURE")
            self.status_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #00FF99; background: transparent;")

    def get_location_name(self, idx):
        if idx == 0: return "ROOT"
        elif idx == 1: return "STEM"
        else: return f"LEAF {idx-1}"

    def closeEvent(self, event):
        self.stop_event.set()
        event.accept()