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

Storage location (via ConfBox):
  Linux: ~/.local/share/nobox/{self.driver.format_subdir}/
  macOS: ~/Library/Application Support/nobox/{self.driver.format_subdir}/
  Windows: %APPDATA%\\nobox\\{self.driver.format_subdir}\\
""".format(cmd="jb" if self.format_name == "JSON" else "yb")
        )

        parser.add_argument("database", help="Database name")
        parser.add_argument("collection", help="Collection name")
        parser.add_argument(
            "command",
            choices=["set", "get", "del", "keys", "all"],
            help="Command to execute"
        )
        parser.add_argument(
            "args",
            nargs="*",
            help="Command arguments (key for get/del, key field:value... for set)"
        )

        # Output format options
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output as JSON"
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
