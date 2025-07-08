from collections import deque

class MovingAverageFilter:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.buffer = deque(maxlen=window_size)

    def apply(self, value):
        self.buffer.append(value)
        return sum(self.buffer) / len(self.buffer)
