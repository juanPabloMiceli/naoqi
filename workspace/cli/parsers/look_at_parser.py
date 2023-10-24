def look_at(args, nao):
    nao.look_at(args.x, args.y)

def add_parser(subparser):
    parser = subparser.add_parser('look-at', help='Set NAOs X and Y head angles.')
    parser.add_argument('--x', type=float, default=0.0,
                        help="Angle in degrees for moving the nao's head left to right. Range: [-119.5, 119.5]")
    parser.add_argument('--y', type=float, default=0.0,
                        help="Angle in degrees for moving the nao's head bottom to top. Range: [-29.5, 38.5]")
    parser.set_defaults(func=look_at)
