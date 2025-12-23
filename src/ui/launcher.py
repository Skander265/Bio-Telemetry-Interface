from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import os

APP_NAME = "Bio-Telemetry Interface"

class PlantBioLauncher(QtWidgets.QDialog):
    def __init__(self, current_config):
        super().__init__()
        self.config = current_config
        self.launch_approved = False 
        self.selected_csv_path = ""

        self.setWindowTitle(f"{APP_NAME} - Setup")
        self.resize(650, 850)
        
        self.setStyleSheet("""
            QDialog { 
                background-color: #121212; 
                color: #e0e0e0; 
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel { 
                color: #e0e0e0; 
                font-size: 36px; 
            }
            QGroupBox { 
                border: 1px solid #333; 
                border-radius: 6px; 
                margin-top: 24px; 
                font-weight: bold; 
                font-size: 34px;
                color: #00FF99; 
                background-color: #1a1a1a;
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 10px; 
                padding: 0 5px; 
            }
            QSpinBox { 
                background-color: #222; 
                color: #00FF99; 
                font-size: 38px; 
                padding: 8px; 
                border: 1px solid #444; 
                border-radius: 4px; 
                font-weight: bold;
            }
            QRadioButton { 
                spacing: 12px; 
                font-size: 35px;
                color: #ccc;
                padding: 8px;
            }
            QRadioButton::indicator { 
                width: 18px; 
                height: 18px; 
                border-radius: 9px;
                border: 2px solid #555;
            }
            QRadioButton::indicator:checked { 
                background-color: #00FF99;
                border-color: #00FF99;
            }
            QCheckBox {
                font-size: 35px;
                color: #ccc;
                spacing: 10px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px; height: 18px;
                border: 2px solid #555; border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #00CCFF; 
                border-color: #00CCFF;
            }
            QPushButton { 
                background-color: #006644; 
                color: white; 
                border-radius: 6px; 
                padding: 15px; 
                font-size: 30px; 
                font-weight: bold; 
                border: 1px solid #008855;
            }
            QPushButton:hover { 
                background-color: #009966; 
                border-color: #00FF99;
                color: #ffffff;
            }
            /* Disabled State Style */
            QPushButton:disabled {
                background-color: #333333;
                color: #555555;
                border: 1px solid #444444;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QtWidgets.QLabel(f"🌿 {APP_NAME}")
        title.setStyleSheet("font-size: 38px; font-weight: bold; color: #00FF99; margin-bottom: 5px;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QtWidgets.QLabel("System Configuration & Topology")
        subtitle.setStyleSheet("color: #666; font-size: 34px; font-style: italic; margin-bottom: 20px;")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(subtitle)

        # 1. Operational Mode
        mode_group = QtWidgets.QGroupBox("OPERATIONAL MODE")
        mode_layout = QtWidgets.QVBoxLayout()
        mode_layout.setSpacing(5)
        mode_layout.setContentsMargins(15, 25, 15, 15)
        
        self.radio_monitor = QtWidgets.QRadioButton("MONITOR (Active Security)")
        self.radio_monitor.setChecked(not self.config['force_retrain'])
        
        self.radio_train = QtWidgets.QRadioButton("CALIBRATE (Model Retraining)")
        self.radio_train.setChecked(self.config['force_retrain'])
        
        mode_layout.addWidget(self.radio_monitor)
        mode_layout.addWidget(self.radio_train)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # 2. Data Source & Topology
        source_group = QtWidgets.QGroupBox("DATA SOURCE")
        source_layout = QtWidgets.QFormLayout()
        source_layout.setContentsMargins(15, 25, 15, 15)
        source_layout.setSpacing(15)

        self.radio_live = QtWidgets.QRadioButton("Live / Mock Generator")
        self.radio_live.setChecked(True)
        self.radio_live.toggled.connect(self.toggle_source_mode)
        
        self.radio_csv = QtWidgets.QRadioButton("Playback CSV File")
        # Note: We don't need to connect radio_csv separately, radio_live covers the toggle
        
        self.file_btn = QtWidgets.QPushButton("Select CSV Data...")
        self.file_btn.clicked.connect(self.browse_file)
        self.file_btn.setStyleSheet("font-size: 24px; padding: 10px;")
        self.file_btn.setEnabled(False)
        
        self.lbl_filename = QtWidgets.QLabel("No file selected")
        self.lbl_filename.setStyleSheet("color: #888; font-size: 18px;")

        source_layout.addRow(self.radio_live)
        source_layout.addRow(self.radio_csv)
        source_layout.addRow(self.file_btn, self.lbl_filename)
        
        self.leaf_spinner = QtWidgets.QSpinBox()
        self.leaf_spinner.setRange(1, 100)
        self.leaf_spinner.setValue(self.config['leaf_sensor_count'])
        
        lbl_leaf = QtWidgets.QLabel("Leaf Sensors used:")
        source_layout.addRow(lbl_leaf, self.leaf_spinner)

        source_group.setLayout(source_layout)
        layout.addWidget(source_group)

        # 3. Processing
        filter_group = QtWidgets.QGroupBox("PROCESSING & FEEDBACK")
        filter_layout = QtWidgets.QFormLayout()
        filter_layout.setContentsMargins(15, 25, 15, 15)
        filter_layout.setSpacing(15)
        
        self.smooth_spinner = QtWidgets.QSpinBox()
        self.smooth_spinner.setRange(1, 50)
        self.smooth_spinner.setValue(self.config['filter_window_size'])
        
        self.chk_audio = QtWidgets.QCheckBox("Enable Bio-Synth Audio")
        self.chk_audio.setChecked(self.config.get('enable_audio', False))
        
        lbl_smooth = QtWidgets.QLabel("Smoothing Factor:")
        filter_layout.addRow(lbl_smooth, self.smooth_spinner)
        filter_layout.addRow(self.chk_audio)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        layout.addStretch()

        self.btn_start = QtWidgets.QPushButton(f"INITIALIZE SYSTEM")
        self.btn_start.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_start.clicked.connect(self.start_system)
        layout.addWidget(self.btn_start)

        # Initial check to set correct state at startup
        self.validate_start_button()

    def toggle_source_mode(self):
        is_csv = self.radio_csv.isChecked()
        self.file_btn.setEnabled(is_csv)
        
        # Style update for file button
        if is_csv:
            self.file_btn.setStyleSheet("background-color: #006644; color: white; font-size: 24px; padding: 10px;")
        else:
            self.file_btn.setStyleSheet("background-color: #333; color: #888; font-size: 24px; padding: 10px;")
            
        # Re-check if start button should be enabled
        self.validate_start_button()

    def browse_file(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Voltage CSV', os.getcwd(), "CSV Files (*.csv)")
        if fname:
            self.selected_csv_path = fname
            self.lbl_filename.setText(os.path.basename(fname))
            self.radio_csv.setChecked(True)
            self.validate_start_button()

    def validate_start_button(self):
        """Disables the start button if CSV mode is selected but no file is chosen."""
        if self.radio_csv.isChecked() and not self.selected_csv_path:
            self.btn_start.setEnabled(False)
            self.btn_start.setText("SELECT A FILE FIRST")
            self.btn_start.setStyleSheet("background-color: #333; color: #666; border: 1px solid #444;")
        else:
            self.btn_start.setEnabled(True)
            self.btn_start.setText("INITIALIZE SYSTEM")
            self.btn_start.setStyleSheet("""
                QPushButton { background-color: #006644; color: white; border: 1px solid #008855; }
                QPushButton:hover { background-color: #009966; border-color: #00FF99; }
            """)

    def start_system(self):
        self.config['leaf_sensor_count'] = self.leaf_spinner.value()
        self.config['filter_window_size'] = self.smooth_spinner.value()
        self.config['force_retrain'] = self.radio_train.isChecked()
        self.config['enable_audio'] = self.chk_audio.isChecked()
        
        if self.radio_csv.isChecked() and self.selected_csv_path:
            self.config['use_csv_input'] = True
            self.config['csv_file_path'] = self.selected_csv_path
        else:
            self.config['use_csv_input'] = False
        
        self.launch_approved = True
        self.accept()