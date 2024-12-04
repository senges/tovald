"""Main Tovald module."""

import argparse
import re
import shutil
from pathlib import Path
from tempfile import mkdtemp

from jinja2 import Template
from sphinx.application import Sphinx

from tovald import __version__


class InvalidDocTreeError(Exception):
    """Provided documentation tree is invalid somehow."""


def validate_documentation_tree(path: Path) -> None:
    """Make sure documentation tree is properly structured.

    Args:
    ----
        path (str): documentation tree root path

    """
    h1 = re.compile(r"(?m)^# (.+)")

    if not path.is_dir():
        raise InvalidDocTreeError

    for root, _, filenames in path.walk():
        if root.stem == ".assets":
            continue

        if "index.md" not in filenames:
            raise InvalidDocTreeError

        index = root / "index.md"
        with index.open(mode="r") as index:
            raw_index = index.read()

        if len(h1.findall(raw_index)) != 1:
            raise InvalidDocTreeError


def build_sphinx_tree(path: Path) -> None:
    """Enhance naked documentation tree to with sphix structure.

    Args:
    ----
        path (Path): documentation tree root path

    """
    resolvpath = Path(__file__).resolve().parent

    toctree_indexer(path)

    shutil.copyfile(resolvpath / "conf.py", path / "conf.py")
    shutil.copytree(resolvpath / "assets", path / "assets")


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


def publish(path: Path) -> None:
    """Publish sphinx-formatted documentation.

    Args:
    ----
        path (Path): sphinx documentation tree root path

    """
    app = Sphinx(
        srcdir=path,
        confdir=path,
        doctreedir=path / "_doctree",
        outdir=path / "xml",
        buildername="confluence",
        freshenv=True,
    )

    app.build(force_all=True)


def main() -> None:
    """Program entrypoint."""
    parser = argparse.ArgumentParser()

    parser.add_argument("DOCUMENTATION")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    documentation = Path(args.DOCUMENTATION)
    validate_documentation_tree(documentation)

    output_directory = Path(mkdtemp(suffix="_sphinx"))
    shutil.copytree(documentation, output_directory, dirs_exist_ok=True)

    build_sphinx_tree(output_directory)
    publish(output_directory)


if __name__ == "__main__":
    main()
