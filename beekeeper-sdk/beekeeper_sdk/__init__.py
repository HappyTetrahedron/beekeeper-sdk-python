import os

rootdir = os.path.dirname(os.path.abspath(__file__))

# Read version from VERSION file
with open(os.path.join(rootdir, 'VERSION')) as version_file:
    __version__ = version_file.read().strip()

del os, rootdir, version_file

from .beekeeper_sdk import BeekeeperSDK
