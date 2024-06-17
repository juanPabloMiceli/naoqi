from threading import Thread
import time

class WaitModule():
    def __init__(self, nao):
        self.nao = nao
        self.controllables = ["start_wait"]

    def start_wait(self):
        Thread(target=self.wait).start()

    def wait(self):
        time.sleep(5)
        self.nao.shared_memory.add_message("end_wait")
