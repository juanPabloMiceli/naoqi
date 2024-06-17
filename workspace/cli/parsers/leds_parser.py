from workspace.naoqi_custom.leds_controller import LedsController
import time

def turn_leds_on(args, nao):
    nao.leds_controller.on()

def turn_leds_off(args, nao):
    nao.leds_controller.off()

def blink_leds(args, nao):
    while True:
        nao.leds_controller.on()
        time.sleep(1)
        nao.leds_controller.off()
        time.sleep(1)

def add_parser(subparser):
    parser = subparser.add_parser('leds', help='Play with NAO leds')
    leds_subparsers = parser.add_subparsers(title='Led actions')
    on_parser = leds_subparsers.add_parser('on', help='Turn head leds on')
    on_parser.set_defaults(func=turn_leds_on)
    off_parser = leds_subparsers.add_parser('off', help='Turn head leds off')
    off_parser.set_defaults(func=turn_leds_off)
    blink_parser = leds_subparsers.add_parser('blink', help='Make head leds blink')
    blink_parser.set_defaults(func=blink_leds)
