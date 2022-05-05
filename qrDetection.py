
import qi
import argparse
import sys
import time
from naoqi import ALProxy

def main(session, args):
    """
    This is just an example script that shows how images can be accessed
    through ALVideoDevice in Python.
    Nothing interesting is done with the images in this example.
    """
    # Get the services ALBarcodeReader and ALMemory.

    barcode_service = session.service("ALBarcodeReader")
    memory_service = session.service("ALMemory")

    barcode_service.setResolution(3)


    barcode_service.subscribe("test_barcode")

    # Query last data from ALMemory twenty times
    while True:
        data = memory_service.getData("BarcodeReader/BarcodeDetected")
        if len(data) > 0:
            
            print("data: " + str(data[0][0]))
            print("positions: " + str(data[0][1]))
        else:
            print("data: []")
        # print("position: " + str(data[0][1]))
        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session, args)

# Sample cmd
# python qrDetection.py --ip=192.168.0.171 --port=9559

# [
#     [
#         'Array', 
#         [[63.0, 56.0], [63.0, 84.0], [91.0, 83.0], [91.0, 56.0]]
#     ]
# ]