def debug_balls_detection(args, nao):
    nao.debug_red_ball_detection()

def add_parser(subparser):
    parser = subparser.add_parser('debug-redballs', help='Detect red balls live and print its information')
    parser.set_defaults(func=debug_balls_detection)
