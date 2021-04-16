#
# Definition of SharedMemoryManager and SharedMemoryServer
#
import os
import signal
from multiprocessing import ProcessError, util
from multiprocessing.managers import BaseManager, Server, State, dispatch
from os import getpid
try:
    from . import shared_memory
    HAS_SHMEM = True
except ImportError:
    HAS_SHMEM = False


__all__ = ['SharedMemoryManager']


if HAS_SHMEM:
    class _SharedMemoryTracker:
        "Manages one or more shared memory segments."

        def __init__(self, name, segment_names=[]):
            self.shared_memory_context_name = name
            self.segment_names = segment_names

        def register_segment(self, segment_name):
            "Adds the supplied shared memory block name to tracker."
            util.debug(f"Register segment {segment_name!r} in pid {getpid()}")
            self.segment_names.append(segment_name)

        def destroy_segment(self, segment_name):
            """Calls unlink() on the shared memory block with the supplied name
            and removes it from the list of blocks being tracked."""
            util.debug(f"Destroy segment {segment_name!r} in pid {getpid()}")
            self.segment_names.remove(segment_name)
            segment = shared_memory.SharedMemory(segment_name)
            segment.close()
            segment.unlink()

        def unlink(self):
            "Calls destroy_segment() on all tracked shared memory blocks."
            for segment_name in self.segment_names[:]:
                self.destroy_segment(segment_name)

        def __del__(self):
            util.debug(f"Call {self.__class__.__name__}.__del__ in {getpid()}")
            self.unlink()

        def __getstate__(self):
            return (self.shared_memory_context_name, self.segment_names)

        def __setstate__(self, state):
            self.__init__(*state)


    class SharedMemoryServer(Server):

        public = Server.public + \
                 ['track_segment', 'release_segment', 'list_segments']

        def __init__(self, *args, **kwargs):
            Server.__init__(self, *args, **kwargs)
            address = self.address
            # The address of Linux abstract namespaces can be bytes
            if isinstance(address, bytes):
                address = os.fsdecode(address)
            self.shared_memory_context = \
                _SharedMemoryTracker(f"shm_{address}_{getpid()}")
            util.debug(f"SharedMemoryServer started by pid {getpid()}")

        def create(*args, **kwargs):
            """Create a new distributed-shared object (not backed by a shared
            memory block) and return its id to be used in a Proxy Object."""
            # Unless set up as a shared proxy, don't make shared_memory_context
            # a standard part of kwargs.  This makes things easier for supplying
            # simple functions.
            if len(args) >= 3:
                typeod = args[2]
            elif 'typeid' in kwargs:
                typeid = kwargs['typeid']
            elif not args:
                raise TypeError("descriptor 'create' of 'SharedMemoryServer' "
                                "object needs an argument")
            else:
                raise TypeError('create expected at least 2 positional '
                                'arguments, got %d' % (len(args)-1))
            if hasattr(self.registry[typeid][-1], "_shared_memory_proxy"):
                kwargs['shared_memory_context'] = self.shared_memory_context
            return Server.create(*args, **kwargs)
        create.__text_signature__ = '($self, c, typeid, /, *args, **kwargs)'

        def shutdown(self, c):
            "Call unlink() on all tracked shared memory, terminate the Server."
            self.shared_memory_context.unlink()
            return Server.shutdown(self, c)

        def track_segment(self, c, segment_name):
            "Adds the supplied shared memory block name to Server's tracker."
            self.shared_memory_context.register_segment(segment_name)

        def release_segment(self, c, segment_name):
            """Calls unlink() on the shared memory block with the supplied name
            and removes it from the tracker instance inside the Server."""
            self.shared_memory_context.destroy_segment(segment_name)

        def list_segments(self, c):
            """Returns a list of names of shared memory blocks that the Server
            is currently tracking."""
            return self.shared_memory_context.segment_names


    class SharedMemoryManager(BaseManager):
        """Like SyncManager but uses SharedMemoryServer instead of Server.
        It provides methods for creating and returning SharedMemory instances
        and for creating a list-like object (ShareableList) backed by shared
        memory.  It also provides methods that create and return Proxy Objects
        that support synchronization across processes (i.e. multi-process-safe
        locks and semaphores).
        """

        _Server = SharedMemoryServer

        def __init__(self, *args, **kwargs):
            if os.name == "posix":
                # bpo-36867: Ensure the resource_tracker is running before
                # launching the manager process, so that concurrent
                # shared_memory manipulation both in the manager and in the
                # current process does not create two resource_tracker
                # processes.
                from . import resource_tracker
                resource_tracker.ensure_running()
            BaseManager.__init__(self, *args, **kwargs)
            util.debug(f"{self.__class__.__name__} created by pid {getpid()}")

        def __del__(self):
            util.debug(f"{self.__class__.__name__}.__del__ by pid {getpid()}")
            pass

        def get_server(self):
            'Better than monkeypatching for now; merge into Server ultimately'
            if self._state.value != State.INITIAL:
                if self._state.value == State.STARTED:
                    raise ProcessError("Already started SharedMemoryServer")
                elif self._state.value == State.SHUTDOWN:
                    raise ProcessError("SharedMemoryManager has shut down")
                else:
                    raise ProcessError(
                        "Unknown state {!r}".format(self._state.value))
            return self._Server(self._registry, self._address,
                                self._authkey, self._serializer)

        @classmethod
        def _run_server(cls, *args, **kwargs):
            # as server protection not implemented in Python < 3.8, we have to
            # add it manually via this measure
            # bpo-36368: protect server process from KeyboardInterrupt signals
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            super()._run_server(*args, **kwargs)

        def SharedMemory(self, size):
            """Returns a new SharedMemory instance with the specified size in
            bytes, to be tracked by the manager."""
            with self._Client(self._address, authkey=self._authkey) as conn:
                sms = shared_memory.SharedMemory(None, create=True, size=size)
                try:
                    dispatch(conn, None, 'track_segment', (sms.name,))
                except BaseException as e:
                    sms.unlink()
                    raise e
            return sms

        def ShareableList(self, sequence):
            """Returns a new ShareableList instance populated with the values
            from the input sequence, to be tracked by the manager."""
            with self._Client(self._address, authkey=self._authkey) as conn:
                sl = shared_memory.ShareableList(sequence)
                try:
                    dispatch(conn, None, 'track_segment', (sl.shm.name,))
                except BaseException as e:
                    sl.shm.unlink()
                    raise e
            return sl
