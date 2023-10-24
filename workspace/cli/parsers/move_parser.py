import time

def walk_forward(args, nao):
    nao.walk_forward()
    time.sleep(args.seconds)
    nao.stop_moving()

def walk_backward(args, nao):
    nao.walk_backward()
    time.sleep(args.seconds)
    nao.stop_moving()

def rotate_clockwise(args, nao):
    nao.rotate_clockwise()
    time.sleep(args.seconds)
    nao.stop_moving()

def rotate_counter_clockwise(args, nao):
    nao.rotate_counter_clockwise()
    time.sleep(args.seconds)
    nao.stop_moving()

def add_parser(subparser):
    parser = subparser.add_parser('move', help='Make Nao move a few seconds')
    parser.add_argument('--seconds', type=float, default=5.0, help='Amount of seconds to move')
    move_subparsers = parser.add_subparsers(title='Direction')
    forward_parser = move_subparsers.add_parser('forward', help='Make NAO walk forward')
    forward_parser.set_defaults(func=walk_forward)
    backward_parser = move_subparsers.add_parser('backward', help='Make NAO walk backward')
    backward_parser.set_defaults(func=walk_backward)
    clockwise_parser = move_subparsers.add_parser('clockwise', help='Make NAO rotate clockwise')
    clockwise_parser.set_defaults(func=rotate_clockwise)
    counterclockwise_parser = move_subparsers.add_parser('counterclockwise', help='Make NAO rotate counterclockwise')
    counterclockwise_parser.set_defaults(func=rotate_counter_clockwise)
