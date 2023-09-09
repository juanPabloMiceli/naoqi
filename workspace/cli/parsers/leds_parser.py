import time

from workspace.naoqi_custom.nao_properties import NaoProperties
from workspace.naoqi_custom.leds_controller import LedsController

ON_INSTRUCTION = 'on'
OFF_INSTRUCTION = 'off'
BLINK_INSTRUCTION = 'blink'

if NaoProperties.testing():
    def switch_leds(instruction):
        print('[Dummy] Leds instruction: {}'.format(instruction))
else:
    def switch_leds(instruction):
        IP, PORT = NaoProperties().get_connection_properties()
        leds_controller = LedsController(IP, PORT)

        if instruction == ON_INSTRUCTION:
            leds_controller.on()
            return
        if instruction == OFF_INSTRUCTION:
            leds_controller.off()
            return
        if instruction == BLINK_INSTRUCTION:
            while True:
                leds_controller.on()
                time.sleep(1)
                leds_controller.off()
                time.sleep(1)
            return
        print('Unknown instruction')

def turn_leds_on(args):
    switch_leds(ON_INSTRUCTION)

def turn_leds_off(args):
    switch_leds(OFF_INSTRUCTION)

def blink_leds(args):
    switch_leds(BLINK_INSTRUCTION)

def add_parser(subparser):
    parser = subparser.add_parser('leds', help='Play with NAO leds')
    leds_subparsers = parser.add_subparsers(title='Led actions')
    on_parser = leds_subparsers.add_parser('on', help='Turn head leds on')
    on_parser.set_defaults(func=turn_leds_on)
    off_parser = leds_subparsers.add_parser('off', help='Turn head leds off')
    off_parser.set_defaults(func=turn_leds_off)
    blink_parser = leds_subparsers.add_parser('blink', help='Make head leds blink')
    blink_parser.set_defaults(func=blink_leds)
