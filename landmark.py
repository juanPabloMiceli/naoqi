# This test degrees(alpha) how to use the ALLandMarkDetection module.
# - We first instantiate a proxy to the ALLandMarkDetection module
#     Note that this module should be loaded on the robot's NAOqi.
#     The module output its results in ALMemory in a variable
#     called "LandmarkDetected"
# - We then read this AlMemory value and check whether we get
#   interesting things.
import time
from naoqi import ALProxy
import qi
import sys
from os.path import exists
import math
import argparse


def disable_basic_awareness(session):
    ba_service = session.service("ALBasicAwareness")
    ba_service.stopAwareness()

def look_front():
    motion_service  = session.service("ALMotion")
    motion_service.setStiffnesses("Head", 1.0) 

    names            = "HeadYaw"
    angles           = 0
    fractionMaxSpeed = 0.1
    motion_service.setAngles(names,angles,fractionMaxSpeed)
    time.sleep(1.0)
    names            = "HeadPitch"
    motion_service.setAngles(names,angles,fractionMaxSpeed)
    time.sleep(1.0)
# A un metro el nao puede detectar landmarks de 19.8cm de diametro en un cono de +-25 grados. (Ojo que 25 le cuesta)
def look_semi_right():
    motion_service  = session.service("ALMotion")
    motion_service.setStiffnesses("Head", 1.0) 

    names            = "HeadYaw"
    angles           = -math.radians(45)
    fractionMaxSpeed = 0.1
    motion_service.setAngles(names,angles,fractionMaxSpeed)
    time.sleep(1.0)
    names            = "HeadPitch"
    angles           = 0
    motion_service.setAngles(names,angles,fractionMaxSpeed)
    time.sleep(1.0)

def get_side_mult(side_str):
    if side_str == "left":
        mult = 1
    elif side_str == "right":
        mult = -1
    else:
        print("side_str must be either \"left\" or \"right\"")
        exit(1)
    return mult

def look_at(angle, side_str):
    side_mult = get_side_mult(side_str)
    motion_service  = session.service("ALMotion")
    motion_service.setStiffnesses("Head", 1.0) 

    names            = "HeadYaw"
    angles           = side_mult * math.radians(angle)
    fractionMaxSpeed = 0.1
    motion_service.setAngles(names,angles,fractionMaxSpeed)
    time.sleep(1.0)
    names            = "HeadPitch"
    angles           = 0
    motion_service.setAngles(names,angles,fractionMaxSpeed)
    time.sleep(1.0)

def get_proxy(proxyName, ip, port):
    try:
        proxy = ALProxy(proxyName, ip, port)
    except Exception as e:
        print("Error when creating "+proxyName+" proxy:")
        print(str(e))
        exit(1)
    return proxy

class ReadingData:
    
    def __init__(self, ID, landmark_shape_info, args):
        self.ID = ID
        self.alpha = landmark_shape_info[1]
        self.alphaD = math.degrees(self.alpha)
        self.beta = landmark_shape_info[2]
        self.betaD = math.degrees(self.beta)
        self.width = landmark_shape_info[3]
        self.widthD = math.degrees(self.width)
        self.height = landmark_shape_info[4]
        self.heightD = math.degrees(self.height)
        self.landmark_diameter = args.landmark_diameter
        self.actual_distance = args.actual_distance
        self.torso_orientation = args.torso_orientation
        self.measured_distance = self.landmark_diameter / (2 * math.tan(self.height / 2))

    def __str__(self):
        return "ID: {}, alpha: {}, alphaD: {}, beta: {}, betaD: {}, width: {}, widthD: {}, height: {}, heightD: {}, landmark_diameter: {}, actual_distance: {}, measured_distance: {}, torso_orientation: {}".format(self.ID, self.alpha, self.alphaD, self.beta, self.betaD, self.width, self.widthD, self.height, self.heightD, self.landmark_diameter, self.actual_distance, self.measured_distance, self.torso_orientation)
    
    def csvString(self):
        return "{},{},{},{},{},{},{},{},{},{},{},{},{}".format(self.ID, self.alpha, self.alphaD, self.beta, self.betaD, self.width, self.widthD, self.height, self.heightD, self.landmark_diameter, self.actual_distance, self.measured_distance, self.torso_orientation)


