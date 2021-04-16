from .shared_memory import *
try:
    from .managers import SharedMemoryManager
except ImportError:
    pass

__version__ = '0.1.0'
