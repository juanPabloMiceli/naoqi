from workspace.utils.geometry import distance
from workspace.utils.logger_factory import LoggerFactory

class SensingPosition():
    def __init__(self, memory, goal_radius):
        self.LOGGER = LoggerFactory.get_logger("SENSING_POSITION")
        self.memory = memory
        self.goal_radius = goal_radius
        self._last_given_signal = ""
        self.FAR = "far"
        self.CLOSE = "close"

    def sense(self):
        distance = self.distance_to_goal()
        if distance > self.goal_radius:
            if self._last_given_signal != self.FAR:
                self.memory.add_message(self.FAR)
                self._last_given_signal = self.FAR
        else:
            if self._last_given_signal != self.CLOSE:
                self.memory.add_message(self.CLOSE)
                self._last_given_signal = self.CLOSE

    def distance_to_goal(self):
        return distance(
                self.memory.get_nao_position(),
                self.memory.get_goal_position()
                )
