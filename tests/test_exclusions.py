"""
Test suite for js-function-scanner exclusion patterns.

Run with: pytest tests/
"""

import pytest
import tempfile
import shutil
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from scan_js_functions import get_excluded_files, COMMON_EXCLUDES


@pytest.fixture
def test_project():
    """Create a temporary project structure for testing."""
    temp_dir = tempfile.mkdtemp()
    base_path = Path(temp_dir)

    # Create directories
    (base_path / "src").mkdir()
    (base_path / "src" / "utils").mkdir()
    (base_path / "node_modules").mkdir()
    (base_path / "dist").mkdir()
    (base_path / "test").mkdir()

    # Create .js files
    (base_path / "src" / "index.js").touch()
    (base_path / "src" / "utils" / "helper.js").touch()
    (base_path / "node_modules" / "pkg.js").touch()
    (base_path / "dist" / "bundle.js").touch()
    (base_path / "test" / "test.js").touch()
    (base_path / "app.js").touch()
    (base_path / "app.min.js").touch()

    yield base_path

    shutil.rmtree(temp_dir)


def test_no_exclusions(test_project):
    """Test with no exclusion patterns."""
    excluded = get_excluded_files(test_project, [])
    assert len(excluded) == 0


def test_exclude_node_modules(test_project):
    """Test excluding node_modules directory."""
    excluded = get_excluded_files(test_project, ["node_modules"])
    expected = {Path("node_modules/pkg.js")}
    assert excluded == expected


def test_exclude_dist(test_project):
    """Test excluding dist directory."""
    excluded = get_excluded_files(test_project, ["dist"])
    expected = {Path("dist/bundle.js")}
    assert excluded == expected


def test_exclude_min_files(test_project):
    """Test excluding .min.js files."""
    excluded = get_excluded_files(test_project, ["*.min.js"])
    expected = {Path("app.min.js")}
    assert excluded == expected


def test_exclude_test_directory_glob(test_project):
    """Test excluding test directory with glob pattern."""
    excluded = get_excluded_files(test_project, ["**/test/**"])
    expected = {Path("test/test.js")}
    assert excluded == expected


def test_multiple_exclusions(test_project):
    """Test multiple exclusion patterns."""
    excluded = get_excluded_files(test_project, ["node_modules", "*.min.js", "dist"])
    expected = {Path("node_modules/pkg.js"), Path("app.min.js"), Path("dist/bundle.js")}
    assert excluded == expected


def test_common_exclusions(test_project):
    """Test COMMON_EXCLUDES pattern set."""
    excluded = get_excluded_files(test_project, [], exclude_common=True)

    # COMMON_EXCLUDES includes: **/node_modules/**, **/dist/**, *.min.js
    assert Path("node_modules/pkg.js") in excluded
    assert Path("dist/bundle.js") in excluded
    assert Path("app.min.js") in excluded

    # These should not be excluded
    assert Path("src/index.js") not in excluded
    assert Path("src/utils/helper.js") not in excluded
    assert Path("test/test.js") not in excluded  # test/ is not in COMMON_EXCLUDES
    assert Path("app.js") not in excluded


def test_exclude_common_and_user_patterns(test_project):
    """Test combining --exclude-common with user --exclude patterns."""
    excluded = get_excluded_files(
        test_project, ["test"], exclude_common=True  # user adds test directory
    )

    # From COMMON_EXCLUDES
    assert Path("node_modules/pkg.js") in excluded
    assert Path("dist/bundle.js") in excluded
    assert Path("app.min.js") in excluded

    # From user pattern
    assert Path("test/test.js") in excluded

    # Should not be excluded
    assert Path("src/index.js") not in excluded
    assert Path("app.js") not in excluded


def test_pattern_with_trailing_slash(test_project):
    """Test pattern with trailing slash."""
    excluded = get_excluded_files(test_project, ["node_modules/"])
    expected = {Path("node_modules/pkg.js")}
    assert excluded == expected


def test_case_sensitivity(test_project):
    """Test case sensitivity on Windows vs Unix."""
    # Create a file with uppercase name
    (test_project / "Test.js").touch()

    excluded = get_excluded_files(test_project, ["test.js"])

    # On Windows, glob.glob is case-insensitive, so Test.js would match
    # On Unix, glob.glob is case-sensitive, so Test.js would not match
    # This test documents the behavior rather than asserting a specific result
    if Path("Test.js").match("test.js"):  # Check if filesystem is case-insensitive
        assert Path("Test.js") in excluded
    else:
        assert Path("Test.js") not in excluded
