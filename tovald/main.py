"""Main Tovald module."""

import argparse
import shutil
import sys
from pathlib import Path
from tempfile import mkdtemp

from jinja2 import Template
from sphinx.application import Sphinx
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceError
from sphinxcontrib.confluencebuilder.publisher import ConfluencePublisher

from tovald import __version__


class InvalidDocTreeError(Exception):
    """Provided documentation tree is invalid somehow."""


def panic(message: str) -> None:
    """Program Panic.

    Args:
    ----
        message (str): error message to display before exit

    """
    print(message)
    sys.exit(1)


def validate_documentation_tree(path: Path) -> None:
    """Make sure documentation tree is properly structured.

    Args:
    ----
        path (str): documentation tree root path

    """
    if not path.is_dir():
        panic("Documentation path is not a directory.")

    for root, _, filenames in path.walk():
        if root.stem == ".assets":
            continue

        if "index.md" not in filenames:
            panic(f"Missing index in {root}.")


def build_sphinx_tree(path: Path) -> None:
    """Enhance naked documentation tree to with sphix structure.

    Args:
    ----
        path (Path): documentation tree root path

    """
    resolvpath = Path(__file__).resolve().parent

    toctree_indexer(path)

    shutil.copyfile(resolvpath / "conf.py", path / "conf.py")


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


def make_sphinx(path: Path) -> Sphinx:
    """Create Sphinx application instance.

    Args:
    ----
        path (Path): documentation tree root path

    """
    return Sphinx(
        srcdir=path,
        confdir=path,
        doctreedir=path / "_doctree",
        outdir=path / "xml",
        buildername="confluence",
        freshenv=True,
    )


def publish(path: Path) -> None:
    """Publish sphinx-formatted documentation.

    Args:
    ----
        path (Path): sphinx documentation tree root path

    """
    app = make_sphinx(path)
    app.build(force_all=True)


def cleanup(path: Path) -> None:
    """Clean up Confluence parent page by removing all child pages.

    Args:
    ----
        path (Path): documentation path

    """
    app = make_sphinx(path)

    try:
        if not (publisher := getattr(app.builder, "publisher", None)):
            publisher = ConfluencePublisher()
            publisher.init(app.config)

        publisher.connect()

        if not (parent_id := publisher.get_base_page_id()):
            panic("No parent page configured or found")

        # Get and remove all child pages
        if child_pages := publisher.get_descendants(parent_id, "search-aggressive"):
            print(f"Removing {len(child_pages)} pages...")
            [publisher.remove_page(page_id) for page_id in child_pages]
            print("Cleanup completed successfully")
        else:
            print("No child pages found to remove")
    except ConfluenceError as e:
        panic(f"Cleanup failed: {e}")


def main() -> None:
    """Program entrypoint."""
    parser = argparse.ArgumentParser()

    parser.add_argument("DOCUMENTATION")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-c", "--cleanup", action="store_true")
    args = parser.parse_args()

    documentation = Path(args.DOCUMENTATION)
    validate_documentation_tree(documentation)

    output_directory = Path(mkdtemp(suffix="_sphinx"))
    shutil.copytree(documentation, output_directory, dirs_exist_ok=True)

    build_sphinx_tree(output_directory)
    if args.cleanup:
        cleanup(output_directory)
    else:
        publish(output_directory)


if __name__ == "__main__":
    main()
