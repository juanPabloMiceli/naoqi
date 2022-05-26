from head_control import look_at
import qi
import argparse

from disableAwareness import disable_basic_awareness
from naoqi import ALProxy

IP = "192.168.0.171"
PORT = 9559

def save_picture(proxy, resolution, format, name):
    proxy.setResolution(resolution)
    proxy.setPictureFormat(format)
    proxy.takePictures(1, "/home/nao/pictures/", name)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=str, required=True,
                        help="Name of the picture saved.")

    args = parser.parse_args()

    session = qi.Session()
    session.connect("tcp://" + IP + ":" + str(PORT))

    try:
        disable_basic_awareness(session)
        look_at(session, 0, "left")
        photoCaptureProxy = ALProxy("ALPhotoCapture", IP, PORT)
    except Exception as e:
        print("Error when creating ALPhotoCapture proxy")
        print(str(e))
        exit(1)

    save_picture(photoCaptureProxy, 3, "jpg", args.out)



''' Resolution table
|   8   |  40x30px  |
---------------------
|   7   |  80x60px  |
---------------------
|   0   | 160x120px |
---------------------
|   1   | 320x240px |
---------------------
|   2   | 640x480px |
---------------------
|   3   |1280x960px |
'''