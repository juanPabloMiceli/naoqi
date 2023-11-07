class GoCommandSensor():
    def __init__(self, nao, simulation):
        self.nao = nao
        self.simulation = simulation
        self.simulation.add_button((0, 160, 0), (0, 50, 0), [500, 100, 100, 50], lambda: self.nao.shared_memory.add_message("go_command"))

    def sense(self):
        pass