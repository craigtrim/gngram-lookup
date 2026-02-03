# Git Context

Handle git operations for gngram-counter repository based on the user's instructions.

**User Instructions:** $ARGUMENTS

## Repository Structure

```
gngram-counter/
├── gngram_counter/          # Main package
│   ├── __init__.py          # Public API exports
│   ├── data.py              # Data path utilities
│   └── download_data.py     # Download from GitHub releases
├── builder/                 # Build scripts
│   ├── build_unigrams.py    # Process raw 1-gram data
│   ├── build_hash_files.py  # Create hash-bucketed files
│   ├── report_stats.py      # Report parquet stats
│   └── package_release.py   # Package for release
├── tests/                   # Test suite
├── pyproject.toml           # Package config
└── Makefile                 # Build commands
```

## CRITICAL: No Co-Authored-By Lines

**NEVER add this line to ANY commit message:**
```
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

This is strictly forbidden. No Claude attribution. No co-author lines. No exceptions.

## Commit Message Format

**Keep commit messages to one line.** Use conventional commit prefixes:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code restructuring
- `test:` - Test additions or changes
- `chore:` - Maintenance tasks

**Examples:**
- `feat: Add lookup function for word frequencies`
- `fix: Handle missing parquet files gracefully`
- `refactor: Simplify hash bucket logic`

**Do NOT include in commit messages:**
- Lists of files changed (git shows this)
- Multi-paragraph descriptions
- "Key features" or bullet point summaries
- **NEVER add `Co-Authored-By:` lines**

## Commit Rules

- **One-line messages** - No multi-line commit messages for regular commits
- **ABSOLUTELY NO Co-Authored-By lines** - Strictly forbidden
- **Atomic commits** - One logical change per commit

## Pull Request Rules

- **No Co-Authored-By attributions** - Do not add Claude attribution to PR descriptions
- **No bot signatures** - Do not add "Generated with Claude Code" or similar footers
- **Clean descriptions** - Keep PR body simple: summary and test plan only

## Checking for Changes

```bash
# All changes
git status
git diff HEAD

# Main package
git status -- gngram_counter/
git diff HEAD -- gngram_counter/

# Builder scripts
git status -- builder/
git diff HEAD -- builder/

# Tests only
git status -- tests/
```

## Staging Changes

```bash
# Single file
git add gngram_counter/data.py

# Main package
git add gngram_counter/

# Builder scripts
git add builder/

# Tests
git add tests/
```

## Creating Commits

```bash
git commit -m "prefix: Commit message here"
```

## Verifying Commits

```bash
git log -1 --oneline
```

## Development Workflow

Before committing:
1. Run `make lint` to check code style
2. Run `make test` to verify all tests pass
3. Stage and commit changes

## Instructions

Follow the user's instructions in `$ARGUMENTS`. This may include:
- Committing specific changes
- Checking what has changed
- Creating commits with specific messages
- Reviewing recent commit history

Always check for changes before attempting to commit. If no changes exist, inform the user and stop.
