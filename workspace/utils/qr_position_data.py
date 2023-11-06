class QrPositionData:
    
    def __init__(self, id, distance, angle):
        self.id = id
        self.distance = distance
        self.angle = angle
    
    def __str__(self):
        return '{}: {} cm away at {:2f} degrees'.format(self.id, self.distance, self.angle)
    
    def __repr__(self):
        return self.__str__()