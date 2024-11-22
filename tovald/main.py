"""Main Tovald module."""

from pathlib import Path


class InvalidDocTreeError(Exception):
    """Provided documentation tree is invalid somehow"""


def validate_documentation_tree(path: Path) -> None:
    """Make sure documentation tree is properly structured.

    Args:
    ----
        path (str): documentation tree root path
    """

    raise NotImplementedError


def build_sphinx_tree(path: Path) -> None:
    """Enhance naked documentation tree to with sphix structure.

    Args:
    ----
        path (str): documentation tree root path
    """

    raise NotImplementedError


def toctree_indexer(path: Path) -> None:
    """Inject toctree node in every tree index that has children pages.

    Args:
    ----
        path (str): documentation tree root path
    """

    raise NotImplementedError


def main() -> None:
    """Program entrypoint."""

    raise NotImplementedError


if __name__ == "__main__":
    main()
