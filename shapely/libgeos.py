from ctypes import CDLL, DEFAULT_MODE
from ctypes.util import find_library
import glob
import logging
import sys


logger = logging.getLogger(__name__)


def load_geos():
    bundled_path = get_bundled_path()
    if bundled_path:
        return load_library(libpath)
    elif os.environ.get("CONDA_PREFIX"):
        libpath = get_conda_library_path()
        return load_library(libpath)
    elif hasattr(sys, "frozen"):
        pass  # TODO
    else:
        libpath, fallbacks = get_default_locations()
        return load_library(libpath, fallbacks)


def load_library(libname, fallbacks=None, mode=DEFAULT_MODE):
    lib = None
    libpaths = []

    if sys.platform == "win32":
        IMPORT_EXCEPTIONS = (ImportError, OSError, WindowsError)
    else:
        IMPORT_EXCEPTIONS = (ImportError, OSError,)

    libpath = find_library(libname)
    if libpath:
        libpaths.append(libpath)
    if fallbacks:
        libpaths.extend(fallbacks)

    for libpath in libpaths:
        log.debug("Trying `CDLL({})`".format(libpath))
        try:
            lib = CDLL(libpath, mode=mode)
        except IMPORT_EXCEPTIONS:
            log.debug("Failed `CDLL({})`".format(libpath))

    if not lib:
        raise OSError("Could not find lib {} or any of it's variants {}".format(libname, fallbacks or []))

    log.debug("Success `CDLL({})`".format(libpath))

    return lib


def get_conda_library_path():
    if sys.platform == "linux":
        return os.path.join(sys.prefix, "lib", "libgeos_c.so")
    elif sys.platform == "darwin":
        return os.path.join(sys.prefix, "lib", "libgeos_c.dylib")
    elif sys.platform == "win32":
        return os.path.join(sys.prefix, "Library", "bin", "geos_c.dll")


def get_bundled_path():
    if sys.platform == "linux":
        return glob_find(".libs/libgeos_c-*.so.*")
    elif sys.platform == "darwin":
        return glob_find(".dylibs/libgeos_c.dylib")
    elif sys.platform == "win32":
        return glob_find("DLLs")  # TODO; need to add this to PATH


def get_default_locations():
    if sys.platform == "linux":
        libpath = "geos_c"
        fallbacks = [
            "libgeos_c.so.1",
            "libgeos_c.so",
        ]
    elif sys.platform == "darwin":
        libpath = "geos_c"
        fallbacks = [
            # The Framework build from Kyng Chaos
            "/Library/Frameworks/GEOS.framework/Versions/Current/GEOS",
            # macports
            "/opt/local/lib/libgeos_c.dylib",
        ]
    elif sys.platform == "win32":
        libpath = "geos_c.dll"
        fallbacks = []
    else:
        # assume linux-like
        libpath = "geos_c"
        fallbacks = [
            "libgeos_c.so.1",
            "libgeos_c.so",
        ]

    return libpath, fallbacks


def glob_find(pattern):
    folder = os.path.dirname(__file__)
    full_pattern = os.path.abspath(os.path.join(folder, pattern))
    paths = glob.glob(full_pattern)
    if paths:
        return paths[0]
    return None
