"""..."""

from pathlib import Path
from typing import ClassVar


class AssetsCompiler:
    """Crawl documentation and compile any asset."""

    compilers: ClassVar = {}

    def __init__(self, path: Path) -> None:
        """Class entrypoint.

        Args:
        ----
            path (Path): documentation path

        """
        raise NotImplementedError

    @classmethod
    def register(cls) -> None:
        """Register new file compiler."""
        raise NotImplementedError

    @classmethod
    def compile(cls, path: Path) -> None:
        """Crawl and compile assets."""
        raise NotImplementedError
