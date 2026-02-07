"""
NoBox - JSON and YAML key-value storage utilities

Part of the Box Suite - a modular Python CLI application framework.

NoBox provides simple command-line interfaces for managing flexible,
schema-less data storage in JSON and YAML formats.
"""

__version__ = "0.1.0"
__author__ = "Jeff Mirabile"
__license__ = "MIT"

from .store import DictStore
from .drivers import Driver, JSONDriver, YAMLDriver

__all__ = ["DictStore", "Driver", "JSONDriver", "YAMLDriver"]
