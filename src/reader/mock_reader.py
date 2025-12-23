import time
import numpy as np
import random

class MockReader:
    def __init__(self, leaf_count=3):
        self.leaf_count = leaf_count
        self.start_time = int(time.time() * 1000)
        self.tick = 0
        
        # tate variables to hold the spike
        self.spike_frames_left = 0
        self.spike_target = None
        self.spike_leaf_index = 0

    def read_line(self):
        # 1. Base Noise
        root = np.random.normal(0.5, 0.1)
        stem = np.random.normal(0.5, 0.02)
        leaves = list(np.random.normal(0.5, 0.05, self.leaf_count))

        #TRIGGER LOGIC
        if self.spike_frames_left == 0 and self.tick % 100 == 0:
            
            # 70% chance to spike whenever check
            if random.random() > 0.3:
                self.spike_frames_left = 10  # Hold for 0.2s
                
                # WEIGHTED CHOICE: 80% chance for Leaf, 20% Root, 20% Stem
                rand_val = random.random()
                if rand_val < 0.2:
                    self.spike_target = 'root'
                elif rand_val < 0.4:
                    self.spike_target = 'stem'
                else:
                    self.spike_target = 'leaf'
                
                self.spike_leaf_index = random.randint(0, self.leaf_count - 1)

        if self.spike_frames_left > 0:
            spike_voltage = 4.0
            
            if self.spike_target == 'root':
                root += spike_voltage
            elif self.spike_target == 'stem':
                stem += spike_voltage
            else:
                leaves[self.spike_leaf_index] += spike_voltage
            
            self.spike_frames_left -= 1

        self.tick += 1
        time.sleep(0.02)
        
        current_time = int(time.time() * 1000) - self.start_time
        full_sensor_list = [root, stem] + leaves
        
        return current_time, full_sensor_list