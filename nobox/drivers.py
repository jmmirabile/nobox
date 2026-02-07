"""
Storage format drivers for NoBox

Provides pluggable serialization backends for different formats (JSON, YAML).
All drivers inherit from the base Driver class and implement load/save operations.
"""

import json
from pathlib import Path
from typing import Dict, Any
from abc import ABC, abstractmethod

try:
    import yaml
except ImportError:
    yaml = None  # YAML driver will check for this


class Driver(ABC):
    """Base driver interface for storage format implementations

    All drivers must implement:
    - extension: File extension (e.g., ".json", ".yaml")
    - app_name: App directory name (always "nobox")
    - format_subdir: Format subdirectory name (e.g., "json", "yaml")
    - load_collection: Load collection data from file
    - save_collection: Save collection data to file
    """

    @property
    @abstractmethod
    def extension(self) -> str:
        """File extension for this format (e.g., '.json')"""
        pass

    @property
    @abstractmethod
    def app_name(self) -> str:
        """App directory name (always 'nobox')"""
        pass

    @property
    @abstractmethod
    def format_subdir(self) -> str:
        """Format subdirectory name (e.g., 'json', 'yaml')"""
        pass

    @abstractmethod
    def load_collection(self, path: Path) -> Dict[str, Any]:
        """Load collection data from file

        Args:
            path: Path to collection file

        Returns:
            Dictionary mapping keys to record data

        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If file cannot be parsed
        """
        pass

    @abstractmethod
    def save_collection(self, path: Path, data: Dict[str, Any]) -> None:
        """Save collection data to file

        Args:
            path: Path to collection file
            data: Dictionary mapping keys to record data

        Raises:
            Exception: If file cannot be written
        """
        pass


class JSONDriver(Driver):
    """JSON format driver using Python's json module"""

    @property
    def extension(self) -> str:
        return ".json"

    @property
    def app_name(self) -> str:
        return "nobox"

    @property
    def format_subdir(self) -> str:
        return "json"

    def load_collection(self, path: Path) -> Dict[str, Any]:
        """Load collection from JSON file

        Args:
            path: Path to JSON file

        Returns:
            Dictionary with collection data

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        if not path.exists():
            return {}

        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_collection(self, path: Path, data: Dict[str, Any]) -> None:
        """Save collection to JSON file with pretty formatting

        Args:
            path: Path to JSON file
            data: Collection data to save
        """
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)


class YAMLDriver(Driver):
    """YAML format driver using PyYAML library"""

    def __init__(self):
        """Initialize YAML driver

        Raises:
            ImportError: If PyYAML is not installed
        """
        if yaml is None:
            raise ImportError(
                "PyYAML is required for YAML format support. "
                "Install it with: pip install PyYAML"
            )

    @property
    def extension(self) -> str:
        return ".yaml"

    @property
    def app_name(self) -> str:
        return "nobox"

    @property
    def format_subdir(self) -> str:
        return "yaml"

    def load_collection(self, path: Path) -> Dict[str, Any]:
        """Load collection from YAML file

        Args:
            path: Path to YAML file

        Returns:
            Dictionary with collection data

        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If file is not valid YAML
        """
        if not path.exists():
            return {}

        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            # safe_load returns None for empty files
            return data if data is not None else {}

    def save_collection(self, path: Path, data: Dict[str, Any]) -> None:
        """Save collection to YAML file with clean formatting

        Args:
            path: Path to YAML file
            data: Collection data to save
        """
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=True
            )
