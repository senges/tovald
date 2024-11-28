# Tovald

Push rich Markdown documentation to Confluence.

## usage (beta)

Export following variables :
- `CONFLUENCE_SERVER_URL`: confluence instance URL
- `CONFLUENCE_SPACE_KEY`: target confluence space
- `CONFLUENCE_PARENT_PAGE` (optional): any parent page in given space
- `CONFLUENCE_PAT`: service account personal access token

```
$ uv run python tovald/main.py DOCUMENTATION_PATH
```

## Contribution

Project management is achieved with `uv`.

```
$ uv sync --dev
```

Install pre-commit hooks.
```
$ uv run pre-commit install [--install-hooks]
```
