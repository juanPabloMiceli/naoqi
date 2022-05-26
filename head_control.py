import qi
import math
import time

def get_side_mult(side_str):
    if side_str == "left":
        mult = 1
    elif side_str == "right":
        mult = -1
    else:
        print("side_str must be either \"left\" or \"right\"")
        exit(1)
    return mult

def look_at(session, angle, side_str):
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