import ConfigParser

class NaoProperties:
    properties_file = "workspace/connection.properties"
    connection_section = "Connection"
    environment_section = "Environment"
    config = ConfigParser.RawConfigParser()
    config.read(properties_file)
    
    @classmethod
    def get_ip(cls):
        return cls.config.get(cls.connection_section, "ip")

    @classmethod
    def get_port(cls):
        return int(cls.config.get(cls.connection_section, "port"))

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
    def get_connection_properties(cls):
        '''
        Returns a tuple (str: ip, int: port)
        '''
        return cls.get_ip(), cls.get_port() 
