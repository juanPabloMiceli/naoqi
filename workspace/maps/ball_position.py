import numpy as np

class BallPosition:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.position = np.array([x, y])
