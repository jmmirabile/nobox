#!/usr/bin/env python3
"""
NoBox entry points for jsonbox and yamlbox commands

This module provides the main() functions that are called when
users run 'jsonbox' or 'yamlbox' from the command line.

The setup.py entry_points configuration maps:
- jsonbox command → main_json()
- yamlbox command → main_yaml()
"""

import sys
from .cli import CLI
from .drivers import JSONDriver, YAMLDriver


def main_json():
    """Entry point for jsonbox command

    Uses JSONDriver for JSON format storage.

    Example:
        $ jsonbox mydb users set alice name:Alice age:30
        $ jb mydb users get alice  # 'jb' is the suggested alias
    """
    try:
        driver = JSONDriver()
        cli = CLI(driver)
        exit_code = cli.run()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nAborted")
        sys.exit(130)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


def main_yaml():
    """Entry point for yamlbox command

    Uses YAMLDriver for YAML format storage.

    Example:
        $ yamlbox mydb users set alice name:Alice age:30
        $ yb mydb users get alice  # 'yb' is the suggested alias
    """
    try:
        driver = YAMLDriver()
        cli = CLI(driver)
        exit_code = cli.run()
        sys.exit(exit_code)
    except ImportError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Install PyYAML with: pip install PyYAML", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAborted")
        sys.exit(130)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # When run directly, default to JSON
    main_json()
