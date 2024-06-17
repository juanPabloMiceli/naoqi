def say(args, nao):
    nao.say(args.text)

def add_parser(subparser):
    parser = subparser.add_parser('say', help='Make Nao say something')
    parser.add_argument('text', type = str, help = 'What you want Nao to say')
    disable_parser.set_defaults(func=say)
