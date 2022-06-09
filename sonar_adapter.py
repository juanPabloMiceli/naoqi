import pandas as pd
import time
import os

class SonarAdapter:
    shared_file = "sharedFile.csv"

    def __init__(self):
        self.last_accesed = time.time()
        self.clean_data()

    def clean_data(self):
        f = open(self.shared_file, "w")
        f.write("id,distance,angle\n")
        f.close()

    def get_data(self):
        self.last_accesed = time.time()
        return pd.read_csv(self.shared_file)

    def write_data(self, data):
        f = open(self.shared_file, "w")
        f.write("id,distance,angle\n")
        for elem in data:
            f.write("\"{}\",{},{}\n".format(elem.id, elem.distance, elem.angle))
        f.close()

    def has_new_data(self):
        return self.last_accesed < os.path.getmtime(self.shared_file)
