import numpy as np
import json

from workspace.maps.qr_position import QrMapPosition
from workspace.maps.ball_position import BallPosition

class Map:
    def __init__(self, json_path):
        self.qrs = []
        self.width = 0
        self.height = 0
        self.load_map(json_path)

    def load_map(self, json_path):
        with open(json_path, 'r') as json_file:
            map_dict = json.load(json_file)
            boundaries = map_dict['boundaries']
            self.width = boundaries['width']
            self.height = boundaries['height']
            self.qrs = self.__map_qrs(map_dict)
            self.balls = self.__map_balls(map_dict)


    def __map_balls(self, map_dict):
        balls = []
        for ball in map_dict["balls"]:
            balls.append(BallPosition(ball["position"]["x"], ball["position"]["y"]))
        return np.array(balls)


    def __map_qrs(self, map_dict):
        qrs = []
        for qr in map_dict['qrs']:
            qrs.append(QrMapPosition(qr['id'], qr['position']['x'], qr['position']['y']))
        return np.array(qrs)
