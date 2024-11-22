"""Main Tovald module."""

import re

from jinja2 import Template
from pathlib import Path


class InvalidDocTreeError(Exception):
    """Provided documentation tree is invalid somehow"""


def validate_documentation_tree(path: Path) -> None:
    """Make sure documentation tree is properly structured.

    Args:
    ----
        path (str): documentation tree root path
    """

    h1 = re.compile(r"(?m)^# (.+)")

    for root, dirnames, filenames in path.walk():
        if root.stem == ".assets":
            continue

        if "index.md" not in filenames:
            raise InvalidDocTreeError

        index = root / "index.md"
        with index.open(mode="r") as index:
            index = index.read()

        if len(h1.findall(index)) != 1:
            raise InvalidDocTreeError


def build_sphinx_tree(path: Path) -> None:
    """Enhance naked documentation tree to with sphix structure.

    Args:
    ----
        path (Path): documentation tree root path
    """

    raise NotImplementedError


def toctree_indexer(path: Path) -> None:
    """Inject toctree node in every tree index that has children pages.

    Args:
    ----
        path (Path): documentation tree root path
    """

    options = ["glob", "hidden", "titlesonly"]

    toctree = Path(__file__).parent / "static/toctree.j2"

    with toctree.open("r") as toctree:
        template = Template(toctree.read())

    toctree = template.render(options=options)

    for root, dirnames, _ in path.walk():
        children = [c for c in dirnames if not c.startswith(".")]
        if not children:
            continue

        index = root / "index.md"
        with index.open("a", encoding="utf-8") as index:
            index.write(toctree)


def main() -> None:
    """Program entrypoint."""

    raise NotImplementedError


if __name__ == "__main__":
    main()
