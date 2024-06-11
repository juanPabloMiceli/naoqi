from workspace.maps.map import Map
from workspace.mock.nao_mock import NaoMock
from workspace.properties.nao_properties import NaoProperties
from workspace.naoqi_custom.red_ball_detection_module import RedBallDetectionModule


class NaoFactory:
    @staticmethod
    def create(shared_memory):
        _map = Map('workspace/maps/square_map.json')

        if NaoProperties.testing():
            nao = NaoMock(shared_memory, _map)
        else:
            from workspace.robot.nao import Nao
            nao = Nao(shared_memory, _map)

        simulation = None
        if NaoProperties.simulation_on():
            from workspace.mock.simulation.nao_simulation import NaoSimulation
            simulation = NaoSimulation(nao, _map)
            simulation.start()

        return nao, simulation
