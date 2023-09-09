import workspace.cli.parsers.awareness_parser as awareness_parser
import workspace.cli.parsers.leds_parser as leds_parser
import workspace.cli.parsers.qrs_scan_parser as qrs_scan_parser
import workspace.cli.parsers.start_camera_parser as start_camera_parser
import argparse

parser = argparse.ArgumentParser(description='A place with lots of simple NAO capabilities')
subparsers = parser.add_subparsers(title='Available capabilities')



awareness_parser.add_parser(subparsers)
leds_parser.add_parser(subparsers)
qrs_scan_parser.add_parser(subparsers)
start_camera_parser.add_parser(subparsers)

args = parser.parse_args()

if hasattr(args, 'func'):
    args.func(args)
else:
    parser.print_help()
