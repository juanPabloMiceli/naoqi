def enable_awareness(args, nao):
    nao.set_awareness(True)

def disable_awareness(args, nao):
    nao.set_awareness(False)

def add_parser(subparser):
    parser = subparser.add_parser('awareness', help='Enable or disable NAOs awareness')
    awareness_subparsers = parser.add_subparsers(title='Available options')

    enable_parser = awareness_subparsers.add_parser('enable', help='Enable NAO awareness')
    enable_parser.set_defaults(func=enable_awareness)

    disable_parser = awareness_subparsers.add_parser('disable', help='disable NAO awareness')
    disable_parser.set_defaults(func=disable_awareness)
