import _winapi
import ctypes.wintypes
from ctypes import c_ulong, byref, sizeof

SIZE_T = c_ulong

INVALID_HANDLE_VALUE = ctypes.wintypes.HANDLE(-1)

PAGE_READWRITE = 0x04

FILE_MAP_COPY = 1
FILE_MAP_WRITE = 2
FILE_MAP_READ = 4


_CreateFileMapping = ctypes.windll.kernel32.CreateFileMappingW
_CreateFileMapping.argtypes = [
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.LPVOID,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.LPWSTR,
]
_CreateFileMapping.restype = ctypes.wintypes.HANDLE


def CreateFileMapping(hFile, lpFileMappingAttributes, flProtect,
                      dwMaximumSizeHigh, dwMaximumSizeLow, lpName):
    handle = _CreateFileMapping(hFile, lpFileMappingAttributes, flProtect,
                                dwMaximumSizeHigh, dwMaximumSizeLow, lpName)
    if handle is None:
        last_err = _winapi.GetLastError()
        raise OSError(last_err)
    return handle


_OpenFileMapping = ctypes.windll.kernel32.OpenFileMappingW
_OpenFileMapping.argtypes = [
    ctypes.wintypes.DWORD,
    ctypes.wintypes.BOOL,
    ctypes.wintypes.LPWSTR
]
_OpenFileMapping.restype = ctypes.wintypes.HANDLE


def OpenFileMapping(dwDesiredAccess, hInheritedHandle, lpName):
    handle = _OpenFileMapping(dwDesiredAccess, hInheritedHandle, lpName)
    if handle is None:
        last_err = _winapi.GetLastError()
        if last_err == 2:
            raise FileNotFoundError
        else:
            raise OSError(last_err)
    return handle


_MapViewOfFile = ctypes.windll.kernel32.MapViewOfFile
_MapViewOfFile.argtypes = [
   ctypes.wintypes.HANDLE,
   ctypes.wintypes.DWORD,
   ctypes.wintypes.DWORD,
   ctypes.wintypes.DWORD,
   SIZE_T
]
_MapViewOfFile.restype = ctypes.wintypes.LPVOID


def MapViewOfFile(hFileMappingObject, dwDesiredAccess, dwFileOffsetHigh,
                  dwFileOffsetLow, dwNumberOfBytesToMap):
    ptr = _MapViewOfFile(hFileMappingObject, dwDesiredAccess, dwFileOffsetHigh,
                         dwFileOffsetLow, dwNumberOfBytesToMap)
    if ptr is None:
        last_err = _winapi.GetLastError()
        raise OSError(last_err)
    return ptr


class MEMORY_BASIC_INFORMATION32(ctypes.Structure):
    """
    MEMORY_BASIC_INFORMATION contains information about a
    particular region of memory. A call to kernel32.VirtualQuery()
    populates this structure
    """
    _fields_ = [
        ("BaseAddress", ctypes.wintypes.LPVOID),
        ("AllocationBase", ctypes.wintypes.LPVOID),
        ("AllocationProtect", ctypes.wintypes.DWORD),
        ("RegionSize", ctypes.wintypes.DWORD),
        ("State", ctypes.wintypes.DWORD),
        ("Protect", ctypes.wintypes.DWORD),
        ("Type", ctypes.wintypes.DWORD),
    ]


class MEMORY_BASIC_INFORMATION64(ctypes.Structure):
    """
    MEMORY_BASIC_INFORMATION contains information about a
    particular region of memory. A call to kernel32.VirtualQuery()
    populates this structure
    """
    _fields_ = [
        ("BaseAddress", ctypes.wintypes.LPVOID),
        ("AllocationBase", ctypes.wintypes.LPVOID),
        ("AllocationProtect", ctypes.wintypes.DWORD),
        ("__alignment1", ctypes.wintypes.DWORD),
        ("RegionSize", ctypes.wintypes.DWORD),
        ("State", ctypes.wintypes.DWORD),
        ("Protect", ctypes.wintypes.DWORD),
        ("Type", ctypes.wintypes.DWORD),
        ("__alignment2", ctypes.wintypes.DWORD),
    ]


MEMORY_BASIC_INFORMATION = MEMORY_BASIC_INFORMATION64 if sizeof(ctypes.c_void_p) == 8 \
    else MEMORY_BASIC_INFORMATION32


VirtualQuery = ctypes.windll.kernel32.VirtualQuery
VirtualQuery.argtypes = [
    ctypes.wintypes.LPCVOID,
    ctypes.POINTER(MEMORY_BASIC_INFORMATION),
    SIZE_T
]
VirtualQuery.restype = SIZE_T


def VirtualQuerySize(address):
    mbi = MEMORY_BASIC_INFORMATION()
    ret_size = VirtualQuery(address, byref(mbi), sizeof(mbi))
    assert ret_size == sizeof(mbi)
    return mbi.RegionSize
