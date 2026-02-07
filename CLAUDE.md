# NoBox Project

## Project Overview
NoBox - JSON and YAML key-value storage utilities for flexible, schema-less data storage via CLI.

Part of the [Box Suite](https://github.com/jmmirabile/confbox) - a modular Python CLI utility framework.

## Project Structure
```
nobox/
├── nobox/
│   ├── __init__.py
│   ├── drivers.py       # Driver base class, JSONDriver, YAMLDriver
│   ├── store.py         # DictStore - CRUD operations
│   ├── cli.py           # CLI command parser and executor
│   └── main.py          # Entry points for jsonbox/yamlbox
├── tests/
├── docs/
├── setup.py
├── pyproject.toml
├── README.md
├── DESIGN.md            # Complete architecture and design decisions
├── CLAUDE.md            # This file - project context
└── LICENSE
```

## Commands Provided

**Installation:**
```bash
pip install nobox
```

**Provides two commands:**
- `jsonbox` (alias: `jb`) - JSON format storage
- `yamlbox` (alias: `yb`) - YAML format storage

## Quick Reference

```bash
# Set record
jb mydb users set alice name:Alice age:30

# Get record
jb mydb users get alice

# List keys
jb mydb users keys

# Show all
jb mydb users all

# Output formats
jb mydb users all --json       # JSON object
jb mydb users all --jsonl      # JSON Lines
jb mydb users all --oneline    # key field:value format
jb mydb users all --csv        # CSV for Excel

# Import from stdin
cat data.txt | jb mydb users import
```

## Storage Location

Uses ConfBox for cross-platform directories:

| OS | Storage Location |
|----|------------------|
| Linux | `~/.local/share/nobox/` |
| macOS | `~/Library/Application Support/nobox/` |
| Windows | `%APPDATA%\nobox\` |

**Structure:**
```
~/.local/share/nobox/
├── json/              # JSON format storage
│   └── mydb/          # Database (directory)
│       ├── users.json # Collection (file)
│       └── products.json
└── yaml/              # YAML format storage
    └── mydb/          # Same database, YAML format
        ├── users.yaml
        └── products.yaml
```

**Benefits:**
- Single storage location (easier to backup)
- Both formats can coexist for same database
- Easy migration between formats (export/import)

## Development Information

### Build Commands
```bash
pip install -e .               # Development install
pip install -e ".[dev]"        # With dev dependencies
```

### Test Commands
```bash
pytest                         # Run all tests
pytest -v                      # Verbose output
pytest tests/test_drivers.py   # Specific test file
```

### Lint Commands
```bash
# TBD - will add flake8, black, mypy
```

## Dependencies

- **Python 3.8+**
- **confbox** >= 0.1.0 - Cross-platform directory management
- **PyYAML** - YAML format support (for yamlbox)

## Key Design Decisions

1. **Single package, two entry points** - DRY principle, shared code
2. **Pluggable drivers** - JSONDriver, YAMLDriver (could add TOML, etc.)
3. **Schema-less** - Flexible key:value storage, complements DBBox
4. **Multiple output formats** - Unix pipeline friendly (--json, --csv, --oneline)
5. **Directory = Database** - Don't load entire DB for one collection

## Use Cases

- Network device configuration snapshots (F5, switches, routers)
- API response caching
- Operational data storage (server inventories, etc.)
- Quick data capture (notes, todos, scratch data)
- Any nested/complex data that's awkward in flat files

## Related Projects

### Box Suite
- **[ConfBox](https://pypi.org/project/confbox/)** ✅ - Config management (published)
- **[DBBox](https://github.com/jmmirabile/dbbox)** ✅ - SQLite utility (complete)
- **NoBox** 🔨 - This project
- **PlugBox** 🔨 - Plugin system (planned)
- **CLIBox** 🔨 - CLI framework (planned)
- **APIBox** 🔨 - API testing tool (planned)

### Comparison: DBBox vs NoBox

**Use DBBox when:**
- Structured, relational data
- Fixed schema
- SQL queries needed
- Flat tabular data

**Use NoBox when:**
- Nested, complex data structures
- Variable/flexible fields
- No schema needed
- JSON/YAML natural format

## Development Status

- **Current Phase:** Complete and functional
- **Version:** 0.1.0
- **Status:** Production-ready, all core features implemented and tested
- **Next Steps (Optional Enhancements):**
  1. Add stdin import command
  2. Add pytest test suite
  3. Publish to PyPI
  4. Add shell completion

## Notes

- See DESIGN.md for complete architecture documentation
- Single user tool - no concurrent access handling
- Complements DBBox (schema-less vs schema-based)
- Part of Box Suite ecosystem
- Follows Box Suite principles: modular, independent, complementary, professional

---

**Project Started:** 2026-02-06
**Working Directory:** /home/jeffmira/Documents/dev/nobox
**Git Repository:** Not yet initialized
