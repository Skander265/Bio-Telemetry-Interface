import numpy as np
import os
import joblib  
from sklearn.ensemble import IsolationForest
from typing import Dict, List, Union

class SignalAnalyst:
    """
    Analyzes real-time sensor data to detect anomalies using an Isolation Forest model.
    Manages the lifecycle of the model (Calibration -> Inference -> Persistence).
    """

    def __init__(self, sensor_id: str = "default"):
        self.sensor_id = sensor_id
        self.model_filename = f"models/model_{self.sensor_id}.pkl"
        
        # Signal Processing Constants
        self.threshold = 0.8      
        self.min_samples = 15       
        
        # State Management
        self.recording = False      
        self.buffer = []            
        self.calibration_data = []  
        
        if not os.path.exists("models"):
            os.makedirs("models")

        # MODEL INITIALIZATION 
        if os.path.exists(self.model_filename):
            print(f"[{self.sensor_id}] System Startup: Loading serialized model from disk...")
            self.model = joblib.load(self.model_filename)
            self.is_calibrated = True
        else:
            print(f"[{self.sensor_id}] System Startup: No existing model found. initializing new Isolation Forest.")
            # n_estimators=100: Number of trees in the forest
            # contamination at auto
            self.model = IsolationForest(n_estimators=100, contamination='auto', random_state=42)
            self.is_calibrated = False

    def update(self, voltage: float) -> Dict[str, str]:
        """
        Ingests a single data point. State machine switches between Scanning and Recording.
        """
        # STATE: SCANNING
        if not self.recording:
            if voltage > self.threshold:
                self.recording = True
                self.buffer = [voltage]
                return {"type": "Recording"} 
            return {"type": "Scanning"}

        # STATE: RECORDING
        else:
            self.buffer.append(voltage)
            
            # End condition: Signal drops below threshold OR buffer overflows
            signal_drop = (len(self.buffer) > 10 and voltage < self.threshold)
            timeout = len(self.buffer) > 100
            
            if signal_drop or timeout:
                result = self.process_event(self.buffer)
                self.recording = False
                self.buffer = [] # reset buffer
                return result
                
            return {"type": "Recording"}

    def process_event(self, raw_signal: List[float]) -> Dict[str, Union[str, float]]:
        """
        Extracts features from the raw signal and passes them to the model logic.
        """
        features = self.extract_features(raw_signal)
        
        # PHASE 1: CALIBRATION (data collection) 
        if not self.is_calibrated:
            self.calibration_data.append(features)
            samples_remaining = self.min_samples - len(self.calibration_data)
            
            if samples_remaining == 0:
                print(f"[{self.sensor_id}] Calibration Limit Reached. Fitting model to baseline data...")
                
                #fit the Isolation Forest to the gathered baseline
                self.model.fit(self.calibration_data)
                self.is_calibrated = True
                
                #save the model state
                joblib.dump(self.model, self.model_filename)
                print(f"[{self.sensor_id}] Model Serialized to {self.model_filename}")
                
                return {
                    "type": "CALIBRATION_COMPLETE", 
                    "peak": features[0], 
                    "duration": len(raw_signal)
                }
            
            return {
                "type": "CALIBRATING", 
                "message": f"Acquiring Baseline",
                "peak": features[0],
                "duration": len(raw_signal)
            }

        #PHASE 2: INFERENCE (Anomaly Detection)
        else:
            # scikit requires 2d array for prediction
            feature_vector = np.array([features])
            
            # Predict: 1 = Inliers (Normal), -1 = Outliers (Anomaly)
            prediction = self.model.predict(feature_vector)[0]
            
            # Decision Function: Negative scores represent outliers
            score = self.model.decision_function(feature_vector)[0]

            if prediction == -1:
                return {
                    "type": "ALARM", 
                    "message": f"Anomaly Detected (Score: {score:.3f})",
                    "peak": features[0],
                    "duration": len(raw_signal)
                }
            else:
                return {
                    "type": "IGNORE", 
                    "message": "Baseline Signal",
                    "peak": features[0],
                    "duration": len(raw_signal)
                }

    def extract_features(self, signal: List[float]) -> List[float]:
        """
        Vectorizes the raw signal into a feature array: [Peak Amplitude, Signal Energy, Rise Time]
        """
        arr = np.array(signal)
        
        # Feature 1: Peak Amplitude (Max Voltage)
        peak = np.max(arr)
        
        # Feature 2: Signal Energy (Sum of Squares)
        energy = np.sum(arr ** 2)
        
        # Feature 3: Rise Time (Index of Peak)
        peak_index = np.argmax(arr)
        rise_time = peak_index if peak_index > 0 else 1
        
        return [peak, energy, rise_time]