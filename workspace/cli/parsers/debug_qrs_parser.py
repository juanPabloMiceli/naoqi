def debug_qrs(args, nao):
    nao.debug_qrs()

def add_parser(subparser):
    parser = subparser.add_parser('debug-qrs', help='Scan QRs live and print its information')
    parser.set_defaults(func=debug_qrs)
