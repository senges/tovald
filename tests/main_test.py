"""Test suite for main module."""

import pytest
import shutil

from filecmp import dircmp
from pathlib import Path

from tovald.main import (
    build_sphinx_tree,
    validate_documentation_tree,
    toctree_indexer,
    InvalidDocTreeError,
)


def match_directories(dcmp: dircmp) -> bool:
    if dcmp.diff_files:
        return False

    for subdir in dcmp.subdirs.values():
        if not match_directories(subdir):
            return False

    return True


@pytest.fixture
def static_path():
    return Path(__file__).parent / "static"


class TestValidateDocumentationTree:
    """Test suite for validate_documentation_tree function"""

    def test_validate_documentation_tree_valid_tree(self, static_path):
        """
        Tests that function works on a complex valid documentation tree.

        Given: Valid documentation tree
        Expect: Function returns True
        """

        valid_path = static_path / "valid_tree/doc"

        try:
            validate_documentation_tree(valid_path)
        except InvalidDocTreeError:
            pytest.fail("Documentation tree should be valid.")

    def test_validate_documentation_tree_missing_index_node(self, static_path):
        """
        Tests that function detects a missing index node in complex documentation tree.

        Given: Documentation tree with missing index node
        Expect: Function returns False
        """

        invalid_path = static_path / "missing_index_tree/doc"
        print(invalid_path)

        with pytest.raises(InvalidDocTreeError):
            validate_documentation_tree(invalid_path)

    def test_validate_documentation_tree_multiple_heading(self, static_path):
        """
        Tests that index node with multiple heading 1 is detected.
        This would cause confluence to create multiple pages.

        Given: Documentation tree with one index node have 2 heading 1 token.
        Expect: Function returns False
        """

        invalid_path = static_path / "double_heading_tree/doc"

        with pytest.raises(InvalidDocTreeError):
            validate_documentation_tree(invalid_path)


class TestBuildSphinxTree:
    """Test suite for build_sphinx_tree function"""

    def test_build_sphinx_tree(self, mocker, tmp_path):
        """
        Tests that function produces a properly configured directory
        for sphinxcontrib-confluencebuilder.

        Given: Documentation path
        Expect: Valid sphinx directory
        """

        tmp_path = Path(tmp_path)

        toctree_indexer_patch = mocker.patch("tovald.main.toctree_indexer")
        build_sphinx_tree(tmp_path)
        toctree_indexer_patch.assert_called_once_with(tmp_path)

        directory_objects = list(tmp_path.iterdir())

        confpy = tmp_path / "conf.py"
        assert confpy in directory_objects
        assert confpy.is_file()

        assets = tmp_path / "assets"
        assert assets in directory_objects
        assert assets.is_dir()


class TestToctreeIndexer:
    """Test suite for toctree_indexer function"""

    def test_toctree_indexer(self, tmp_path, static_path):
        """
        Tests that function produces a properly indexed toc tree structure.

        Given: Documentation tree
        Expect: Documentation tree with injected toc indexes
        """

        tmp_path = Path(tmp_path)

        input_path = static_path / "valid_tree/doc"
        control_path = static_path / "valid_tree/toc"

        shutil.copytree(input_path, tmp_path, dirs_exist_ok=True)
        toctree_indexer(tmp_path)

        assert match_directories(dircmp(control_path, tmp_path))
