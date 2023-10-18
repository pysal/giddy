"""
:mod:`giddy` --- Spatial Dynamics and Mobility
==============================================

"""

import contextlib
from importlib.metadata import PackageNotFoundError, version

from . import directional, ergodic, markov, mobility, rank, sequence, util

with contextlib.suppress(PackageNotFoundError):
    __version__ = version("giddy")
