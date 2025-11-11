import time
from threading import Thread

class MovingModule():
    def __init__(self, nao):
        self.nao = nao
        self.controllables = ["move"]

    def move(self):
        self.nao.stop_moving()
        self.nao.walk_forward()
        Thread(target=self.end_move_after_time).start()

    def end_move_after_time(self):
        time.sleep(0.5)
        self.nao.shared_memory.add_message("move_end")
