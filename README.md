# Bio-Telemetry Interface: Botanical Intrusion Detector

This system monitors the bioelectric voltage of living plants to detect external stimuli. It acts as a bridge between organic life and digital systems, using machine learning to distinguish between natural background noise and deliberate intrusions like cutting or burning.

## Hardware Setup (For Live Mode)

To use this with a real plant, you need an Arduino (Uno/Nano/ESP32) communicating via Serial/USB.

Probes: Use Ag/AgCl electrodes or standard alligator clips.
Signal (+): Clip gently onto the leaf or stem.
Ground (-): Insert a metal spike or probe deep into the moist soil (root system).


Circuit:
* Recommended: Use an Instrumentation Amplifier (like the AD620) to boost micro-voltage changes and reduce noise.
* Basic: A simple voltage divider can detect strong trauma signals, but may miss subtle interactions.
* Input: The software expects a standardized analog signal (0-5V) mapped to the Arduino's analog pins.



## Quick Start

```bash
pip install -r requirements.txt
python src/main.py
```

## Data analysis

The system uses Isolation Forest (Scikit-Learn) for unsupervised anomaly detection.

* Preprocessing: A Moving Average Filter cleans raw signals to remove high-frequency noise (like 60Hz hum) while preserving organic spike shapes.
* Training: Each sensor (Root, Stem, Leaf) trains its own independent model during the "Calibration" phase to learn the specific plant's baseline behavior.
* Inference: Once trained, any voltage pattern that deviates significantly from the learned baseline is immediately flagged as an intrusion.

## Modes & Features

* Live Mode: Reads real-time voltage from the hardware bridge.
* Mock Mode: Generates physics-based plant signals (noise + random spikes) for testing without hardware.
* Playback Mode: Loads .csv files to replay and analyze historical data.
* Bio-Synth: Converts voltage fluctuations into real-time audio. The plant "drones" when calm and goes higher pitch when disturbed.
