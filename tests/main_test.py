"""Test suite for main module."""

import pytest

from pathlib import Path

from tovald.main import validate_documentation_tree, InvalidDocTreeError


class TestValidateDocumentationTree:
    """Test suite for validate_documentation_tree function"""

    def test_validate_documentation_tree_valid_tree(self):
        """
        Tests that function works on a complex valid documentation tree.

        Given: Valid documentation tree
        Expect: Function returns True
        """

        valid_path = Path(__file__) / "static/valid_tree/doc"

        try:
            validate_documentation_tree(valid_path)
        except InvalidDocTreeError:
            pytest.fail("Documentation tree should be valid.")

    def test_validate_documentation_tree_missing_index_node(self):
        """
        Tests that function detects a missing index node in complex documentation tree.

        Given: Documentation tree with missing index node
        Expect: Function returns False
        """

        invalid_path = Path(__file__) / "static/missing_index_tree/doc"

        with pytest.raises(InvalidDocTreeError):
            validate_documentation_tree(invalid_path)

    def test_validate_documentation_tree_multiple_heading(self):
        """
        Tests that index node with multiple heading 1 is detected.
        This would cause confluence to create multiple pages.

        Given: Documentation tree with one index node have 2 heading 1 token.
        Expect: Function returns False
        """

        invalid_path = Path(__file__) / "static/double_heading_tree/doc"

        with pytest.raises(InvalidDocTreeError):
            validate_documentation_tree(invalid_path)


class TestBuildSphinxTree:
    """Test suite for build_sphinx_tree function"""


class TestToctreeIndexer:
    """Test suite for toctree_indexer function"""
