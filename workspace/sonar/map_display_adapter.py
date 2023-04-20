import pandas as pd
import numpy as np
import time
import os

class MapDisplayAdapter:

    class QrInformation:
        
        def __init__(self, id, x, y):
            self.id = id
            self.x = x
            self.y = y
        
        def __str__(self):
            return "{}: ({},{})".format(self.id, self.x, self.y)

        def __repr__(self):
            return self.__str__()

    shared_file = "sharedFileMapDisplay.csv"

    def __init__(self):
        self.__read_data()

    def clean_data(self):
        f = open(self.shared_file, "w")
        f.write("id,x,y\n")
        f.close()

    def get_qrs_information(self):
        self.__read_data()
        qrs_info = []
        for index in self.data_df.index.values:
            if index != "robot":
                qrs_info.append(self.QrInformation(index, self.data_df.loc[index]["x"], self.data_df.loc[index]["y"]))
        return np.array(qrs_info)

    def get_robot_location(self):
        self.__read_data()
        robot_row = self.data_df.loc["robot"]
        return (robot_row["x"], robot_row["y"])

    def write_data(self, robot_position, qrs_data):        
        f = open(self.shared_file, "w")
        f.write("id,x,y\n")
        if not robot_position == None: 
            f.write("\"robot\",{},{}\n".format(robot_position[0], robot_position[1]))
        for elem in qrs_data:
            f.write("\"{}\",{},{}\n".format(elem.id, elem.point[0], elem.point[1]))
        f.close()

    def has_new_data(self):
        return self.last_accesed < os.path.getmtime(self.shared_file)
    
    def __read_data(self):
        self.last_accesed = time.time()
        self.data_df = pd.read_csv(self.shared_file).set_index("id")