def main(session, args):

    # Stop basic awareness so that nao doesn't move his head when not commanded 
    disable_basic_awareness(session)

    # Look at some angle for finding the landmark
    look_at(0, "right")

    # Create a proxy to ALLandMarkDetection
    landMarkProxy = get_proxy("ALLandMarkDetection", args.ip, args.port)

    # Subscribe to the ALLandMarkDetection proxy
    # This means that the module will write in ALMemory with
    # the given period below
    period = 500
    landMarkProxy.subscribe("Test_LandMark", period, 0.0 )

    # ALMemory variable where the ALLandMarkdetection module
    # outputs its results
    memKey = "LandmarkDetected"

    # Create a proxy to ALMemory
    memoryProxy = get_proxy("ALMemory", args.ip, args.port)

    # A simple loop that reads the memKey and checks
    # whether landmarks are detected.
    currentReadings = []
    totalTries = 0
    while True or (totalTries < (args.measurings * 3) and len(currentReadings) < args.measurings):
        time.sleep(0.5)
        val = memoryProxy.getData(memKey, 0)
        # Check whether we got a valid output: a list with two fields.
        if(val and isinstance(val, list) and len(val) >= 2):
            # We detected landmarks !
            # Second Field = array of Mark_Info's.
            markInfoArray = val[1]
            print("val: ")
            print(val)

            try:
                # Browse the markInfoArray to get info on each detected mark.
                for markInfo in markInfoArray:
                    # First Field = Shape info.
                    markShapeInfo = markInfo[0]
                    markID = markInfo[1][0]
                    readingData = ReadingData(markID, markShapeInfo, args)
                    currentReadings.append(readingData)

                    # Print Mark information.
                    print(readingData)
            except Exception as e:
                print("Landmarks detected, but it seems getData is invalid. ALValue =")
                print(val)
                print("Error msg %s" % (str(e)))
        else:
            print("Error with getData. ALValue = %s" % (str(val)))
        totalTries = totalTries + 1

    # Unsubscribe from the module.
    landMarkProxy.unsubscribe("Test_LandMark")
    if len(currentReadings) < args.measurings:
        print("Measuring goal could not be achieved ({} of {})".format(len(currentReadings), args.measurings))
        exit(1)
    print("Readings finished successfully")
    
    if not args.out == "":
        print("Writing to csv...")
        f = open(args.out, "a")
        for reading in currentReadings:
            f.write(reading.csvString()+"\n")
        f.close()
            

def check_args(args):
    if args.out == "":
        return
    if not exists(args.out):
        print("Please provide an existent csv with the following columns:\n"+
              "ID,alpha,alphaD,beta,betaD,width,widthD,height,heightD,landmark_diameter,actual_distance,measured_distance,torso_orientation")
        exit(1)
    if (args.landmark_diameter == 0.0):
        print("If you want to write into a file, please provide --landmark_diameter")
        exit(1)
    if(args.landmark_diameter < 0.0):
        print("--landmark_diameter must be greater than 0")
        exit(1)
    if (args.actual_distance == 0.0):
        print("If you want to write into a file, please provide --actual_distance")
        exit(1)
    if(args.actual_distance < 0.0):
        print("--actual_distance must be greater than 0")
        exit(1)
    if (args.torso_orientation not in ["TL", "SL", "F", "SR", "TR"]):
        print("If you want to write into a file, please provide one of the following --torso_orientation (TL, SL, F, SR, TR)")
        exit(1)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--out", type=str, default="",
                        help="Output file for throwing the readings, if not passed no file will be created")
    parser.add_argument("--landmark_diameter", type=float, default=0.0,
                        help="Landmark diameter (cm) for throwing at the csv and calculating the distance, not required if --out not especified")
    parser.add_argument("--actual_distance", type=float, default=0.0,
                        help="Distance to the landmark (cm) for throwing at the csv, not required if --out not especified")
    parser.add_argument("--torso_orientation", type=str, default="",
                        help="Orientation of the torso respect to the landmark for throwing at the csv, not required if --out not especified.\n"+
                             "Please use: TL, SL, F, SR, TR. (total left, semi left, front, semi right, total right)")
    parser.add_argument("--measurings", type=int, default=10,
                        help="Total measurings for throwing at the csv, default is 10.\n"+
                             "If goal can not be achieved, csv is not written.")

    args = parser.parse_args()

    # Check there is nothing invalid in the arguments received
    check_args(args)

    # Init session
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
                "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session, args)

# Sample cmd
# python landmark.py --ip=192.168.0.171 --port=9559 --out=data.csv --landmark_diameter=19.8 --actual_distance=30 --torso_orientation=F