# NoBox Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-02-10

### ⚠️ BREAKING CHANGES

#### Case-Sensitive Keys
**Keys are now case-sensitive to comply with JSON/YAML specifications.**

- **v0.1.0 behavior**: Keys were case-insensitive ("Jeff", "jeff", "JEFF" all mapped to "jeff")
- **v0.2.0 behavior**: Keys are case-sensitive ("Jeff", "jeff", "JEFF" are three different keys)

**Why this change:**
1. **JSON/YAML spec compliance**: Both specifications define keys as case-sensitive
2. **Data portability**: Prevents data corruption when round-tripping data
3. **Example problem**:
   ```
   Original system: {"User": {...}, "user": {...}}  # Two keys
   Import to v0.1.0: {"user": {...}}                # MERGED - data lost!
   Export back:      {"user": {...}}                # "User" gone forever!
   ```

**Migration guide:**
- Review your existing data for keys that differ only in case
- Update your scripts/workflows to use exact case when accessing records
- Keys like "Alice" must now be accessed as "Alice", not "alice"

### Fixed

#### Set Operation Now Merges Data
**The `set` command now properly merges fields instead of replacing entire records.**

- **Bug (v0.1.0)**: Setting a single field would remove all other fields
  - Example: If record had `{name: "Nick", email: "nick@example.com"}`, running `set nick age:25` resulted in `{age: 25}` (other fields removed!)

- **Fix (v0.2.0)**: Setting a field now merges with existing data
  - Example: Same record, running `set nick age:25` results in `{name: "Nick", email: "nick@example.com", age: 25}` (all fields preserved!)

**Technical details:**
- Modified `DictStore.set()` to use `dict.update()` for existing records
- Only replaces entire record if it doesn't exist or isn't a dict

### Added

#### Delete Operations
- **Delete database**: `jb <database> -d` or `jb <database> --delete`
- **Delete collection**: `jb <database> <collection> -d` or `jb <database> <collection> --delete`
- Confirmation prompts for safety
- Works for both JSON and YAML formats

### Changed

#### Documentation
- Updated all documentation to reflect case-sensitive keys
- Added breaking change summary document
- Updated docstrings throughout codebase to note case-sensitivity
- Clarified set operation merge behavior in README and docstrings

---

## [0.1.0] - 2026-02-09

### Added

#### Hierarchical Discovery Interface 🎉
- **List databases** command with three syntax options:
  - `jb --list` or `jb -l` (flag-based)
  - `jb databases` (explicit command)
  - Works for both JSON (`jb`) and YAML (`yb`) formats

- **List collections** command with three syntax options:
  - `jb <database> --list` or `jb <database> -l` (flag-based)
  - `jb <database> collections` (explicit command)
  - Shows all collections within a database

- **Hierarchical navigation** pattern:
  1. `jb -l` → databases
  2. `jb mydb -l` → collections
  3. `jb mydb users keys` → keys
  4. `jb mydb users get alice` → record data

#### Command Aliases
- Added `jb` as short alias for `jsonbox`
- Added `yb` as short alias for `yamlbox`
- Aliases registered in both `setup.py` and `pyproject.toml`

#### Import from stdin 🎉
- **Import command** for bulk data loading:
  - `cat file.txt | jb mydb users import`
  - Format: `key field:value field:value ...` (one record per line)
  - Auto type conversion (integers, floats)
  - Skips empty lines and comments (# prefix)
  - Error handling with detailed reporting
  - Best-effort import (continues on errors)
  - Works with both JSON and YAML formats

#### Core Features (Previously Implemented)
- Driver architecture (JSONDriver, YAMLDriver)
- DictStore with full CRUD operations
- Multiple output formats:
  - Pretty table (default)
  - JSON (`--json`)
  - JSON Lines (`--jsonl`)
  - One-line format (`--oneline`)
  - CSV (`--csv`)
- ~~Case-insensitive key storage~~ (removed in v0.2.0)
- Cross-platform storage via ConfBox

### Changed

#### Documentation
- **README.md**:
  - Added "Hierarchical Navigation" section with examples
  - Added "Complete Workflow Example" demonstrating end-to-end usage
  - Added "Quick Reference Card" for common commands
  - Updated all use case examples to show discovery commands
  - Updated command sections with database/collection listing

- **DESIGN.md**:
  - Added `databases` and `collections` to operations table
  - Added "Hierarchical Navigation" section
  - Updated examples to show discovery workflow
  - Updated roadmap with completed phases
  - Added design decision entries for new features (2026-02-09)

- **CLAUDE.md**:
  - Updated Quick Reference with discovery commands
  - Updated Development Status with current progress
  - Added hierarchical discovery to Key Design Decisions
  - Clarified TODO items (import command, tests)

#### Code
- **store.py**:
  - Added `DictStore.list_databases(driver)` class method
  - Lists all databases for a given format (JSON/YAML)

- **cli.py**:
  - Made `database`, `collection`, and `command` arguments optional
  - Added `-l`/`--list` flag for hierarchical listing
  - Added `databases` and `collections` to command choices
  - Added `import` command with stdin reading and error handling
  - Implemented smart command routing for discovery vs CRUD
  - Updated help text with discovery and import examples

- **setup.py** & **pyproject.toml**:
  - Added `jb` and `yb` console script entry points

### Added Files
- **demo.sh**: Comprehensive demo script showcasing all features
- **CHANGELOG.md**: This file

### TODO Before Release

#### High Priority
- [ ] Add pytest test suite
- [ ] Add input validation (database/collection names)
- [ ] Prevent path traversal vulnerabilities

#### Medium Priority
- [ ] Shell completion scripts (bash/zsh)
- [ ] Add `--version` flag
- [ ] More comprehensive error messages

#### Nice to Have
- [ ] Batch operations (set-many, del-many)
- [ ] Query/filter capabilities
- [ ] Backup/export entire database

---

## Version History

### [0.1.0] - 2026-02-09
Initial release with core features and hierarchical discovery.

**Known Issues (Fixed in v0.2.0)**:
- Keys were case-insensitive (breaking: now case-sensitive)
- Set operation replaced entire record instead of merging fields
