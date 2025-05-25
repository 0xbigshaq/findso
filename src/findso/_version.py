"""Version management for the findso package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("findso")
except PackageNotFoundError:
    # package is not installed
    __version__ = "unknown"
