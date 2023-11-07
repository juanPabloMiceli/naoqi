class MoveModule():
    def __init__(self, nao):
        self.nao = nao
        self.controllables = ['go']

    def go(self):
        self.nao.move_to_goal()