"""
DictStore - CRUD operations for NoBox collections

Handles all create, read, update, delete operations on collections.
Uses a pluggable Driver for serialization (JSON, YAML, etc.).
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from confbox import get_app_data_dir
from .drivers import Driver


class DictStore:
    """Key-value storage with CRUD operations

    Stores collections of records as nested dictionaries:
    - Database = directory
    - Collection = file (users.json, products.yaml, etc.)
    - Record = key → dict mapping

    Example structure:
        ~/.local/share/nobox/
        └── json/
            └── mydb/
                └── users.json  → {"alice": {"name": "Alice", "age": 30}}

    Args:
        db_name: Name of the database (directory)
        driver: Storage format driver (JSONDriver, YAMLDriver, etc.)
    """

    def __init__(self, db_name: str, driver: Driver):
        """Initialize DictStore

        Args:
            db_name: Database name (becomes a directory)
            driver: Format driver for serialization
        """
        self.db_name = db_name
        self.driver = driver

        # Get base nobox directory via ConfBox
        base_dir = get_app_data_dir(driver.app_name)

        # Add format subdirectory (json/ or yaml/)
        self.db_dir = base_dir / driver.format_subdir / db_name

    def _get_collection_path(self, collection: str) -> Path:
        """Get path to collection file

        Args:
            collection: Collection name

        Returns:
            Path to collection file
        """
        return self.db_dir / f"{collection}{self.driver.extension}"

    def _load_collection(self, collection: str) -> Dict[str, Any]:
        """Load collection data from file

        Args:
            collection: Collection name

        Returns:
            Dictionary of records (empty dict if collection doesn't exist)
        """
        path = self._get_collection_path(collection)
        return self.driver.load_collection(path)

    def _save_collection(self, collection: str, data: Dict[str, Any]) -> None:
        """Save collection data to file

        Args:
            collection: Collection name
            data: Collection data to save
        """
        path = self._get_collection_path(collection)
        self.driver.save_collection(path, data)

    # Removed: _normalize_key() - NoBox is case-sensitive to follow JSON/YAML specs
    # Keys are stored exactly as provided to ensure data portability and spec compliance

    def set(self, collection: str, key: str, data: Dict[str, Any]) -> None:
        """Create or update a record

        If the record exists, new fields are merged with existing data.
        Existing fields are updated with new values.

        Args:
            collection: Collection name
            key: Record key (case-sensitive)
            data: Record data (dictionary) - merged with existing record

        Example:
            store.set("users", "Alice", {"name": "Alice", "age": 30})
            # Creates: {"name": "Alice", "age": 30}

            store.set("users", "Alice", {"age": 31, "city": "NYC"})
            # Updates: {"name": "Alice", "age": 31, "city": "NYC"}
        """
        collection_data = self._load_collection(collection)

        # Merge with existing record if it exists
        if key in collection_data and isinstance(collection_data[key], dict) and isinstance(data, dict):
            collection_data[key].update(data)
        else:
            collection_data[key] = data

        self._save_collection(collection, collection_data)

    def get(self, collection: str, key: str) -> Optional[Dict[str, Any]]:
        """Get a specific record

        Args:
            collection: Collection name
            key: Record key (case-sensitive)

        Returns:
            Record data or None if not found

        Example:
            user = store.get("users", "Alice")  # Must match exact case
            # Returns: {"name": "Alice", "age": 30}
        """
        collection_data = self._load_collection(collection)
        return collection_data.get(key)

    def delete(self, collection: str, key: str) -> bool:
        """Delete a record

        Args:
            collection: Collection name
            key: Record key (case-sensitive)

        Returns:
            True if record was deleted, False if it didn't exist

        Example:
            deleted = store.delete("users", "Alice")  # Must match exact case
        """
        collection_data = self._load_collection(collection)

        if key in collection_data:
            del collection_data[key]
            self._save_collection(collection, collection_data)
            return True

        return False

    def keys(self, collection: str) -> List[str]:
        """List all record keys in a collection

        Args:
            collection: Collection name

        Returns:
            List of record keys (sorted)

        Example:
            keys = store.keys("users")
            # Returns: ["alice", "bob", "charlie"]
        """
        collection_data = self._load_collection(collection)
        return sorted(collection_data.keys())

    def all(self, collection: str) -> Dict[str, Any]:
        """Get all records in a collection

        Args:
            collection: Collection name

        Returns:
            Dictionary mapping keys to record data

        Example:
            all_users = store.all("users")
            # Returns: {"alice": {...}, "bob": {...}}
        """
        return self._load_collection(collection)

    def exists(self, collection: str, key: str) -> bool:
        """Check if a record exists

        Args:
            collection: Collection name
            key: Record key (case-sensitive)

        Returns:
            True if record exists, False otherwise

        Example:
            if store.exists("users", "Alice"):  # Must match exact case
                print("Alice exists!")
        """
        collection_data = self._load_collection(collection)
        return key in collection_data

    def count(self, collection: str) -> int:
        """Count records in a collection

        Args:
            collection: Collection name

        Returns:
            Number of records

        Example:
            num_users = store.count("users")
        """
        collection_data = self._load_collection(collection)
        return len(collection_data)

    def list_collections(self) -> List[str]:
        """List all collections in this database

        Returns:
            List of collection names (sorted)

        Example:
            collections = store.list_collections()
            # Returns: ["products", "users"]
        """
        if not self.db_dir.exists():
            return []

        collections = []
        for path in self.db_dir.iterdir():
            if path.is_file() and path.suffix == self.driver.extension:
                collections.append(path.stem)

        return sorted(collections)

    def collection_exists(self, collection: str) -> bool:
        """Check if a collection exists

        Args:
            collection: Collection name

        Returns:
            True if collection file exists, False otherwise
        """
        path = self._get_collection_path(collection)
        return path.exists()

    def delete_collection(self, collection: str) -> bool:
        """Delete an entire collection

        Args:
            collection: Collection name

        Returns:
            True if collection was deleted, False if it didn't exist

        Example:
            deleted = store.delete_collection("old_users")
        """
        path = self._get_collection_path(collection)

        if path.exists():
            path.unlink()
            return True

        return False

    @classmethod
    def list_databases(cls, driver: Driver) -> List[str]:
        """List all databases for this format

        Args:
            driver: Storage format driver

        Returns:
            List of database names (sorted)

        Example:
            databases = DictStore.list_databases(JSONDriver())
            # Returns: ["contacts", "inventory", "mydb"]
        """
        from confbox import get_app_data_dir

        # Get base nobox directory via ConfBox
        base_dir = get_app_data_dir(driver.app_name)
        format_dir = base_dir / driver.format_subdir

        if not format_dir.exists():
            return []

        databases = []
        for path in format_dir.iterdir():
            if path.is_dir():
                databases.append(path.name)

        return sorted(databases)
