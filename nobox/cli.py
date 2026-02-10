#!/usr/bin/env python3
"""
NoBox CLI - Command-line interface for key-value storage

Provides commands for CRUD operations on collections:
- set: Create/update records
- get: Retrieve specific records
- del: Delete records
- keys: List all record keys
- all: Show all records

Part of the Box Suite - a modular Python CLI utility framework.
"""

import argparse
import sys
import json
from typing import Dict, Any, List
from .store import DictStore
from .drivers import Driver


class CLI:
    """Command-line interface for NoBox

    Handles argument parsing and command execution.
    Uses a DictStore instance for all operations.

    Args:
        driver: Storage format driver (JSONDriver or YAMLDriver)
    """

    def __init__(self, driver: Driver):
        """Initialize CLI with a driver

        Args:
            driver: Format driver for serialization
        """
        self.driver = driver
        self.format_name = driver.format_subdir.upper()  # "JSON" or "YAML"

    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser

        Returns:
            Configured ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            description=f"NoBox - {self.format_name} key-value storage utility (Part of the Box Suite)",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=f"""
Examples:
  # List all databases
  {{cmd}} --list
  {{cmd}} databases

  # List collections in a database
  {{cmd}} mydb --list
  {{cmd}} mydb collections

  # Set a record with key:value pairs
  {{cmd}} mydb users set alice name:Alice age:30 email:alice@example.com

  # Get a specific record
  {{cmd}} mydb users get alice

  # List all keys
  {{cmd}} mydb users keys

  # Show all records
  {{cmd}} mydb users all

  # Delete a record
  {{cmd}} mydb users del alice

  # Delete a collection (table)
  {{cmd}} mydb users --delete

  # Delete entire database
  {{cmd}} mydb --delete

  # Import from stdin
  cat data.txt | {{cmd}} mydb users --import
  cat data.txt | {{cmd}} mydb users -i

  Import format (one record per line):
    Standard:  key field:value field:value ...
               ↑   ↑           ↑
               |   |           Space-separated (NOT comma-separated)
               |   field:value pairs
               Record key (required, first item on line)

    Example file (data.txt):
      alice name:Alice email:alice@example.com age:30
      bob name:Bob department:engineering salary:75000
      charlie name:Charlie role:manager team:sales

    Notes:
      • One record per line
      • Key is the first word (required)
      • Fields are space-separated (use quotes for spaces in values)
      • Numbers auto-convert (age:30 becomes integer 30)
      • Empty lines and # comments are skipped

Storage location (via ConfBox):
  Linux: ~/.local/share/nobox/{self.driver.format_subdir}/
  macOS: ~/Library/Application Support/nobox/{self.driver.format_subdir}/
  Windows: %APPDATA%\\nobox\\{self.driver.format_subdir}\\
""".format(cmd="jb" if self.format_name == "JSON" else "yb")
        )

        parser.add_argument("database", nargs="?", help="Database name")
        parser.add_argument("collection", nargs="?", help="Collection name")
        parser.add_argument(
            "command",
            nargs="?",
            choices=["set", "get", "del", "keys", "all", "databases", "collections"],
            help="Command to execute"
        )
        parser.add_argument(
            "args",
            nargs="*",
            help="Command arguments (key for get/del, key field:value... for set)"
        )

        # List flag
        parser.add_argument(
            "-l", "--list",
            action="store_true",
            help="List databases (no args) or collections (with database)"
        )

        # Import flag
        parser.add_argument(
            "-i", "--import",
            dest="import_flag",
            action="store_true",
            help="Import records from stdin (requires database and collection)"
        )

        # Delete flag
        parser.add_argument(
            "-d", "--delete",
            dest="delete_flag",
            action="store_true",
            help="Delete database (with database only) or collection (with database and collection)"
        )

        # Output format options
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output as JSON (or import from JSON)"
        )
        parser.add_argument(
            "--jsonl",
            action="store_true",
            help="Output as JSON Lines (one object per line)"
        )
        parser.add_argument(
            "--oneline",
            action="store_true",
            help="Output as one-line format (key field:value ...)"
        )
        parser.add_argument(
            "--csv",
            action="store_true",
            help="Output as CSV"
        )

        return parser

    def parse_key_values(self, args: List[str]) -> Dict[str, Any]:
        """Parse key:value pairs from command line arguments

        Args:
            args: List of key:value strings

        Returns:
            Dictionary mapping keys to values

        Example:
            parse_key_values(["name:Alice", "age:30"])
            # Returns: {"name": "Alice", "age": 30}
        """
        data = {}

        for arg in args:
            if ':' not in arg:
                raise ValueError(
                    f"Invalid format '{arg}'. Use 'field:value' format."
                )

            key, value = arg.split(':', 1)

            # Try to convert to int
            try:
                value = int(value)
            except ValueError:
                # Try to convert to float
                try:
                    value = float(value)
                except ValueError:
                    # Keep as string
                    pass

            data[key] = value

        return data

    def format_table(self, records: Dict[str, Any]) -> str:
        """Format records as a pretty table

        Args:
            records: Dictionary of records

        Returns:
            Formatted table string
        """
        if not records:
            return "No records found"

        # Get all unique field names across all records
        all_fields = set()
        for record in records.values():
            if isinstance(record, dict):
                all_fields.update(record.keys())

        # Sort fields
        fields = sorted(all_fields)

        # Build header
        columns = ["key"] + fields
        col_widths = {col: len(col) for col in columns}

        # Calculate column widths
        for key, record in records.items():
            col_widths["key"] = max(col_widths["key"], len(str(key)))
            if isinstance(record, dict):
                for field in fields:
                    value = str(record.get(field, ""))
                    col_widths[field] = max(col_widths.get(field, 0), len(value))

        # Format header
        header = " | ".join(col.ljust(col_widths[col]) for col in columns)
        separator = "-" * len(header)

        # Format rows
        rows = []
        for key in sorted(records.keys()):
            record = records[key]
            if isinstance(record, dict):
                row_values = [str(key).ljust(col_widths["key"])]
                for field in fields:
                    value = str(record.get(field, ""))
                    row_values.append(value.ljust(col_widths[field]))
                rows.append(" | ".join(row_values))

        return f"{header}\n{separator}\n" + "\n".join(rows) + f"\n\n{len(records)} record(s)"

    def format_output(self, records: Dict[str, Any], output_format: str) -> str:
        """Format records according to specified format

        Args:
            records: Dictionary of records
            output_format: One of: table, json, jsonl, oneline, csv

        Returns:
            Formatted output string
        """
        if output_format == "json":
            return json.dumps(records, indent=2, ensure_ascii=False)

        elif output_format == "jsonl":
            lines = []
            for key, record in sorted(records.items()):
                if isinstance(record, dict):
                    record_with_key = {"_key": key, **record}
                    lines.append(json.dumps(record_with_key, ensure_ascii=False))
            return "\n".join(lines)

        elif output_format == "oneline":
            lines = []
            for key, record in sorted(records.items()):
                if isinstance(record, dict):
                    pairs = [f"{k}:{v}" for k, v in record.items()]
                    lines.append(f"{key} " + " ".join(pairs))
            return "\n".join(lines)

        elif output_format == "csv":
            if not records:
                return ""

            # Get all unique field names
            all_fields = set()
            for record in records.values():
                if isinstance(record, dict):
                    all_fields.update(record.keys())

            fields = sorted(all_fields)

            # Header
            lines = ["key," + ",".join(fields)]

            # Rows
            for key in sorted(records.keys()):
                record = records[key]
                if isinstance(record, dict):
                    values = [str(key)]
                    for field in fields:
                        value = str(record.get(field, ""))
                        # Escape commas and quotes
                        if "," in value or '"' in value:
                            value = '"' + value.replace('"', '""') + '"'
                        values.append(value)
                    lines.append(",".join(values))

            return "\n".join(lines)

        else:  # table (default)
            return self.format_table(records)

    def run(self, args: List[str] = None) -> int:
        """Run CLI with given arguments

        Args:
            args: Command line arguments (defaults to sys.argv[1:])

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)

        try:
            # Handle special case: "databases" as first argument
            if parsed_args.database == "databases":
                databases = DictStore.list_databases(self.driver)
                if databases:
                    print(f"Databases ({self.format_name}):")
                    for db in databases:
                        print(f"  {db}")
                    print(f"\n{len(databases)} database(s)")
                else:
                    print(f"No databases found in {self.format_name} format")
                return 0

            # Handle special case: "collections" as second argument
            if parsed_args.collection == "collections":
                if not parsed_args.database:
                    print("Error: 'collections' command requires a database name", file=sys.stderr)
                    print("Usage: jb <database> collections", file=sys.stderr)
                    return 1

                store = DictStore(parsed_args.database, self.driver)
                collections = store.list_collections()
                if collections:
                    print(f"Collections in '{parsed_args.database}':")
                    for coll in collections:
                        print(f"  {coll}")
                    print(f"\n{len(collections)} collection(s)")
                else:
                    print(f"No collections found in database '{parsed_args.database}'")
                return 0

            # Handle --import flag
            if parsed_args.import_flag:
                if not parsed_args.database or not parsed_args.collection:
                    print("Error: import requires database and collection", file=sys.stderr)
                    print("Usage: jb <database> <collection> --import", file=sys.stderr)
                    print("   or: cat data.txt | jb <database> <collection> import", file=sys.stderr)
                    return 1

                # Create store instance
                store = DictStore(parsed_args.database, self.driver)

                # Import records from stdin
                imported = 0
                errors = 0
                error_lines = []

                try:
                    # Case 1: Import from JSON object
                    if parsed_args.json:
                        try:
                            content = sys.stdin.read()
                            if content.strip():
                                data_map = json.loads(content)
                                for key, record in data_map.items():
                                    store.set(parsed_args.collection, key, record)
                                    imported += 1
                        except Exception as e:
                            errors += 1
                            error_lines.append((0, f"JSON Parse Error: {e}"))

                    # Case 2: Import from space-separated format or JSON Lines
                    else:
                        for line_num, line in enumerate(sys.stdin, 1):
                            line = line.strip()
                            if not line or line.startswith('#'):
                                continue

                            try:
                                # Check if it's JSON Lines
                                if line.startswith('{') and line.endswith('}'):
                                    record = json.loads(line)
                                    key = record.pop("_key", None)
                                    if key:
                                        store.set(parsed_args.collection, str(key), record)
                                        imported += 1
                                        continue
                                    else:
                                        raise ValueError("JSON Line missing '_key' field")

                                # Standard format: key field:value ...
                                parts = line.split()
                                if len(parts) < 2:
                                    errors += 1
                                    error_lines.append((line_num, f"Invalid format: {line}"))
                                    continue

                                key = parts[0]
                                data = self.parse_key_values(parts[1:])
                                store.set(parsed_args.collection, key, data)
                                imported += 1

                            except ValueError as e:
                                errors += 1
                                error_lines.append((line_num, str(e)))
                            except Exception as e:
                                errors += 1
                                error_lines.append((line_num, f"Unexpected error: {e}"))

                    # Report results
                    print(f"✓ Imported {imported} record(s) into {parsed_args.collection}")

                    if errors > 0:
                        print(f"⚠ {errors} line(s) skipped due to errors:", file=sys.stderr)
                        for line_num, error in error_lines[:5]:
                            print(f"  Line {line_num}: {error}", file=sys.stderr)
                        if len(error_lines) > 5:
                            print(f"  ... and {len(error_lines) - 5} more", file=sys.stderr)

                    return 0 if imported > 0 else 1

                except KeyboardInterrupt:
                    print(f"\n⚠ Import interrupted. Imported {imported} record(s) before interruption.")
                    return 1

            # Handle --delete flag
            if parsed_args.delete_flag:
                import shutil

                # Delete collection
                if parsed_args.database and parsed_args.collection:
                    store = DictStore(parsed_args.database, self.driver)
                    collection_path = store._get_collection_path(parsed_args.collection)

                    if not collection_path.exists():
                        print(f"Error: Collection '{parsed_args.collection}' not found in database '{parsed_args.database}'", file=sys.stderr)
                        return 1

                    collection_path.unlink()
                    print(f"✓ Deleted collection '{parsed_args.collection}' from database '{parsed_args.database}'")
                    return 0

                # Delete database
                elif parsed_args.database:
                    store = DictStore(parsed_args.database, self.driver)

                    if not store.db_dir.exists():
                        print(f"Error: Database '{parsed_args.database}' not found", file=sys.stderr)
                        return 1

                    # Count collections before deleting
                    collections = store.list_collections()

                    shutil.rmtree(store.db_dir)
                    print(f"✓ Deleted database '{parsed_args.database}' ({len(collections)} collection(s))")
                    return 0

                else:
                    print("Error: --delete requires database name", file=sys.stderr)
                    print("Usage: jb <database> --delete                     # Delete database", file=sys.stderr)
                    print("   or: jb <database> <collection> --delete       # Delete collection", file=sys.stderr)
                    return 1

            # Handle --list flag
            if parsed_args.list:
                # List databases (no database specified)
                if not parsed_args.database:
                    databases = DictStore.list_databases(self.driver)
                    if databases:
                        print(f"Databases ({self.format_name}):")
                        for db in databases:
                            print(f"  {db}")
                        print(f"\n{len(databases)} database(s)")
                    else:
                        print(f"No databases found in {self.format_name} format")
                    return 0

                # List collections in database
                else:
                    store = DictStore(parsed_args.database, self.driver)
                    collections = store.list_collections()
                    if collections:
                        print(f"Collections in '{parsed_args.database}':")
                        for coll in collections:
                            print(f"  {coll}")
                        print(f"\n{len(collections)} collection(s)")
                    else:
                        print(f"No collections found in database '{parsed_args.database}'")
                    return 0

            # Handle explicit 'collections' command (third position)
            if parsed_args.command == "collections":
                if not parsed_args.database:
                    print("Error: 'collections' command requires a database name", file=sys.stderr)
                    print("Usage: jb <database> collections", file=sys.stderr)
                    return 1

                store = DictStore(parsed_args.database, self.driver)
                collections = store.list_collections()
                if collections:
                    print(f"Collections in '{parsed_args.database}':")
                    for coll in collections:
                        print(f"  {coll}")
                    print(f"\n{len(collections)} collection(s)")
                else:
                    print(f"No collections found in database '{parsed_args.database}'")
                return 0

            # Handle explicit 'databases' command (third position)
            if parsed_args.command == "databases":
                databases = DictStore.list_databases(self.driver)
                if databases:
                    print(f"Databases ({self.format_name}):")
                    for db in databases:
                        print(f"  {db}")
                    print(f"\n{len(databases)} database(s)")
                else:
                    print(f"No databases found in {self.format_name} format")
                return 0

            # Validate required arguments for CRUD commands
            if not parsed_args.database or not parsed_args.collection or not parsed_args.command:
                print("Error: database, collection, and command are required for CRUD operations", file=sys.stderr)
                parser.print_help()
                return 1

            # Create store instance
            store = DictStore(parsed_args.database, self.driver)

            # Determine output format
            if parsed_args.json:
                output_format = "json"
            elif parsed_args.jsonl:
                output_format = "jsonl"
            elif parsed_args.oneline:
                output_format = "oneline"
            elif parsed_args.csv:
                output_format = "csv"
            else:
                output_format = "table"

            # Execute command
            if parsed_args.command == "set":
                if len(parsed_args.args) < 2:
                    print("Error: 'set' requires key and at least one field:value pair", file=sys.stderr)
                    return 1

                key = parsed_args.args[0]
                data = self.parse_key_values(parsed_args.args[1:])
                store.set(parsed_args.collection, key, data)
                print(f"✓ Set record '{key}' in {parsed_args.collection}")

            elif parsed_args.command == "get":
                if len(parsed_args.args) != 1:
                    print("Error: 'get' requires exactly one key", file=sys.stderr)
                    return 1

                key = parsed_args.args[0]
                record = store.get(parsed_args.collection, key)

                if record is None:
                    print(f"Error: Record '{key}' not found", file=sys.stderr)
                    return 1

                # Format single record
                output = self.format_output({key: record}, output_format)
                print(output)

            elif parsed_args.command == "del":
                if len(parsed_args.args) != 1:
                    print("Error: 'del' requires exactly one key", file=sys.stderr)
                    return 1

                key = parsed_args.args[0]
                deleted = store.delete(parsed_args.collection, key)

                if deleted:
                    print(f"✓ Deleted record '{key}' from {parsed_args.collection}")
                else:
                    print(f"Error: Record '{key}' not found", file=sys.stderr)
                    return 1

            elif parsed_args.command == "keys":
                keys = store.keys(parsed_args.collection)
                for key in keys:
                    print(key)

                if not keys:
                    print(f"No records in {parsed_args.collection}")

            elif parsed_args.command == "all":
                records = store.all(parsed_args.collection)
                output = self.format_output(records, output_format)
                print(output)

            return 0

        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
