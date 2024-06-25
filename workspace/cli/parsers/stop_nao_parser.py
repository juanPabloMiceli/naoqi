
def stop_moving(args, nao):
    nao.stop_moving()

def add_parser(subparser):
    parser = subparser.add_parser("stop", help="Stop NAO movement")
    parser.set_defaults(func=stop_moving)
