# Tovald

Publish rich Markdown documentation to Confluence.

## usage (alpha)

Install tovald with `pipx install tovald` or run virtualenv `uv run tovald`.

Export the following variables :
- `CONFLUENCE_SERVER_URL`: confluence instance URL
- `CONFLUENCE_SPACE_KEY`: target confluence space
- `CONFLUENCE_PARENT_PAGE` (optional): any parent page in a given space
- `CONFLUENCE_PAT`: service account personal access token
- `CONFLUENCE_SOURCES_URL` (optional): sources repository URL

```
usage: tovald [-h] [-v] DOCUMENTATION

positional arguments:
  DOCUMENTATION

options:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
```

## Documentation structure

In Confluence, documentation is organized using a hierarchical structure of pages and sub-pages.

* Page 1
    * Sub-page 1
    * Sub-page 2
        * Sub-sub-page 1
* Page 2
    * Sub-page 3

Similarly, in tovald documentation structure, each page is represented as a folder containing an `index.md` file and an optional `.assets` folder.
* The `index.md` file holds the content of the page, and the first-level `# heading` is used as the page title in the page tree view.
* The `.assets` folder contains any static asset required by the given index page.

```
doc
├── index.md
└── operational-guide
    ├── .assets
    │   └── demo.png
    └── index.md
```

## Editorial guide

Standard markdown is supported, as well as [MyST flavored syntax](https://myst-parser.readthedocs.io/en/latest/index.html).

Most Confluence built-in features are also available via [confluencebuilder](https://sphinxcontrib-confluencebuilder.readthedocs.io)
(ie. Jira integration, emoticon, mentions, macros, ...).

## Contribution

Project management is achieved with `uv`.

```
$ uv sync --dev
```

Install pre-commit hooks.
```
$ uv run pre-commit install [--install-hooks]
```

## Credits

Tovald is just a modest wrapper around various tools:
- [sphinx-doc/sphinx](https://github.com/sphinx-doc/sphinx)
- [sphinx-contrib/confluencebuilder](https://github.com/sphinx-contrib/confluencebuilder)
- [executablebooks/MyST-Parser](https://github.com/executablebooks/MyST-Parser)
