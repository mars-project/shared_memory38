from .shared_memory import *
try:
    from .managers import SharedMemoryManager
except ImportError:
    pass

from ._version import __version__
