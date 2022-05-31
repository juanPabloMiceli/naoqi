import ConfigParser

class NaoProperties:
    properties_file = "connection.properties"
    nao_section = "NaoSection"
    
    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read(self.properties_file)
    
    def get_ip(self):
        return self.config.get(self.nao_section, "nao.ip")

    def get_port(self):
        return int(self.config.get(self.nao_section, "nao.port"))

    def get_connection_properties(self):
        '''
        Returns a tuple (str: ip, int: port)
        '''
        return self.get_ip(), self.get_port() 

if __name__ == "__main__":
    print("nao properties: {}".format(NaoProperties().get_connection_properties()))