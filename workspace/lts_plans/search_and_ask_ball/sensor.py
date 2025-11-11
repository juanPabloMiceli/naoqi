import abc

class Sensor(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, nao):
        self.nao = nao
        self._enabled = False

    def enable(self):
        if not self._enabled:
            self._enabled = True
            self.on_enable()

    def disable(self):
        if self._enabled:
            self._enabled = False
            self.on_disable()

    def on_enable(self):
        """Optional hook for subclasses."""
        pass

    def on_disable(self):
        """Optional hook for subclasses."""
        pass

    def sense(self):
        """Template method controlling enable/disable behavior."""
        if not self._enabled:
            return False

        should_disable = self._sense_impl()
        if should_disable:
            self.disable()

    @abc.abstractmethod
    def _sense_impl(self):
        """Override this method with the sensor logic in subclasses."""
        raise NotImplementedError

