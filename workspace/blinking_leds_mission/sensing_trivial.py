import time

class SensingTrivial():
    def __init__(self, memory):
        self.memory = memory
        self.last_event = time.time()

    def sense(self):
        now = time.time()
        if now - self.last_event >= 1:
            self.last_event = now
            self.memory.add_message("event")
