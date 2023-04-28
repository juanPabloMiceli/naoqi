import ConfigParser


class NaoProperties:
    """
    An accesor class for NAO information
    """

    # path to the file where configuration info is stored
    properties_file = "workspace/connection.properties"

    # infortmation tag of the connection file
    nao_section = "NaoSection"

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read(self.properties_file)

    def get_ip(self):
        # type: () -> str
        """
        Gathers the IP of the NAO on the configuration file

        Returns
        -------
        nap.ip: str
            The IP of the NAO on the configuration file
        """
        return self.config.get(self.nao_section, "nao.ip")

    def get_port(self):
        # type: () -> int
        """
        Gathers the port of the NAO on the configuration file

        Returns
        -------
        nap.port: int
            The port of the NAO on the configuration file
        """
        return int(self.config.get(self.nao_section, "nao.port"))

    def get_connection_properties(self):
        # type: () -> tuple[str, int]
        """
        Gathers all conenction propiertes from the configuration file

        Returns
        -------
        IP, PORT: tuple of string and int
            The connection information
        """
        return self.get_ip(), self.get_port()


if __name__ == "__main__":
    print("nao properties: {}".format(NaoProperties().get_connection_properties()))
