import os
import sys
import subprocess
from setuptools import setup, find_packages, Extension

if sys.version_info[:2] == (3, 6):
    clinic_file = "tools/py36_clinic.py"
elif sys.version_info[:2] == (3, 7):
    clinic_file = "tools/py37_clinic.py"
else:
    raise ValueError("Must run on Python 3.6 or 3.7")

if sys.platform != 'win32':
    tool_env = os.environ.copy()
    tool_env['PYTHONPATH'] = f'{os.getcwd()}/tools:' + tool_env.get('PYTHONPATH', '')
    subprocess.run([sys.executable, clinic_file, "shared_memory/posixshmem.c"], 
                   env=tool_env)

posix_shm_mod = Extension(
    "shared_memory._posixshmem",
    define_macros=[
        ("HAVE_SHM_OPEN", "1"),
        ("HAVE_SHM_UNLINK", "1"),
        ("HAVE_SHM_MMAN_H", 1),
    ],
    libraries=["rt"] if sys.platform == 'linux' else [],
    sources=["shared_memory/posixshmem.c"],
)

setup(
    name="shared_memory38",
    version="0.1.0",
    description="Backport of multiprocessing.shared_memory in Python 3.8",
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries',
    ],
    url="https://github.com/mars-project/shared_memory38",
    packages=find_packages(exclude=('*.tests.*', '*.tests')),
    ext_modules=[posix_shm_mod] if sys.platform != 'win32' else [],
)
