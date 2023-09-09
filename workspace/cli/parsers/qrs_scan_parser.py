import time
import cv2


from workspace.naoqi_custom.nao_properties import NaoProperties
from workspace.naoqi_custom.video_controller import VideoController

if NaoProperties.testing():
    def scan_qrs(args):
        print('[Dummy] Oh yes, much QRs. Many fun!')
else:
    from workspace.utils.qr_decoder import QrDecoder
    def scan_qrs(args):
        IP, PORT = NaoProperties().get_connection_properties()
        video_controller = VideoController(IP, PORT)
        qr_decoder = QrDecoder.Instance()
        while True:
            print('Taking picture')
            start = time.time()
            gray_image = video_controller.get_raw_gray_image()
            end = time.time()
            take_picture_time = end - start

            print('Decoding QRs')
            start = time.time()
            cv2_image = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)
            decoded_qrs = qr_decoder.decode(cv2_image)
            cv2.imwrite('gray_image.png', cv2_image)
            end = time.time()
            decode_time = end - start

            print('QRs decoded, I found {} of them.\n'.format(len(decoded_qrs)))
            for decoded_qr in decoded_qrs:
                print(decoded_qr)
                print('\n\n')

            print('Time to take the picture: {} seconds'.format(take_picture_time))
            print('Time to decode the QRs: {} seconds'.format(decode_time))
            #time.sleep(2)



def add_parser(subparser):
    parser = subparser.add_parser('qrs-scan', help='Scan QRs live and print its information')
    parser.set_defaults(func=scan_qrs)
