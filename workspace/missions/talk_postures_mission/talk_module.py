class TalkModule:
    def __init__(self, nao):
        self.nao = nao
        self.controllables = ["start_talk"]

    def start_talk(self):
        self.nao.start_talk()

    def end_talk(self):
        self.nao.end_talk()
