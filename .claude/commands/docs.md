# Documentation Context

Documentation guidelines for gngram-counter.

**User Instructions:** $ARGUMENTS

## Documentation Location

Primary documentation lives in:
- `README.md` - Package overview, installation, usage
- Code docstrings - API documentation

## README Structure

The README should cover:

1. **Overview** - What gngram-counter does
2. **Installation** - pip install and data download
3. **Usage** - Basic API examples
4. **Data Format** - Schema of parquet files
5. **Building Data** - For maintainers rebuilding from source

## Code Documentation

Keep docstrings concise but informative:

```python
def get_hash_file(prefix: str) -> Path:
    """Return path to a specific hash bucket parquet file.

    Args:
        prefix: Two hex characters (00-ff)

    Returns:
        Path to the parquet file

    Raises:
        FileNotFoundError: If data files not installed
    """
```

## When to Update Documentation

- **README.md** - When API changes or new features added
- **Docstrings** - When function behavior changes
- **pyproject.toml description** - When package purpose changes

## Instructions

Follow the user's instructions in `$ARGUMENTS`. Apply these documentation guidelines:

- Keep documentation minimal and focused
- Update README when user-facing behavior changes
- Ensure docstrings match actual function behavior
