import numpy as np

class QrMapPosition:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.position = np.array([x, y])
