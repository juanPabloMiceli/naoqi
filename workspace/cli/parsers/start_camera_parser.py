import time

def start_camera(args, nao):
    nao.set_awareness(False)

    last_10_times = []
    while True:
        start = time.time()
        nao.get_frame()
        end = time.time()
        last_10_times.append(end - start)
        last_10_times = last_10_times[-10:]
        mean = sum(last_10_times) / len(last_10_times)
        print('Frame took: {:.4f} seconds. Average FPS: {:.2f}'.format(last_10_times[-1], 1/mean))

def add_parser(subparser):
    parser = subparser.add_parser('start-camera', help='Starts camera and loggs time to get each frame')
    parser.set_defaults(func=start_camera)
