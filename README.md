# Bioelectric Plant Event Detector

this project explores how plants react to external stimuli. While plants may seem static, they emit small bioelectric signals that change in response to their environment. This tool acts as a translator for those signals, turning raw voltage into events.

the system functions as a plant security alarm. it monitors bioelectric activity and uses a custom algorithm to distinguish between a deliberate human touch (a sharp spike) and random environmental noise (wind or interference).

this tool should work with sensors connected to an Arduino card. If you don't have an Arduino connected, the script will automatically generate synthetic data so you can test the detection logic.

the application runs a real-time analysis loop
1.  **Reads Signal:** captures voltage data from an Arduino or generates a simulation if no hardware is found.
2.  **Filters Noise:** smooths out the raw electrical input.
3.  **Classifies Events:** uses a state machine to measure the peak and duration of every spike, determining if it is a "Touch" (Alarm) or just background noise.

### 1. Installation
Install the necessary Python libraries:
`pip install matplotlib numpy pyserial`

### 2. Running the Project
`python src/main.py`
