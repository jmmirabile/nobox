# NoBox Changelog

## [0.1.0] - 2026-02-09 (Pre-release)

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
- Case-insensitive key storage
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

### [0.1.0] - 2026-02-09 (Pre-release)
Initial pre-release with core features and hierarchical discovery.

**Note**: This version is feature-complete for core functionality but lacks:
- stdin import command (documented but not implemented)
- Test suite
- Input validation

Once these are added, this will be promoted to official 0.1.0 release.
