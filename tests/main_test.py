"""Test suite for main module."""

import shutil
from filecmp import dircmp
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from tovald.main import (
    InvalidDocTreeError,
    build_sphinx_tree,
    main,
    publish,
    toctree_indexer,
    validate_documentation_tree,
)


def match_directories(dcmp: dircmp) -> bool:
    """Check if directories match."""
    if dcmp.diff_files:
        return False

    for subdir in dcmp.subdirs.values():
        if not match_directories(subdir):
            return False

    return True


@pytest.fixture
def static_path() -> Path:
    """Test static data folder."""
    return Path(__file__).parent / "static"


class TestValidateDocumentationTree:
    """Test suite for validate_documentation_tree function."""

    def test_validate_documentation_tree_valid_tree(self, static_path: Path) -> None:
        """Tests that function works on a complex valid documentation tree.

        Given: Valid documentation tree
        Expect: Function do not raise InvalidDocTreeError exception
        """
        valid_path = static_path / "valid_tree/doc"

        try:
            validate_documentation_tree(valid_path)
        except InvalidDocTreeError:
            pytest.fail("Documentation tree should be valid.")

    def test_validate_documentation_tree_path_not_exist(self, mocker: MockerFixture, static_path: Path) -> None:
        """Tests that function can detect that a documentation path does not exist.

        Given: A wrong documentation path
        Expect: Function calls panic with not a directory message
        """
        invalid_path = static_path / "definitely/not/existing/doc"
        panic_patch = mocker.patch("tovald.main.panic")
        panic_patch.side_effect = InvalidDocTreeError

        with pytest.raises(InvalidDocTreeError):
            validate_documentation_tree(invalid_path)

        panic_patch.assert_called_once_with("Documentation path is not a directory.")

    def test_validate_documentation_tree_missing_index_node(self, mocker: MockerFixture, static_path: Path) -> None:
        """Tests that function detects a missing index node in complex documentation tree.

        Given: Documentation tree with missing index node
        Expect: Function calls panic with missing index message
        """
        invalid_path = static_path / "missing_index_tree/doc"
        panic_patch = mocker.patch("tovald.main.panic")
        panic_patch.side_effect = InvalidDocTreeError

        with pytest.raises(InvalidDocTreeError):
            validate_documentation_tree(invalid_path)

        panic_patch.assert_called_once_with(f"Missing index in {invalid_path / "level-1/level-2"}.")

    @pytest.mark.skip(reason="Removed due to improper implementation.")
    def test_validate_documentation_tree_multiple_heading(self, mocker: MockerFixture, static_path: Path) -> None:
        """Tests that index node with multiple heading 1 is detected.

        This would cause confluence to create multiple pages.

        Given: Documentation tree with one index node have 2 heading 1 token.
        Expect: Function calls panic with multiple headings message
        """
        invalid_path = static_path / "double_heading_tree/doc"
        panic_patch = mocker.patch("tovald.main.panic")
        panic_patch.side_effect = InvalidDocTreeError

        with pytest.raises(InvalidDocTreeError):
            validate_documentation_tree(invalid_path)

        panic_patch.assert_called_once_with(
            f"Multiple h1 headings found in {invalid_path / "level-1/level-2/level-3"} index."
        )


class TestBuildSphinxTree:
    """Test suite for build_sphinx_tree function."""

    def test_build_sphinx_tree(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Tests that function produces a properly configured directory for confluencebuilder.

        Given: Documentation path
        Expect: Valid sphinx directory
        """
        toctree_indexer_patch = mocker.patch("tovald.main.toctree_indexer")
        build_sphinx_tree(tmp_path)
        toctree_indexer_patch.assert_called_once_with(tmp_path)

        directory_objects = list(tmp_path.iterdir())

        confpy = tmp_path / "conf.py"
        assert confpy in directory_objects
        assert confpy.is_file()


class TestToctreeIndexer:
    """Test suite for toctree_indexer function."""

    def test_toctree_indexer(self, tmp_path: Path, static_path: Path) -> None:
        """Tests that function produces a properly indexed toc tree structure.

        Given: Documentation tree
        Expect: Documentation tree with injected toc indexes
        """
        input_path = static_path / "valid_tree/doc"
        control_path = static_path / "valid_tree/toc"

        shutil.copytree(input_path, tmp_path, dirs_exist_ok=True)
        toctree_indexer(tmp_path)

        assert match_directories(dircmp(control_path, tmp_path))


class TestPublish:
    """Test suite for publish function."""

    def test_publish(self, tmp_path: Path, static_path: Path) -> None:
        """Tests that function produces a reproductible conf tree.

        Given: Sphinx tree
        Expect: Confluence xml conf tree
        """
        input_path = static_path / "valid_tree/sphinx"
        control_path = static_path / "valid_tree/xml"

        shutil.copytree(input_path, tmp_path, dirs_exist_ok=True)
        publish(tmp_path)

        assert match_directories(dircmp(control_path, tmp_path / "xml"))


class TestMain:
    """Test suite for main function."""

    def test_main(self, mocker: MockerFixture, tmp_path: Path, static_path: Path) -> None:
        """Tests that main function perlerly chain things together.

        Given: Documentation path
        Expect: Enhanced copy of this documentation to publish
        """
        input_path = static_path / "valid_tree/doc"
        documentation_path = tmp_path / "documentation"
        mkdtemp_path = tmp_path / "mkdtemp"

        shutil.copytree(input_path, documentation_path)

        mocker.patch("tovald.main.argparse._sys.argv", ["tovald", str(documentation_path)])
        mocker.patch("tovald.main.publish")
        mocker.patch("tovald.main.mkdtemp").return_value = mkdtemp_path

        main()

        assert match_directories(dircmp(input_path, documentation_path))
        assert match_directories(dircmp(static_path / "valid_tree/toc", mkdtemp_path))

    def test_main_missing_arg(self, mocker: MockerFixture) -> None:
        """Tests that function properly detects if documentation is missing in cli args.

        Given: An invalid of system args
        Expect: Program exist with non-zero code
        """
        mocker.patch("tovald.main.argparse._sys.argv", ["tovald"])

        with pytest.raises(SystemExit) as system_exit:
            main()

        assert system_exit.value.code > 0
