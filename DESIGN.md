# NoBox Design Document

## Overview

**NoBox** - JSON and YAML key-value storage utilities for flexible, schema-less data storage via CLI.

Part of the [Box Suite](https://github.com/jmmirabile/confbox) - a modular Python CLI utility framework.

---

## Design Philosophy

Following Box Suite principles:
- ✅ **Modular** - Solves one problem well (flexible data storage)
- ✅ **Independent** - Works standalone, no dependencies except ConfBox
- ✅ **Complementary** - Stores data for other tools, integrates with Unix pipelines
- ✅ **Professional** - Production-ready, tested, documented

---

## Architecture

### Package Structure

**Single package with two entry points:**

```
nobox/                       # Package name
├── __init__.py             # Package exports
├── drivers.py              # Driver base class, JSONDriver, YAMLDriver
├── store.py                # DictStore - all CRUD logic
├── cli.py                  # CLI class - command parsing and execution
└── main.py                 # Entry points for jsonbox and yamlbox
```

**Entry points (setup.py):**
```python
entry_points={
    'console_scripts': [
        'jsonbox=nobox.main:main_json',    # Uses JSONDriver
        'yamlbox=nobox.main:main_yaml',    # Uses YAMLDriver
    ],
}
```

**Result:**
```bash
pip install nobox
# Provides two commands:
jsonbox (alias: jb)    # JSON format
yamlbox (alias: yb)    # YAML format
```

---

## Driver Architecture

**Pluggable format drivers** - same logic, different serialization:

```python
class Driver:
    """Base driver interface"""

    @property
    def extension(self) -> str:
        """File extension (.json, .yaml)"""

    @property
    def app_name(self) -> str:
        """App directory name (jsonbox, yamlbox)"""

    def load_collection(self, path: Path) -> dict:
        """Load collection from file"""

    def save_collection(self, path: Path, data: dict):
        """Save collection to file"""


class JSONDriver(Driver):
    extension = ".json"
    app_name = "nobox"
    format_subdir = "json"
    # Uses json.load() / json.dump()


class YAMLDriver(Driver):
    extension = ".yaml"
    app_name = "nobox"
    format_subdir = "yaml"
    # Uses yaml.safe_load() / yaml.safe_dump()
```

**All CRUD logic is shared** - only serialization differs!

---

## File Storage Structure

**Single `nobox` directory with format subdirectories**

```
~/.local/share/nobox/            # Via ConfBox get_app_data_dir("nobox")
├── json/                         # ← JSON format storage
│   └── mydb/                     # ← Database (directory)
│       ├── users.json            # ← Collection (file)
│       └── products.json
└── yaml/                         # ← YAML format storage
    └── mydb/                     # ← Same database, YAML format
        ├── users.yaml            # ← Collection (file)
        └── products.yaml
```

**Benefits:**
- Single storage location (easier to backup)
- Both formats can coexist for same database
- Clear format separation (json/ vs yaml/)
- Migration-friendly (export from one, import to other)

**Collection file contents:**
```json
{
  "alice": {"name": "Alice", "age": 30, "email": "alice@example.com"},
  "bob": {"name": "Bob", "role": "admin"}
}
```

---

## CLI Interface

### Command Syntax

```bash
<command> <database> <collection> <operation> [args] [flags]
```

**Commands:**
- `jsonbox` (jb) - JSON format
- `yamlbox` (yb) - YAML format

### Operations

| Operation | Syntax | Description |
|-----------|--------|-------------|
| **keys** | `jb mydb users keys` | List all record keys |
| **get** | `jb mydb users get <key>` | Get specific record |
| **set** | `jb mydb users set <key> field:value ...` | Create/update record |
| **del** | `jb mydb users del <key>` | Delete record |
| **all** | `jb mydb users all` | Show all records |
| **import** | `cat file \| jb mydb users import` | Import from stdin |

### Examples

```bash
# Set a record with key:value pairs
jb mydb users set alice name:Alice age:30 email:alice@example.com

# Get a specific record
jb mydb users get alice

# List all keys
jb mydb users keys

# Show all records
jb mydb users all

# Delete a record
jb mydb users del alice

# Import from stdin
cat parsed_data.txt | jb mydb users import
```

---

## Output Formats

**Multiple output formats for Unix pipeline integration:**

### Default: Pretty Table (terminal viewing)
```bash
jb mydb users all

# Output:
# key          | name            | age             | email
# -------------------------------------------------------------------------
# alice        | Alice           | 30              | alice@example.com
# bob          | Bob             |                 | bob@example.com
```

### --json: Full JSON object
```bash
jb mydb users all --json

# Output:
# {"alice": {"name": "Alice", "age": 30}, "bob": {"name": "Bob"}}
```

### --jsonl: JSON Lines (one object per line)
```bash
jb mydb users all --jsonl

# Output:
# {"_key":"alice","name":"Alice","age":30,"email":"alice@example.com"}
# {"_key":"bob","name":"Bob","email":"bob@example.com"}
```

### --oneline: Key-value pairs (for grep/awk)
```bash
jb mydb users all --oneline

# Output:
# alice name:Alice age:30 email:alice@example.com
# bob name:Bob email:bob@example.com

# Easy to pipe:
jb mydb users all --oneline | grep "age:30"
jb mydb users all --oneline | awk '{print $1, $2}'
```

### --csv: CSV format (for Excel)
```bash
jb mydb users all --csv > users.csv

# Output:
# key,name,age,email
# alice,Alice,30,alice@example.com
# bob,Bob,,bob@example.com
```

---

## Use Cases

### 1. Network Device Configuration Snapshots
```bash
# Extract F5 LTM VIP configs (complex nested data)
./extract_f5_vips.sh | jb f5 vips import

# Query later
jb f5 vips get prod-web-vip --json | jq '.pool.members'

# Generate diagrams
jb f5 vips all --json | python generate_topology.py | dot -Tsvg > diagram.svg

# Export for documentation
jb f5 vips all --csv > vip_inventory.csv
```

### 2. API Response Caching
```bash
# Cache API responses
curl https://api.example.com/users | jb cache api set users --json-stdin

# Query cached data
jb cache api get users --json | jq '.[] | select(.active==true)'
```

### 3. Operational Data Storage
```bash
# Parse and store server inventory
ssh server "show inventory" | awk '{print $1, "ip:"$2, "os:"$3}' | jb inventory servers import

# Query
jb inventory servers keys | grep prod
jb inventory servers all --oneline | grep "os:linux"
```

### 4. Quick Data Capture
```bash
# Store notes/todos with arbitrary fields
jb notes tasks set fix-dns priority:high notes:"Check resolver" assigned:alice

# Flexible fields - no schema required
jb notes tasks set deploy-app priority:low deadline:2026-02-15 status:pending
```

---

## Comparison: DBBox vs NoBox

| Aspect | DBBox (SQL) | NoBox (Key-Value) |
|--------|-------------|-------------------|
| **Storage** | SQLite database | JSON/YAML files |
| **Schema** | Required upfront | Schema-less |
| **Data Model** | Tables with rows | Collections with key→dict |
| **Best For** | Structured, relational data | Nested, flexible data |
| **CLI** | Flags (`-c`, `-r`, `-u`, `-d`) | Commands (`set`, `get`, `del`) |
| **Use When** | Fixed schema, SQL queries | Variable fields, complex structures |

**Example - F5 VIP Data:**

**DBBox approach (flat, requires schema):**
```bash
db f5 vips --schema name:TEXT destination:TEXT pool:TEXT
db f5 vips -c "prod-vip" "10.1.1.1:443" "web_pool"
# Problem: Can't store nested pool members, SSL profiles, etc.
```

**NoBox approach (nested, flexible):**
```bash
jb f5 vips set prod-vip \
  destination:10.1.1.1:443 \
  pool:'{"name":"web_pool","members":["10.2.1.10","10.2.1.11"]}' \
  ssl_profiles:'["client-ssl","server-ssl"]'
# Natural representation of complex nested data
```

---

## stdin Import Format

**One record per line: `key field:value field:value ...`**

```bash
# Input format
echo "alice name:Alice age:30 email:alice@example.com" | jb mydb users import
echo "bob name:Bob role:admin" | jb mydb users import

# From parsed data
cat f5_vips.txt | awk '{print $1, "dest:"$2, "pool:"$3}' | jb f5 vips import
```

---

## Dependencies

- **Python 3.8+**
- **confbox** >= 0.1.0 (for `get_app_data_dir()`)
- **PyYAML** (for yamlbox/YAMLDriver only)

---

## Implementation Notes

### Single User, No Concurrency

- **Scope:** Personal productivity tool for sysadmins/developers
- **No locking:** Single user, no concurrent access concerns
- **Simple file I/O:** Load entire collection → modify → save

### When to Use NoBox vs Text Files

**Use NoBox when:**
- ✅ Data has nested/complex structure (JSON-like)
- ✅ Want structured CRUD operations
- ✅ Multiple collections need organization
- ✅ Want multiple output formats (JSON, CSV, oneline)

**Use text files + awk when:**
- ✅ Data is flat/tabular
- ✅ Simple grep/awk queries suffice
- ✅ You know awk well

**NoBox shines for hierarchical data; text files win for simple tables.**

---

## Development Roadmap

### Phase 1: Core Implementation
- [ ] Implement Driver base class and JSON/YAML drivers
- [ ] Implement DictStore (CRUD operations)
- [ ] Implement CLI with basic commands (set, get, del, keys, all)
- [ ] Default table output format

### Phase 2: Output Formats
- [ ] Implement --json output
- [ ] Implement --jsonl output
- [ ] Implement --oneline output
- [ ] Implement --csv output

### Phase 3: stdin Support
- [ ] Implement import command
- [ ] Parse key:value format from stdin
- [ ] Handle bulk imports

### Phase 4: Polish
- [ ] Error handling and validation
- [ ] Help text and documentation
- [ ] Unit tests
- [ ] Integration tests

### Phase 5: Release
- [ ] Complete README with examples
- [ ] setup.py and pyproject.toml
- [ ] Version 0.1.0
- [ ] Publish to PyPI

---

## Future Enhancements (Optional)

- [ ] **TOMLDriver** - Add TOML format support
- [ ] **Query language** - Simple filtering (`--where "age > 30"`)
- [ ] **Nested key access** - `jb mydb users get alice.email`
- [ ] **Backup/export** - Export entire database
- [ ] **Merge/import** - Merge from another database
- [ ] **Schema validation** - Optional schema enforcement
- [ ] **Encryption** - Encrypted storage option

---

## Design Decisions Log

### 2026-02-06: Single Package, Two Entry Points
- **Decision:** One package (nobox) with two commands (jsonbox/yamlbox)
- **Rationale:** DRY - all code shared, only driver differs
- **Implementation:** setup.py entry_points trick

### 2026-02-06: Directory = Database, File = Collection
- **Decision:** Database is a directory, collection is a file
- **Rationale:** Don't load entire database for one collection, scalable

### 2026-02-07: Single nobox Directory with Format Subdirectories
- **Decision:** Use `~/.local/share/nobox/` with `json/` and `yaml/` subdirectories
- **Rationale:**
  - Single storage location (one package, one directory)
  - Both formats can coexist peacefully
  - Enables easy migration (export from yaml, import to json)
  - Cleaner than separate jsonbox/yamlbox directories
  - Matches package name (nobox)

### 2026-02-06: Multiple Output Formats
- **Decision:** Support --json, --jsonl, --oneline, --csv, table
- **Rationale:** Unix pipeline integration, different use cases (jq, Excel, grep)

### 2026-02-06: Schema-less by Design
- **Decision:** No schema enforcement, flexible key:value storage
- **Rationale:** Complement to DBBox (schema-based), handles variable fields

### 2026-02-06: key:value CLI Syntax
- **Decision:** Use `field:value` pairs for setting data
- **Rationale:** Natural format from awk output, easy to parse, clear syntax

### 2026-02-06: Single User Tool
- **Decision:** No concurrent access handling, no locking
- **Rationale:** Personal productivity tool, not multi-user database

---

**Created:** 2026-02-06
**Status:** Design phase
**Next:** Begin implementation
