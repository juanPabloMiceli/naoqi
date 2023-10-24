import workspace.cli.parsers.awareness_parser as awareness_parser
import workspace.cli.parsers.leds_parser as leds_parser
import workspace.cli.parsers.debug_qrs_parser as debug_qrs_parser
import workspace.cli.parsers.start_camera_parser as start_camera_parser
import workspace.cli.parsers.look_at_parser as look_at_parser
import workspace.cli.parsers.move_parser as move_parser
import argparse

from workspace.properties.nao_properties import NaoProperties
from workspace.mock.nao_mock import NaoMock
from workspace.robot.nao_shared_memory import NaoSharedMemory
import threading
from workspace.maps.map import Map


def get_nao(shared_memory):
    if NaoProperties.testing():
        _map = Map('workspace/maps/square_map.json')
        nao = NaoMock(shared_memory, _map)
        if NaoProperties.simulation_on():
            from workspace.mock.simulation.nao_simulation import NaoSimulation
            NaoSimulation(nao, _map).start()
        return nao
    else:
        from workspace.robot.nao import Nao
        return Nao(shared_memory)

def add_subparsers(subparsers):
    subparsers = parser.add_subparsers(title='Available capabilities')

    awareness_parser.add_parser(subparsers)
    leds_parser.add_parser(subparsers)
    debug_qrs_parser.add_parser(subparsers)
    start_camera_parser.add_parser(subparsers)
    look_at_parser.add_parser(subparsers)
    move_parser.add_parser(subparsers)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A place with lots of simple NAO capabilities')
    add_subparsers(parser)
    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args, get_nao(NaoSharedMemory()))
    else:
        parser.print_help()
