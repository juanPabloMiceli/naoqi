import numpy as np
from multiprocessing import Value, Queue
from redis import Redis


class NaoSharedMemory:
    def __init__(self):

        # Location
        self.__x_position = Value('f', 0.0)
        self.__y_position = Value('f', 0.0)
        self.__direction = Value('f', 0.0)
        self.__nao_is_lost = Value('b', True)

        # Messages
        self.__event_queue = Queue()

        # Simulation Only
        self.__x_position_simulation = Value('f', 150.0)
        self.__y_position_simulation = Value('f', 150.0)
        self.__direction_simulation = Value('f', 45.0)

        # Red Ball Detection
        self.__distance_to_red_ball = Value('f', 0.0)
        self.__horizontal_degrees_to_red_ball = Value('f', 0.0)
        self.__vertical_degrees_to_red_ball = Value('f', 0.0)

        # Movement goals
        self.__current_goal_x = Value('f', -1000000.0)
        self.__current_goal_y = Value('f', -1000000.0)
        self.__current_goal_direction = Value('f', 0.0)

        # Actuators
        self.__brain_leds = Value('b', False)

        # out of module communication
        self.__redis_conn = Redis

    
    def set_brain_leds(self, new_value):
        with self.__brain_leds.get_lock():
            self.__brain_leds.value = new_value

    def get_brain_leds(self):
        return self.__brain_leds.value

    def set_position(self, new_position):
        with self.__x_position.get_lock():
            self.__x_position.value = new_position[0]
        with self.__y_position.get_lock():
            self.__y_position.value = new_position[1]

    def get_position(self):
        return np.array([self.__x_position.value, self.__y_position.value])

    def get_direction(self):
        return self.__direction.value

    def set_direction(self, new_direction):
        new_direction %= 360
        with self.__direction.get_lock():
            self.__direction.value = new_direction

    def set_position_simulation(self, new_position_simulation):
        with self.__x_position_simulation.get_lock():
            self.__x_position_simulation.value = new_position_simulation[0]
        with self.__y_position_simulation.get_lock():
            self.__y_position_simulation.value = new_position_simulation[1]

    def get_position_simulation(self):
        return np.array(
            [self.__x_position_simulation.value, self.__y_position_simulation.value]
        )

    def get_direction_simulation(self):
        return self.__direction_simulation.value

    def set_direction_simulation(self, new_direction_simulation):
        new_direction_simulation %= 360
        with self.__direction_simulation.get_lock():
            self.__direction_simulation.value = new_direction_simulation

    def set_nao_is_lost(self, new_value):
        with self.__nao_is_lost.get_lock():
            self.__nao_is_lost.value = new_value

    def get_nao_is_lost(self):
        return self.__nao_is_lost.value

    def set_current_goal_position(self, new_position):
        with self.__current_goal_x.get_lock():
            self.__current_goal_x.value = new_position[0]
        with self.__current_goal_y.get_lock():
            self.__current_goal_y.value = new_position[1]

    def get_current_goal_position(self):
        x = self.__current_goal_x.value
        y = self.__current_goal_y.value
        if x < 0 or y < 0:
            return None
        return np.array([x, y])

    def set_current_goal_direction(self, new_direction):
        new_direction %= 360
        with self.__current_goal_direction.get_lock():
            self.__current_goal_direction.value = new_direction

    def get_current_goal_direction(self):
        return self.__current_goal_direction.value

    def add_message(self, msg):
        self.__event_queue.put(msg)

    def get_message(self):
        return self.__event_queue.get()

    def messages_left(self):
        return self.__event_queue.qsize()

    def redis(self, command, *args):
        return getattr(self.__redis_conn, command)(*args)
    
    def set_new_ball(self, new_distance, new_horizontal_angle_degrees, new_vertical_angle_degrees):
        with self.__distance_to_red_ball.get_lock():
            self.__distance_to_red_ball.value = new_distance

        with self.__horizontal_degrees_to_red_ball.get_lock():
            self.__horizontal_degrees_to_red_ball.value = new_horizontal_angle_degrees

        with self.__vertical_degrees_to_red_ball.get_lock():
            self.__vertical_degrees_to_red_ball.value = new_vertical_angle_degrees

    def get_latest_ball_info(self):
        return (self.__distance_to_red_ball.value,
                self.__horizontal_degrees_to_red_ball.value,
                self.__vertical_degrees_to_red_ball.value)
