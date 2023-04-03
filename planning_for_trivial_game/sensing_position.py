class SensingPosition():
    def __init__(self, memory):
        self.memory = memory

    def sense(self):
        x, y = self.memory.get_player_position()
        self.memory.event_queue.put(f"{x}{y}")
