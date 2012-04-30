import abc

# Field positions for introspection overrides:
TOP = 'TOP'
BOTTOM = 'BOTTOM'
AFTER = 'AFTER'
BEFORE = 'BEFORE'

class Introspector(metaclass=abc.ABCMeta):
    """Base class for all introspectors"""

    def __init__(self, source):
        self.source = source

    @abc.abstractmethod
    def get_fields(self):
        pass
