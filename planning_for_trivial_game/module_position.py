import time

class ModulePosition():
    def __init__(self, memory):
        self.memory = memory
        self.controllables = ["up", "down", "left", "right"]

    def left(self):
        print("Moving left...")
        time.sleep(1)
        print("Moved left!")
        x, y = self.memory.get_player_position()
        self.memory.set_player_position([max(0, x - 1), y])

    def right(self):
        print("Moving right...")
        time.sleep(1)
        print("Moved right!")
        x, y = self.memory.get_player_position()
        grid_size = self.memory.get_grid_size()
        self.memory.set_player_position([min(grid_size - 1, x + 1), y])

    def up(self):
        print("Moving up...")
        time.sleep(1)
        print("Moved up!")
        x, y = self.memory.get_player_position()
        self.memory.set_player_position([x, max(0, y - 1)])

    def down(self):
        print("Moving down...")
        time.sleep(1)
        print("Moved down!")
        x, y = self.memory.get_player_position()
        grid_size = self.memory.get_grid_size()
        self.memory.set_player_position([x, min(grid_size - 1, y + 1)])
