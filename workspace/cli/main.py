import workspace.cli.parsers.awareness_parser as awareness_parser
import workspace.cli.parsers.leds_parser as leds_parser
import workspace.cli.parsers.debug_qrs_parser as debug_qrs_parser
import workspace.cli.parsers.start_camera_parser as start_camera_parser
import workspace.cli.parsers.look_at_parser as look_at_parser
import workspace.cli.parsers.move_parser as move_parser
import workspace.cli.parsers.advanced_movement_parser as advanced_movement_parser
import workspace.cli.parsers.tts_parser as tts_parser
import workspace.cli.parsers.debug_red_ball_detection_parser as debug_red_ball_detection_parser
import argparse

from workspace.properties.nao_properties import NaoProperties
from workspace.robot.nao_shared_memory import NaoSharedMemory
from workspace.utils.nao_factory import NaoFactory

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
    debug_red_ball_detection_parser.add_parser(subparsers)

def add_redball_module_to_nao(nao, simulation):
    """
    This has to be made in the main module, because this only works if redBallModule is a variable in the main scope.
    i.e. It can't be RedBallDetectionModule.redBallModule.
    (If this doesn't work, move redBallModule declaration outside add_redball_module_to_nao().)
    """
    if not NaoProperties.testing():
        from workspace.naoqi_custom.red_ball_detection_module import RedBallDetectionModule
        redBallModule = RedBallDetectionModule("redBallModule", nao)
        nao.nao_memory.subscribeToEvent('redBallDetected', 'redBallModule', 'red_ball_detected')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A place with lots of simple NAO capabilities')
    add_subparsers(parser)
    args = parser.parse_args()

    if hasattr(args, 'func'):
        nao, simulation = NaoFactory.create(NaoSharedMemory())
        add_redball_module_to_nao(nao, simulation)
        args.func(args, nao)
    else:
        parser.print_help()
