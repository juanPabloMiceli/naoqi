class PosturesModule:
    def __init__(self, nao):
        self.nao = nao
        self.controllables = ["sit", "lay", "stand"]

    def sit(self):
        self.nao.sit()

    def lay(self):
        self.nao.lay()

    def stand(self):
        self.nao.stand()
