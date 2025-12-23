# 🌿 Bio-Telemetry Interface: Botanical Intrusion Detector

This project acts as a bridge between organic life and digital systems. It monitors the bioelectric potential (voltage) of living plants in real-time to detect external stimuli. By analyzing these micro-voltage changes, the system can distinguish between background noise (wind, growth) and deliberate intrusion (human touch, cutting, or burning).

## System Architecture

The application is built on a modular pipeline designed for low-latency signal processing:

### 1. Signal Acquisition Layer

* Hardware Bridge: Reads raw analog voltage (0-5V) via Serial/USB from an Arduino.
* Virtual Plant Generator: A physics-based mock engine that simulates organic noise and random voltage spikes for testing without hardware.
* Forensic Replay: Loads historical .csv voltage data to train the AI on specific scenarios.

### 2. Signal Processing & Intelligence

* Noise Filtration: Implements a Moving Average Filter to smooth out high-frequency electrical noise (60Hz hum) while preserving the shape of organic spikes.
* Anomaly Detection Engine: Uses Scikit-Learn's Isolation Forest. Each sensor (Root, Stem, Leaf) has its own dedicated machine learning model that learns the "baseline" behavior of the plant during a calibration phase.
* State Machine Logic: Automatically switches sensors between states like Calibrating and Monitoring.

### 3. Human-Machine Interface (HMI)

* Real-Time Dashboard: A high-performance PyQt5 & PyQtGraph interface rendering live bio-signals.
* Bio-Synth Sonification: A generative audio engine that converts voltage fluctuations into sound. The plant "sings" a low drone when calm and shrieks when disturbed.

---

## Key Features

* Neural Calibration: The system spends the first 15 seconds "learning" the plant's normal electrical activity. It adapts to the specific noise floor of your environment automatically.
* Auditory Feedback: Enable "Bio-Synth" to hear the plant's nervous system. Pitch modulates based on the highest voltage detected in the network.
* Dataset Training: Import your own .csv files to train the detection models on pre-recorded events.

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Usage

Run the main entry point to open the System Launcher:

```bash
python src/main.py
```

### The Launcher Config

Before the monitoring starts, you can configure:

1. Operational Mode:

* Monitor: Load existing AI models (instant start).
* Calibrate: Force the AI to relearn the plant's signals (may take some time).

2. Data Source:

* Live/Mock: Use real Arduino or the internal simulator.
* Playback CSV: Select a file to simulate a specific attack pattern.

3. Topology: Define how many leaf sensors are connected.

---

## Hardware Setup (Optional)

To use this with a real plant, you need:

* Microcontroller: Arduino Uno/Nano or ESP32.
* Probes: Ag/AgCl electrodes or simple alligator clips.
* Positive Probe: Attach to the leaf/stem.
* Ground Probe: Insert into the soil (Root).
* Circuit: Simple voltage divider or Op-Amp (instrumentation amplifier) recommended for cleaner signals.