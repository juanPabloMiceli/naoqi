import workspace.cli.parsers.awareness_parser as awareness_parser
import workspace.cli.parsers.leds_parser as leds_parser
import workspace.cli.parsers.debug_qrs_parser as debug_qrs_parser
import workspace.cli.parsers.start_camera_parser as start_camera_parser
import workspace.cli.parsers.look_at_parser as look_at_parser
import workspace.cli.parsers.move_parser as move_parser
import workspace.cli.parsers.advanced_movement_parser as advanced_movement_parser
import workspace.cli.parsers.tts_parser as tts_parser
import argparse

from workspace.naoqi_custom.red_ball_detection_module import RedBallDetectionModule
from workspace.robot.nao_shared_memory import NaoSharedMemory
from workspace.utils.nao_factory import NaoFactory
from workspace.properties.nao_properties import NaoProperties


def add_subparsers(subparsers):
    subparsers = parser.add_subparsers(title='Available capabilities')

    awareness_parser.add_parser(subparsers)
    leds_parser.add_parser(subparsers)
    debug_qrs_parser.add_parser(subparsers)
    start_camera_parser.add_parser(subparsers)
    look_at_parser.add_parser(subparsers)
    move_parser.add_parser(subparsers)
    advanced_movement_parser.add_parser(subparsers)
    tts_parser.add_parser(subparsers)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A place with lots of simple NAO capabilities')
    add_subparsers(parser)
    args = parser.parse_args()

    if hasattr(args, 'func'):
        nao, simulation = NaoFactory.create(NaoSharedMemory())
        if not simulation:
            redBallModule = RedBallDetectionModule('redBallModule', nao)
            nao.nao_memory.subscribeToEvent('redBallDetected', 'redBallModule', 'red_ball_detected')
        args.func(args, nao)
    else:
        parser.print_help()
