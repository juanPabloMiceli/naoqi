# naoqi

## Setup

Run `build.sh` under the repo root to build the NAO execution environment. The synthesized controller and the NAO connection is run under this environment.

Run `run.sh` under the repo root to open a docker container on which to run the initializer command. An example of the initializer command would be:
`python -m workspace/missions/blinking_leds_mission/blinking_leds_mission.py`

## Developing Environment

All code under the `workspace` directory must be compatible with the NAO execution environment (python 2.7). External modules are the exception.

## External Modules

### Setup

All external modules (under `workspace/external_modules`) have their own `build.sh` and `run.sh`. These work as the main naoqi module, except the `run.sh` script also initialize the module.

### Developing environment

External modules are not restricted to python 2.7 and can be developed with any version. To be compatible they must be able to use the existing redis connection or to add a communication method to the NAO execution environment. 