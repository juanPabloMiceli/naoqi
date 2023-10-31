import numpy as np

def move_to(args, nao):
    nao.new_goal(np.array([args.target_x, args.target_y]), args.target_angle_degrees)
    nao.move_to_goal()
    while True:
        pass

def add_parser(subparser):
    parser = subparser.add_parser('advanced_movement', help='Make Nao move more complex ways')
    advanced_movement_subparsers = parser.add_subparsers(title='Command')

    move_to_parser = advanced_movement_subparsers.add_parser('move_to', help='Move NAO to target an leave it pointing to the target angle in degrees')
    move_to_parser.add_argument('target_x', type=float)
    move_to_parser.add_argument('target_y', type=float)
    move_to_parser.add_argument('target_angle_degrees', type=float)
    move_to_parser.set_defaults(func=move_to)