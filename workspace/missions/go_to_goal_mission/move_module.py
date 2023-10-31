class MoveModule():
    def __init__(self, nao, goal_position, goal_direction_degrees):
        self.nao = nao
        self.goal_position = goal_position
        self.goal_direction_degrees = goal_direction_degrees
        self.controllables = ["go"]

    def go(self):
        self.nao.move_to(self.goal_position[0], self.goal_position[1], self.goal_direction_degrees)