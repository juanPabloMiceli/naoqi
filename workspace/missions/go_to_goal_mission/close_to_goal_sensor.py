from workspace.utils import geometry


class CloseToGoalSensor():
    def __init__(self, nao, goals_positions, goals_directions):
        self.nao = nao
        self.goals_positions = goals_positions
        self.goals_directions = goals_directions
        self.current_goal = 0
        self.already_arrived = False

    def sense(self):
        nao_position = self.nao.get_position()
        nao_direction = self.nao.get_direction()
        goal_position, target_direction = self.nao.get_goal()
        if geometry.distance(nao_position, goal_position) > 20:
            self.already_arrived = False
            return
        clockwise_distance = (target_direction - nao_direction + 360) % 360
        counterclockwise_distance = (nao_direction - target_direction + 360) % 360
        angle_to_target = min(clockwise_distance, counterclockwise_distance)
        if angle_to_target > 30:
            self.already_arrived = False
            return

        if self.already_arrived:        
            return
        
        self.nao.shared_memory.add_message("at")
        self.already_arrived = True
        self.current_goal = (self.current_goal + 1) % len(self.goals_positions) 
        self.nao.new_goal(self.goals_positions[self.current_goal], self.goals_directions[self.current_goal])
