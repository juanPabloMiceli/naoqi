from naoqi import ALProxy

class ProxyFactory:

    @staticmethod
    def get_proxy(proxyName, ip, port):
        try:
            proxy = ALProxy(proxyName, ip, port)
        except Exception as e:
            print("Error when creating "+proxyName+" proxy:")
            print(str(e))
            exit(1)
        return proxy
