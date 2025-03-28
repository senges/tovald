"""Test suite for main module."""

import shutil
from filecmp import dircmp
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from tovald.main import (
    InvalidDocTreeError,
    build_sphinx_tree,
    cleanup,
    main,
    make_sphinx,
    panic,
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


class TestLogging:
    """Test suite for logging features."""

    def test_panic_sys_exit(self, mocker: MockerFixture) -> None:
        """Tests that panic properly exits program with error exit code."""
        exit_patch = mocker.patch("tovald.main.sys.exit")

        panic("")
        exit_patch.assert_called_once_with(1)

    def test_panic_print(self, mocker: MockerFixture) -> None:
        """Tests that panic yields error message."""
        error_message = "test_panic_print"
        mocker.patch("tovald.main.sys.exit")
        print_patch = mocker.patch("tovald.main.print")

        panic("test_panic_print")
        print_patch.assert_called_once_with(error_message)


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

        panic_patch.assert_called_once_with(f"Missing index in {invalid_path / 'level-1/level-2'}.")

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
            f"Multiple h1 headings found in {invalid_path / 'level-1/level-2/level-3'} index."
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


class TestMakeSphinx:
    """Test suite for make_sphinx function."""

    def test_make_sphinx_returns_sphinx_instance(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Tests that function returns a proper Sphinx instance.

        Given: A documentation path
        Expect: A Sphinx application instance with correct configurations
        """
        (tmp_path / "conf.py").write_text("master_doc = 'index'\n")

        sphinx_mock = mocker.patch("tovald.main.Sphinx")
        make_sphinx(tmp_path)

        sphinx_mock.assert_called_once_with(
            srcdir=tmp_path,
            confdir=tmp_path,
            doctreedir=tmp_path / "_doctree",
            outdir=tmp_path / "xml",
            buildername="confluence",
            freshenv=True,
        )


class TestCleanup:
    """Test suite for cleanup function."""

    def test_cleanup_no_child_pages(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Tests cleanup behavior when no child pages exist.

        Given: A documentation path with no child pages
        Expect: Function connects to Confluence and reports no pages found
        """
        (tmp_path / "conf.py").write_text("master_doc = 'index'\n")

        mock_sphinx = mocker.Mock()
        mock_publisher = mocker.Mock()

        mock_sphinx.builder.publisher = None
        mocker.patch("tovald.main.make_sphinx", return_value=mock_sphinx)
        mocker.patch("tovald.main.ConfluencePublisher", return_value=mock_publisher)
        mock_publisher.get_base_page_id.return_value = "parent-page-id"
        mock_publisher.get_descendants.return_value = []

        print_patch = mocker.patch("tovald.main.print")

        cleanup(tmp_path)

        mock_publisher.connect.assert_called_once()
        mock_publisher.get_base_page_id.assert_called_once()
        mock_publisher.get_descendants.assert_called_once_with("parent-page-id", "search-aggressive")
        mock_publisher.remove_page.assert_not_called()
        print_patch.assert_called_with("No child pages found to remove")

    def test_cleanup_with_child_pages(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Tests cleanup behavior when child pages exist.

        Given: A documentation path with child pages
        Expect: Function removes all child pages and reports success
        """
        (tmp_path / "conf.py").write_text("master_doc = 'index'\n")

        mock_sphinx = mocker.Mock()
        mock_publisher = mocker.Mock()
        child_pages = ["page-1", "page-2", "page-3"]

        mocker.patch("tovald.main.make_sphinx", return_value=mock_sphinx)
        mock_sphinx.builder.publisher = mock_publisher
        mock_publisher.get_base_page_id.return_value = "parent-page-id"
        mock_publisher.get_descendants.return_value = child_pages

        print_patch = mocker.patch("tovald.main.print")

        cleanup(tmp_path)

        mock_publisher.connect.assert_called_once()
        mock_publisher.get_base_page_id.assert_called_once()
        mock_publisher.get_descendants.assert_called_once_with("parent-page-id", "search-aggressive")
        assert mock_publisher.remove_page.call_count == len(child_pages)
        print_patch.assert_any_call(f"Removing {len(child_pages)} pages...")
        print_patch.assert_any_call("Cleanup completed successfully")

    def test_cleanup_no_parent_page(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Tests cleanup behavior when no parent page is configured.

        Given: A documentation path with no parent page configured
        Expect: Function panics with appropriate message
        """
        (tmp_path / "conf.py").write_text("master_doc = 'index'\n")

        mock_sphinx = mocker.Mock()
        mock_publisher = mocker.Mock()

        mocker.patch("tovald.main.make_sphinx", return_value=mock_sphinx)
        mock_sphinx.builder.publisher = mock_publisher
        mock_publisher.get_base_page_id.return_value = None

        panic_patch = mocker.patch("tovald.main.panic")
        panic_patch.side_effect = Exception("Halting execution")

        with pytest.raises(Exception, match="Halting execution"):
            cleanup(tmp_path)

        panic_patch.assert_called_once_with("No parent page configured or found")

    def test_cleanup_confluence_error(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Tests cleanup behavior when Confluence error occurs.

        Given: A documentation path where Confluence API raises an error
        Expect: Function panics with error message
        """
        (tmp_path / "conf.py").write_text("master_doc = 'index'\n")

        mock_sphinx = mocker.Mock()
        mock_publisher = mocker.Mock()
        error_message = "API connection failed"

        class TestConfluenceError(Exception):
            pass

        mocker.patch("tovald.main.make_sphinx", return_value=mock_sphinx)
        mocker.patch("tovald.main.ConfluenceError", TestConfluenceError)
        mock_sphinx.builder.publisher = mock_publisher

        mock_publisher.connect.side_effect = TestConfluenceError(error_message)

        panic_patch = mocker.patch("tovald.main.panic")

        cleanup(tmp_path)

        panic_patch.assert_called_once_with(f"Cleanup failed: {error_message}")


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
