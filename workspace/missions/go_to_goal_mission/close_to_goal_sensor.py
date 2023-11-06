from workspace.utils import geometry


class CloseToGoalSensor():
    def __init__(self, nao, goal_position, target_direction):
        self.nao = nao
        self.goal_position = goal_position
        self.target_direction = target_direction

    def sense(self):
        nao_position = self.nao.get_position()
        nao_direction = self.nao.get_direction()
        if geometry.distance(nao_position, self.goal_position) > 20:
            return
        clockwise_distance = (self.target_direction - nao_direction + 360) % 360
        counterclockwise_distance = (nao_direction - self.target_direction + 360) % 360
        angle_to_target = min(clockwise_distance, counterclockwise_distance)
        if angle_to_target > 30:
            return
        self.nao.shared_memory.add_message("at")
