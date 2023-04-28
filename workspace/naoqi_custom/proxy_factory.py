from naoqi import ALProxy


class ProxyFactory:

    """
    Creates proxies used to interact with the NAO API
    """

    @staticmethod
    def get_proxy(proxyName, ip, port):
        # type: (str, str, int) -> ALProxy
        """
        Creates a NAO proxy object with the given name using the given connection info.

        Parameters
        ----------
        proxyName : str
            Proxy object requested
        ip : str
            IP of the NAO
        port : str
            Port of the NAO

        Returns
        -------
        proxy : ALProxy
            The requested proxy object used to interact with the NAO API
        """
        try:
            proxy = ALProxy(proxyName, ip, port)
        except Exception as e:
            print("Error when creating " + proxyName + " proxy:")
            print(str(e))
            exit(1)
        return proxy
