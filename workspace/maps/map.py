import numpy as np
import json

from workspace.maps.qr_position import QrMapPosition

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
            qrs = []
            for qr in map_dict['qrs']:
                qrs.append(QrMapPosition(qr['id'], qr['position']['x'], qr['position']['y']))
            self.qrs = np.array(qrs)
