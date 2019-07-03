import sys
from warnings import warn

if sys.version_info < (3, 5):
    warn("proxyget is designed for python 3.6 or later but you are running {}"
         .format('.'.join(map(str, sys.version_info[:3]))))
del sys, warn

# main file

# noinspection PyUnresolvedReferences
from .proxyget import *  # __all__ defines what is imported

__author__ = "FHT Mitchell"
__version__ = "0.3.0"
__date__ = "2018-12-05"
