# NoBox

**JSON and YAML key-value storage utilities with CRUD operations via CLI**

Part of the [Box Suite](https://github.com/jmmirabile/confbox) - a modular Python CLI utility framework.

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
# Discover what's stored
jb --list                        # List all databases
jb mydb --list                   # List collections in a database

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
yb --list                        # List YAML databases
yb mydb users set bob name:Bob role:admin
```

## Commands

### List Databases

```bash
jb --list              # or jb -l
jb databases           # explicit command
```

**Examples:**
```bash
# List all JSON databases
jb --list

# Output:
# Databases (JSON):
#   contacts
#   inventory
#   mydb
#
# 3 database(s)

# List all YAML databases
yb -l
```

### List Collections

```bash
jb <database> --list       # or jb <database> -l
jb <database> collections  # explicit command
```

**Examples:**
```bash
# List collections in a database
jb mydb --list

# Output:
# Collections in 'mydb':
#   products
#   users
#
# 2 collection(s)

# Short form
jb inventory -l

# Explicit command
jb contacts collections
```

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
cat data.txt | jb <database> <collection> --import
cat data.txt | jb <database> <collection> -i
```

Import records from stdin, one per line.

---

## Import Format (IMPORTANT!)

Each line must follow this exact format:
```
key field:value field:value field:value
↑   ↑
|   Space-separated field:value pairs (NOT commas!)
Record key (required, first word)
```

### Valid Example
```
alice name:Alice email:alice@example.com age:30
bob name:Bob department:engineering salary:75000
charlie name:Charlie role:manager
```

### Invalid Examples ❌
```
# Missing key
name:Alice email:alice@example.com

# Using commas instead of spaces
alice name:Alice,email:alice@example.com,age:30

# Missing colons
alice Alice alice@example.com 30
```

---

**Features:**
- Auto type conversion (numbers are parsed as int/float)
- Skips empty lines and comments (lines starting with #)
- Reports success count and error details
- Best-effort import (continues on errors)

**Examples:**
```bash
# Import from a file
cat data.txt | jb mydb users --import

# File format (one record per line):
# alice name:Alice age:30 email:alice@example.com
# bob name:Bob department:engineering salary:75000

# Import parsed data with awk
cat servers.txt | awk '{print $1, "ip:"$2, "os:"$3}' | jb inventory servers -i

# Import from a script
./extract_data.sh | jb cache results --import

# Single line import
echo "server1 ip:10.1.1.10 status:active" | jb infra hosts -i

# Multiple records
printf "web1 ip:10.1.1.1 role:frontend\nweb2 ip:10.1.1.2 role:frontend\n" | jb infra servers --import
```

**Error Handling:**
```bash
$ cat data.txt | jb mydb users import
✓ Imported 10 record(s) into users
⚠ 2 line(s) skipped due to errors:
  Line 5: Invalid format 'baddata'. Use 'field:value' format.
  Line 8: Missing field:value pairs: incomplete
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

## Hierarchical Navigation

NoBox provides intuitive hierarchical discovery:

```bash
# Level 1: What databases exist?
jb -l
→ contacts, inventory, mydb

# Level 2: What collections in this database?
jb mydb -l
→ users, products

# Level 3: What keys in this collection?
jb mydb users keys
→ alice, bob, charlie

# Level 4: What data in this record?
jb mydb users get alice
→ name:Alice, age:30, email:alice@example.com
```

This hierarchical interface makes it easy to explore your data without remembering specific names.

## Complete Workflow Example

Here's a complete example showing discovery, creation, and querying:

```bash
# Start fresh - check what databases exist
$ jb -l
No databases found in JSON format

# Create some data
$ jb contacts people set alice name:Alice email:alice@example.com phone:555-1234
✓ Set record 'alice' in people

$ jb contacts people set bob name:Bob email:bob@example.com department:engineering
✓ Set record 'bob' in people

$ jb contacts companies set acme name:"Acme Corp" industry:manufacturing employees:500
✓ Set record 'acme' in companies

# Discover what we created
$ jb -l
Databases (JSON):
  contacts

1 database(s)

$ jb contacts -l
Collections in 'contacts':
  companies
  people

2 collection(s)

$ jb contacts people keys
alice
bob

# Query the data
$ jb contacts people all
key   | department  | email               | name  | phone
-----------------------------------------------------------------
alice |             | alice@example.com   | Alice | 555-1234
bob   | engineering | bob@example.com     | Bob   |

2 record(s)

# Export as JSON for further processing
$ jb contacts people all --json
{
  "alice": {
    "email": "alice@example.com",
    "name": "Alice",
    "phone": "555-1234"
  },
  "bob": {
    "department": "engineering",
    "email": "bob@example.com",
    "name": "Bob"
  }
}

# Export as CSV for Excel
$ jb contacts people all --csv > contacts.csv
$ cat contacts.csv
key,department,email,name,phone
alice,,alice@example.com,Alice,555-1234
bob,engineering,bob@example.com,Bob,

# Use with jq for complex queries
$ jb contacts people all --json | jq '.[] | select(.department=="engineering")'
{
  "department": "engineering",
  "email": "bob@example.com",
  "name": "Bob"
}

# One-line format for grep/awk
$ jb contacts people all --oneline | grep alice
alice email:alice@example.com name:Alice phone:555-1234
```

## Use Cases

### Network Device Configurations
```bash
# Extract F5 LTM configs
./extract_f5_vips.sh | jb f5 vips import

# Discover what's stored
jb -l                            # See all device databases
jb f5 -l                         # See all F5 collections (vips, pools, etc.)

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

# Discover inventory structure
jb inventory -l                   # See all collections (servers, switches, etc.)
jb inventory servers keys         # List all server names

# Query
jb inventory servers keys | grep prod
jb inventory servers all --csv > inventory.csv
```

### Quick Notes/Todos
```bash
# Flexible fields - no schema needed
jb notes tasks set fix-dns priority:high assigned:alice notes:"Check resolver config"
jb notes tasks set deploy priority:low deadline:2026-02-15

# Explore your notes
jb -l                             # See all note databases
jb notes -l                       # See all note collections (tasks, ideas, etc.)
jb notes tasks keys               # List all task names

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

## Quick Reference Card

### Discovery Commands
```bash
jb -l                          # List all JSON databases
jb --list                      # Same as above (long form)
jb databases                   # Same as above (explicit)

jb mydb -l                     # List collections in mydb
jb mydb --list                 # Same as above (long form)
jb mydb collections            # Same as above (explicit)

jb mydb users keys             # List keys in users collection
```

### CRUD Commands
```bash
jb mydb users set alice name:Alice age:30    # Create/update record
jb mydb users get alice                      # Get specific record
jb mydb users all                            # Show all records
jb mydb users del alice                      # Delete record

# Import from stdin (one record per line)
cat data.txt | jb mydb users import          # Bulk import
```

### Output Formats
```bash
jb mydb users all              # Pretty table (default)
jb mydb users all --json       # JSON object
jb mydb users all --jsonl      # JSON Lines (one per line)
jb mydb users all --oneline    # key field:value format
jb mydb users all --csv        # CSV for Excel
```

### YAML Format
```bash
yb -l                          # List YAML databases
yb mydb -l                     # List collections
yb mydb users set bob name:Bob # Same commands as jb
```

## Links

- **PyPI:** https://pypi.org/project/nobox/ (coming soon)
- **GitHub:** https://github.com/jmmirabile/nobox
- **ConfBox:** https://github.com/jmmirabile/confbox
- **DBBox:** https://github.com/jmmirabile/dbbox
- **Box Suite Design:** See ConfBox repository for the full Box Suite vision
