import math
class SensingAngle():
    def __init__(self, memory):
        self.memory = memory
        self.max_error = 10.0

    def sense(self):
        angle = math.degrees(self.memory.get_angle_to_goal())
        if angle < 0:
            angle += 360.0
        if angle > 360.0:
            angle -= 360.0
        if 0.0 <=  angle <= self.max_error:
            self._push_queue("narrow_deviation_right")
        elif self.max_error < angle <= 180.0:
            self._push_queue("wide_deviation_right")
        elif 360.0 - self.max_error <= angle < 360.0:
            self._push_queue("narrow_deviation_left")
        elif 180.0 < angle < 360.0 - self.max_error:
            self._push_queue("wide_deviation_left")
        else:
            raise Exception(f"What? Angle is wrong {angle=}")

    def _push_queue(self, event):
        self.memory.event_queue.put(event)
