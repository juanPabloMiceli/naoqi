import time
import qi
from workspace.naoqi_custom.nao_properties import NaoProperties
from workspace.naoqi_custom.awareness_controller import AwarenessController
from workspace.naoqi_custom.head_controller import HeadController
from workspace.naoqi_custom.video_controller import VideoController

if NaoProperties.testing():
    def start_camera(args):
        print('[Dummy] Camera started :)'.format(args.out))
else:
    def start_camera(args):
        IP, PORT = NaoProperties().get_connection_properties()
        session = qi.Session()
        session.connect("tcp://" + IP + ":" + str(PORT))
        AwarenessController(session).set(False)
        HeadController(session).look_at(0, 0)
        video_controller = VideoController(IP, PORT)
        last_10_times = []

        while True:
            print('Retrieving frame')
            start = time.time()
            nao_image = video_controller.get_raw_gray_image()
            print(nao_image.shape)
            end = time.time()
            last_10_times.append(end - start)
            last_10_times = last_10_times[-10:]
            mean = sum(last_10_times) / len(last_10_times)
            print('Frame took: {:.4f} seconds. Average FPS: {:.2f}'.format(last_10_times[-1], 1/mean))


def add_parser(subparser):
    parser = subparser.add_parser('start-camera', help='Starts camera and loggs time to get each frame')
    parser.set_defaults(func=start_camera)
