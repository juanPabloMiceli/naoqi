from workspace.naoqi_custom.awareness_controller import AwarenessController
from workspace.naoqi_custom.head_controller import HeadController
from workspace.naoqi_custom.nao_properties import NaoProperties
from workspace.naoqi_custom.proxy_factory import ProxyFactory
import qi
import argparse

class PhotoController:

    def __init__(self, ip, port):
        self.proxy = ProxyFactory.get_proxy("ALPhotoCapture", ip, port)

    def save_picture(self, resolution, format, name):
        self.proxy.setResolution(resolution)
        self.proxy.setPictureFormat(format)
        self.proxy.takePictures(1, "/home/nao/pictures/", name)
        
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=str, required=True,
                        help="Name of the picture saved.")

    args = parser.parse_args()
    OUT = args.out
    IP, PORT = NaoProperties().get_connection_properties()

    session = qi.Session()
    session.connect("tcp://" + IP + ":" + str(PORT))
    
    AwarenessController(session).set(False)
    HeadController(session).look_at(0, 0)
    PhotoController(IP, PORT).save_picture(3, "jpg", OUT)



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
