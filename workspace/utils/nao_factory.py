from workspace.maps.map import Map
from workspace.mock.nao_mock import NaoMock
from workspace.properties.nao_properties import NaoProperties


class NaoFactory:
    
    @staticmethod
    def create(shared_memory):
        if NaoProperties.testing():
            _map = Map('workspace/maps/square_map.json')
            nao = NaoMock(shared_memory, _map)
            simulation = None
            if NaoProperties.simulation_on():
                from workspace.mock.simulation.nao_simulation import NaoSimulation
                simulation = NaoSimulation(nao, _map)
                simulation.start()
            return nao, simulation
        else:
            from workspace.robot.nao import Nao
            return Nao(shared_memory), None