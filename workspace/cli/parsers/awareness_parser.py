import qi

from workspace.naoqi_custom.nao_properties import NaoProperties
from workspace.naoqi_custom.awareness_controller import AwarenessController

if NaoProperties.testing():
    def set_awareness(new_awareness):
        print('[Dummy] Setting awareness to {}'.format(new_awareness))
else:
    def set_awareness(new_awareness):
        IP, PORT = NaoProperties().get_connection_properties()

        # Init session
        session = qi.Session()
        try:
            session.connect("tcp://" + IP + ":" + str(PORT))
        except RuntimeError:
            print ("Can't connect to Naoqi at ip \"" + IP + "\" on port " + str(PORT) +".\n"
                    "Please check your script arguments. Run with -h option for help.")
            sys.exit(1)
        AwarenessController(session).set(new_awareness)

def enable_awareness(args):
    set_awareness(True)

def disable_awareness(args):
    set_awareness(False)

def add_parser(subparser):
    parser = subparser.add_parser('awareness', help='Enable or disable NAOs awareness')
    awareness_subparsers = parser.add_subparsers(title='Available options')

    enable_parser = awareness_subparsers.add_parser('enable', help='Enable NAO awareness')
    enable_parser.set_defaults(func=enable_awareness)

    disable_parser = awareness_subparsers.add_parser('disable', help='disable NAO awareness')
    disable_parser.set_defaults(func=disable_awareness)
