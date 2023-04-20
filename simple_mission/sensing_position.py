from ..geometry import distance

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
                self.memory.add_message(self.FAR)
                self._last_given_signal = self.FAR
        else:
            if self._last_given_signal != self.CLOSE:
                self.memory.add_message(self.CLOSE)
                self._last_given_signal = self.CLOSE

    def distance_to_goal(self):
        return geometry.distance(
                self.memory.get_nao_position(),
                self.memory.get_goal_position()
                )
