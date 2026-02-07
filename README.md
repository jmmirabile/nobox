# NoBox

**JSON and YAML key-value storage utilities with CRUD operations via CLI**

Part of the [Box Suite](https://github.com/jmmirabile/confbox) - a modular Python CLI application framework.

> **Status:** 🔨 In development - design complete, implementation in progress

## Features

- **Schema-less storage** - flexible key-value collections
- **Two formats** - JSON and YAML (choose your preference)
- **Simple CRUD** via command-line (`set`, `get`, `del`, `keys`, `all`)
- **Multiple output formats** - JSON, JSON Lines, CSV, one-line, pretty tables
- **Cross-platform storage** using [ConfBox](https://pypi.org/project/confbox/)
- **Unix-friendly** - pipe data in and out
- **Zero configuration** - just install and use

## Installation

```bash
pip install nobox
```

Or install from source:

```bash
git clone https://github.com/jmmirabile/nobox.git
cd nobox
pip install -e .
```

## Storage Location

NoBox uses ConfBox to store databases in OS-specific data directories:

| OS | Storage Location |
|----|------------------|
| Linux | `~/.local/share/nobox/` |
| macOS | `~/Library/Application Support/nobox/` |
| Windows | `%APPDATA%\nobox\` |

**Directory Structure:**
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

**Key Features:**
- Single storage location for both formats
- Both JSON and YAML can coexist for the same database
- Easy migration between formats using export/import
- Cleaner backup and management

## Quick Start

```bash
# Create/update a record (JSON format)
jb mydb users set alice name:Alice age:30 email:alice@example.com

# Get a specific record
jb mydb users get alice

# List all keys
jb mydb users keys

# Show all records
jb mydb users all

# Delete a record
jb mydb users del alice

# Use YAML format instead
yb mydb users set bob name:Bob role:admin
```

## Commands

### Set (Create/Update)
```bash
jb <database> <collection> set <key> <field:value> ...
```

**Examples:**
```bash
jb contacts people set alice name:Alice phone:555-1234
jb inventory servers set web1 ip:10.1.1.10 os:linux role:webserver
```

### Get (Read)
```bash
jb <database> <collection> get <key>
```

**Examples:**
```bash
jb contacts people get alice
jb inventory servers get web1
```

### Delete
```bash
jb <database> <collection> del <key>
```

**Examples:**
```bash
jb contacts people del alice
```

### Keys (List)
```bash
jb <database> <collection> keys
```

**Examples:**
```bash
jb contacts people keys
jb contacts people keys | grep alice
```

### All (Show All Records)
```bash
jb <database> <collection> all [--format]
```

**Examples:**
```bash
jb contacts people all                    # Pretty table (default)
jb contacts people all --json             # JSON object
jb contacts people all --jsonl            # JSON Lines
jb contacts people all --oneline          # key field:value format
jb contacts people all --csv > data.csv   # CSV for Excel
```

### Import (from stdin)
```bash
cat data.txt | jb <database> <collection> import
```

**Examples:**
```bash
# Import parsed data
cat servers.txt | awk '{print $1, "ip:"$2, "os:"$3}' | jb inventory servers import

# Import from script
./extract_data.sh | jb cache results import
```

## Output Formats

### Default: Pretty Table
```bash
jb mydb users all

# Output:
# key          | name            | age             | email
# -------------------------------------------------------------------------
# alice        | Alice           | 30              | alice@example.com
# bob          | Bob             | 25              | bob@example.com
```

### JSON
```bash
jb mydb users all --json

# Output:
# {"alice": {"name": "Alice", "age": 30}, "bob": {"name": "Bob", "age": 25}}
```

### JSON Lines
```bash
jb mydb users all --jsonl

# Output:
# {"_key":"alice","name":"Alice","age":30,"email":"alice@example.com"}
# {"_key":"bob","name":"Bob","age":25,"email":"bob@example.com"}
```

### One-line (for grep/awk)
```bash
jb mydb users all --oneline

# Output:
# alice name:Alice age:30 email:alice@example.com
# bob name:Bob age:25 email:bob@example.com

# Easy to pipe:
jb mydb users all --oneline | grep "age:30"
```

### CSV (for Excel)
```bash
jb mydb users all --csv > users.csv

# Output:
# key,name,age,email
# alice,Alice,30,alice@example.com
# bob,Bob,25,bob@example.com
```

## Use Cases

### Network Device Configurations
```bash
# Extract F5 LTM configs
./extract_f5_vips.sh | jb f5 vips import

# Query later
jb f5 vips get prod-web-vip --json | jq '.pool.members'

# Generate diagrams
jb f5 vips all --json | python generate_diagram.py > topology.svg
```

### API Response Caching
```bash
# Cache API response
curl https://api.example.com/users | jb cache api set users --json-stdin

# Query cached data
jb cache api get users --json | jq '.[] | select(.active==true)'
```

### Server Inventory
```bash
# Parse and store
ssh server "show inventory" | awk '{print $1, "ip:"$2, "os:"$3}' | jb inventory servers import

# Query
jb inventory servers keys | grep prod
jb inventory servers all --csv > inventory.csv
```

### Quick Notes/Todos
```bash
# Flexible fields - no schema needed
jb notes tasks set fix-dns priority:high assigned:alice notes:"Check resolver config"
jb notes tasks set deploy priority:low deadline:2026-02-15

# Query
jb notes tasks all --oneline | grep "priority:high"
```

## JSON vs YAML

**jsonbox (jb):**
- Faster parsing
- Universal format
- Better for machine processing
- Pipe to `jq` for queries

**yamlbox (yb):**
- More human-readable
- Supports comments
- Better for hand-editing
- Cleaner syntax

**Both use the same commands and syntax!**

```bash
jb mydb users set alice name:Alice    # Stores in ~/.local/share/nobox/json/
yb mydb users set alice name:Alice    # Stores in ~/.local/share/nobox/yaml/
```

**Migration between formats:**
```bash
# Export from YAML and import to JSON
yb mydb users all --json | jb mydb users import-json

# Both formats can coexist in the same nobox directory
```

## Python API

NoBox can also be used as a Python library:

```python
from nobox import DictStore
from nobox.drivers import JSONDriver

# Create store with JSON driver
store = DictStore("mydb", JSONDriver())

# Set a record
store.set("users", "alice", {"name": "Alice", "age": 30})

# Get a record
user = store.get("users", "alice")
print(user)  # {"name": "Alice", "age": 30}

# List keys
keys = store.keys("users")

# Get all records
all_users = store.all("users")

# Delete a record
store.delete("users", "alice")
```

## Comparison: DBBox vs NoBox

| Feature | DBBox (SQL) | NoBox (Key-Value) |
|---------|-------------|-------------------|
| **Storage** | SQLite database | JSON/YAML files |
| **Schema** | Required upfront | Schema-less |
| **Data Model** | Tables with rows | Collections with key→dict |
| **Best For** | Structured relational data | Nested, flexible data |
| **Queries** | SQL | Get by key, list all |

**Use DBBox when:**
- Fixed schema, structured data
- SQL queries needed
- Relational data with joins

**Use NoBox when:**
- Variable/flexible fields
- Nested complex structures
- JSON/YAML natural format
- Quick data capture

## The Box Suite

NoBox is part of the Box Suite - a collection of modular Python packages for building CLI applications:

- **[ConfBox](https://pypi.org/project/confbox/)** ✅ - Cross-platform configuration management
- **[DBBox](https://github.com/jmmirabile/dbbox)** ✅ - SQLite database utility
- **NoBox** 🔨 - JSON/YAML key-value storage (this package)
- **PlugBox** 🔨 - Plugin system (planned)
- **CLIBox** 🔨 - Complete CLI framework (planned)
- **APIBox** 🔨 - API testing tool (planned)

Each package can be used independently or together for maximum flexibility.

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

## Requirements

- Python 3.8+
- [confbox](https://pypi.org/project/confbox/) >= 0.1.0
- PyYAML (for yamlbox/YAML format)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- **PyPI:** https://pypi.org/project/nobox/ (coming soon)
- **GitHub:** https://github.com/jmmirabile/nobox
- **ConfBox:** https://github.com/jmmirabile/confbox
- **DBBox:** https://github.com/jmmirabile/dbbox
- **Box Suite Design:** See ConfBox repository for the full Box Suite vision
