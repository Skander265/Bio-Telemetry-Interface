import csv
import time
import os

class CsvReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = []
        self.index = 0
        self.start_time = int(time.time() * 1000)
        
        print(f"Loading Dataset: {self.file_path}")
        self._load_file()

    def _load_file(self):
        if not os.path.exists(self.file_path):
            print("Error: File not found.")
            return

        try:
            with open(self.file_path, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                start_row = 0
                try:
                    float(rows[0][0])
                except ValueError:
                    print("   -> Detected Header row. Skipping.")
                    start_row = 1
                
                # Parse Data
                for row in rows[start_row:]:
                    try:
                        # Extract only voltage columns 
                        float_row = [float(x) for x in row if x.replace('.','',1).isdigit()]
                        if float_row:
                            self.data.append(float_row)
                    except ValueError:
                        continue
                        
            print(f"   -> Loaded {len(self.data)} samples.")

        except Exception as e:
            print(f"CSV Load Error: {e}")

    def read_line(self):
        """Returns the next row of data. Loops back to start if finished."""
        if not self.data:
            time.sleep(1) # Sleep to prevent CPU spike if file empty
            return 0, []

        # If we hit the end, go back to 0
        if self.index >= len(self.data):
            self.index = 0 

        voltages = self.data[self.index]
        self.index += 1
        
        # Simulate real-time sensor delay
        time.sleep(0.02)
        
        current_time = int(time.time() * 1000) - self.start_time
        return current_time, voltages