import math

class SensingPosition():
    def __init__(self, memory, goal_radius):
        self.memory = memory
        self.goal_radius = goal_radius
        self._last_given_signal = ""
        self.FAR = "far"
        self.CLOSE = "close"

    def sense(self):
        if self.distance_to_goal() > self.goal_radius:
            if self._last_given_signal != self.FAR:
                self.memory.event_queue.put(self.FAR)
                self._last_given_signal = self.FAR
        else:
            if self._last_given_signal != self.CLOSE:
                self.memory.event_queue.put(self.CLOSE)
                self._last_given_signal = self.CLOSE
                self.memory.advance_goal()

    def distance_to_goal(self):
        player_x, player_y = self.memory.get_player_position()
        goal_x, goal_y = self.memory.get_goal_position()
        return math.sqrt(
                math.pow(player_x - goal_x, 2) +
                math.pow(player_y - goal_y, 2))
