import ConfigParser

class NaoProperties:
    environment_section = 'Environment'
    connection_section = 'Connection'
    misc_config_section = 'MiscConfiguration'
    simulation_section = 'Simulation'
    config = ConfigParser.RawConfigParser()
    config.read('workspace/nao.properties')

    @classmethod
    def testing(cls):
        robot_mode = cls.config.get(cls.environment_section, "robot_mode")
        if robot_mode == 'mock':
            return True
        if robot_mode == 'robot':
            return False
        print('\'{}\' is not a valid robot mode. Valid modes: {{mock, robot}}'.format(robot_mode))
        exit(1)
    
    @classmethod
    def simulation_on(cls):
        return bool(cls.config.getboolean(cls.environment_section, "simulation"))
        

    @classmethod
    def get_ip(cls):
        return cls.config.get(cls.connection_section, "ip")

    @classmethod
    def get_port(cls):
        return cls.config.getint(cls.connection_section, "port")
    
    @classmethod
    def get_connection_properties(cls):
        '''
        Returns a tuple (str: ip, int: port)
        '''
        return cls.get_ip(), cls.get_port()
    
    @classmethod
    def simulation_fps(cls):
        return cls.config.getfloat(cls.simulation_section, 'frames_per_second')
    
    @classmethod
    def forward_speed(cls):
        return cls.config.getfloat(cls.simulation_section, 'forward_centimeters_per_second') / cls.simulation_fps()

    @classmethod
    def backward_speed(cls):
        return cls.config.getfloat(cls.simulation_section, 'backward_centimeters_per_second') / cls.simulation_fps()

    @classmethod
    def rotation_speed(cls):
        return cls.config.getfloat(cls.simulation_section, 'rotation_degrees_per_second') / cls.simulation_fps()

    @classmethod
    def qr_detection_angle(cls):
        return cls.config.getfloat(cls.simulation_section, 'qr_detection_angle_degrees')
    
    @classmethod
    def qr_max_distance(cls):
        return cls.config.getint(cls.simulation_section, 'qr_maximum_detection_distance_centimeters')

    @classmethod
    def qr_min_distance(cls):
        return cls.config.getint(cls.simulation_section, 'qr_minimum_detection_distance_centimeters')
    
    @classmethod
    def nao_fps(cls):
        return cls.config.getfloat(cls.simulation_section, 'nao_frames_per_second')

    @classmethod
    def balls_diameter(cls):
        return cls.config.getfloat(cls.misc_config_section, 'red_balls_diameter')

    @classmethod
    def seen_ball_time_of_grace(cls):
        return cls.config.getfloat(cls.misc_config_section, "seen_ball_time_of_grace_seconds")
