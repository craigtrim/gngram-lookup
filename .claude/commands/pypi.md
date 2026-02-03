# Publish Context

Publish gngram-counter to PyPI.

**User Instructions:** $ARGUMENTS

## Prerequisites

- All tests must pass: `make all`
- Version must be bumped in `pyproject.toml` before publishing
- The PyPI API token is stored at `pypi.key` in the project root

## Publish Command

Use `poetry publish` -- not twine. Twine 6.x rejects the `license-file` metadata field that poetry-core generates.

```bash
poetry build && poetry publish --username __token__ --password "$(cat pypi.key)"
```

## Full Workflow

1. Run `make all` (install, test) -- all tests must pass
2. If lint fails, run `ruff check --fix .` and retry
3. Build and publish with poetry:

```bash
poetry build && poetry publish --username __token__ --password "$(cat pypi.key)"
```

4. Verify the release is live at `https://pypi.org/project/gngram-counter/<version>/`

## Important Notes

- Never use `twine upload` -- it conflicts with poetry-core's metadata format
- Never commit `pypi.key` -- it should be in `.gitignore`
- The `builder/` directory is excluded from the package (see pyproject.toml)

## Data Distribution

Data files are NOT distributed via PyPI. They are:
1. Built with `make build-hash`
2. Packaged with `make package-release`
3. Uploaded to GitHub releases
4. Downloaded by users via `python -m gngram_counter.download_data`
