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

repo_root = os.path.dirname(os.path.abspath(__file__))

tool_env = os.environ.copy()
tool_env["PYTHONPATH"] = os.path.join(repo_root, "tools") \
    + ":" + tool_env.get("PYTHONPATH", "")
shmem_source = "winshmem" if sys.platform == "win32" else "posixshmem"
subprocess.run([sys.executable, clinic_file, f"shared_memory/{shmem_source}.c"],
                env=tool_env)

posix_shm_mod = Extension(
    "shared_memory._posixshmem",
    define_macros=[
        ("HAVE_SHM_OPEN", "1"),
        ("HAVE_SHM_UNLINK", "1"),
        ("HAVE_SHM_MMAN_H", "1"),
    ],
    libraries=["rt"] if sys.platform == 'linux' else [],
    sources=["shared_memory/posixshmem.c"],
)
win_shm_mod = Extension(
    "shared_memory._winshmem",
    sources=["shared_memory/winshmem.c"],
)

def execfile(fname, globs, locs=None):
    locs = locs or globs
    exec(compile(open(fname).read(), fname, "exec"), globs, locs)

version_file_path = os.path.join(repo_root, "shared_memory", "_version.py")
version_ns = {"__file__": version_file_path}
execfile(version_file_path, version_ns)
version = version_ns["__version__"]

setup(
    name="shared_memory38",
    version=version,
    author="Wenjun Si",
    author_email="swj0066@gmail.com",
    description="Backport of multiprocessing.shared_memory in Python 3.8",
    long_description=open(os.path.join(repo_root, "README.rst"),
                          encoding="utf-8").read(),
    long_description_content_type="text/x-rst",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries",
    ],
    url="https://github.com/mars-project/shared_memory38",
    packages=find_packages(exclude=("*.tests.*", "*.tests")),
    ext_modules=[posix_shm_mod] if sys.platform != "win32" \
        else [win_shm_mod],
)
