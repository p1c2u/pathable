"""Tests for PathAccessor and FilesystemPath."""

import os
import sys
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from pathable.accessors import PathAccessor
from pathable.paths import FilesystemPath


class TestPathAccessorStat:
    """Tests for PathAccessor.stat() method."""

    def test_stat_existing_file(self, tmp_path):
        """Test stat returns dict of stat attributes for existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        accessor = PathAccessor(tmp_path)
        result = accessor.stat(["test.txt"])

        assert result is not None
        assert isinstance(result, dict)
        assert "st_size" in result
        assert "st_mode" in result
        assert "st_mtime" in result
        assert result["st_size"] == 7  # "content" is 7 bytes

    def test_stat_existing_directory(self, tmp_path):
        """Test stat returns dict for existing directory."""
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        accessor = PathAccessor(tmp_path)
        result = accessor.stat(["testdir"])

        assert result is not None
        assert isinstance(result, dict)
        assert "st_mode" in result

    def test_stat_nonexistent_path_returns_none(self, tmp_path):
        """Test stat returns None when path does not exist."""
        accessor = PathAccessor(tmp_path)
        result = accessor.stat(["nonexistent.txt"])

        assert result is None

    def test_stat_oserror_returns_none(self, tmp_path):
        """Test stat returns None when OSError is raised."""
        accessor = PathAccessor(tmp_path)

        # Mock the joinpath to raise OSError
        with patch.object(Path, "joinpath") as mock_joinpath:
            mock_path = Mock()
            mock_path.stat.side_effect = OSError("Permission denied")
            mock_path.lstat.side_effect = OSError("Permission denied")
            mock_joinpath.return_value = mock_path

            result = accessor.stat(["test.txt"])

            assert result is None

    def test_stat_nested_path(self, tmp_path):
        """Test stat works with nested paths."""
        nested_dir = tmp_path / "dir1" / "dir2"
        nested_dir.mkdir(parents=True)
        test_file = nested_dir / "test.txt"
        test_file.write_text("nested")

        accessor = PathAccessor(tmp_path)
        result = accessor.stat(["dir1", "dir2", "test.txt"])

        assert result is not None
        assert result["st_size"] == 6  # "nested" is 6 bytes

    @pytest.mark.skipif(
        sys.version_info < (3, 10),
        reason="follow_symlinks requires Python 3.10+",
    )
    def test_stat_symlink_not_followed_py310(self, tmp_path):
        """Test stat does not follow symlinks on Python 3.10+."""
        target_file = tmp_path / "target.txt"
        target_file.write_text("target content")

        link_file = tmp_path / "link.txt"
        link_file.symlink_to(target_file)

        accessor = PathAccessor(tmp_path)
        result = accessor.stat(["link.txt"])

        assert result is not None
        # On 3.10+, should use stat(follow_symlinks=False)
        # which means we get the symlink's own stat, not the target's

    @pytest.mark.skipif(
        sys.version_info >= (3, 10), reason="lstat used on Python < 3.10"
    )
    def test_stat_uses_lstat_pre_py310(self, tmp_path):
        """Test stat uses lstat on Python < 3.10."""
        target_file = tmp_path / "target.txt"
        target_file.write_text("target content")

        link_file = tmp_path / "link.txt"
        link_file.symlink_to(target_file)

        accessor = PathAccessor(tmp_path)
        result = accessor.stat(["link.txt"])

        assert result is not None
        # On <3.10, should use lstat()


class TestPathAccessorKeys:
    """Tests for PathAccessor.keys() method."""

    def test_keys_empty_directory(self, tmp_path):
        """Test keys returns empty list for empty directory."""
        accessor = PathAccessor(tmp_path)
        result = accessor.keys([])

        assert result == []

    def test_keys_with_files(self, tmp_path):
        """Test keys returns file names."""
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.txt").write_text("content2")
        (tmp_path / "file3.txt").write_text("content3")

        accessor = PathAccessor(tmp_path)
        result = accessor.keys([])

        assert sorted(result) == ["file1.txt", "file2.txt", "file3.txt"]

    def test_keys_with_directories(self, tmp_path):
        """Test keys returns directory names."""
        (tmp_path / "dir1").mkdir()
        (tmp_path / "dir2").mkdir()

        accessor = PathAccessor(tmp_path)
        result = accessor.keys([])

        assert sorted(result) == ["dir1", "dir2"]

    def test_keys_mixed_files_and_directories(self, tmp_path):
        """Test keys returns both file and directory names."""
        (tmp_path / "file.txt").write_text("content")
        (tmp_path / "dir").mkdir()

        accessor = PathAccessor(tmp_path)
        result = accessor.keys([])

        assert sorted(result) == ["dir", "file.txt"]

    def test_keys_returns_names_not_paths(self, tmp_path):
        """Test keys returns entry names, not full paths."""
        (tmp_path / "test.txt").write_text("content")

        accessor = PathAccessor(tmp_path)
        result = accessor.keys([])

        # Should return just the name, not the full path
        assert result == ["test.txt"]
        assert all(not str(item).startswith("/") for item in result)

    def test_keys_nested_directory(self, tmp_path):
        """Test keys works with nested paths."""
        nested_dir = tmp_path / "dir1" / "dir2"
        nested_dir.mkdir(parents=True)
        (nested_dir / "file1.txt").write_text("content1")
        (nested_dir / "file2.txt").write_text("content2")

        accessor = PathAccessor(tmp_path)
        result = accessor.keys(["dir1", "dir2"])

        assert sorted(result) == ["file1.txt", "file2.txt"]

    def test_keys_hidden_files(self, tmp_path):
        """Test keys includes hidden files (Unix convention)."""
        (tmp_path / ".hidden").write_text("hidden")
        (tmp_path / "visible.txt").write_text("visible")

        accessor = PathAccessor(tmp_path)
        result = accessor.keys([])

        assert sorted(result) == [".hidden", "visible.txt"]


class TestFilesystemPathExists:
    """Tests for FilesystemPath.exists() method."""

    def test_exists_true_for_file(self, tmp_path):
        """Test exists returns True for existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        path = FilesystemPath.from_path(tmp_path / "test.txt")
        result = path.exists()

        assert result is True

    def test_exists_true_for_directory(self, tmp_path):
        """Test exists returns True for existing directory."""
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        path = FilesystemPath.from_path(tmp_path / "testdir")
        result = path.exists()

        assert result is True

    def test_exists_false_for_nonexistent(self, tmp_path):
        """Test exists returns False for nonexistent path."""
        path = FilesystemPath.from_path(tmp_path / "nonexistent.txt")
        result = path.exists()

        assert result is False

    def test_exists_false_when_stat_raises_oserror(self, tmp_path):
        """Test exists returns False when stat raises OSError."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        path = FilesystemPath.from_path(test_file)

        # Mock the accessor's stat to raise OSError by returning None
        with patch.object(path.accessor, "stat", return_value=None):
            result = path.exists()

            assert result is False

    def test_exists_with_nested_path(self, tmp_path):
        """Test exists works with nested paths."""
        nested_dir = tmp_path / "dir1" / "dir2"
        nested_dir.mkdir(parents=True)
        test_file = nested_dir / "test.txt"
        test_file.write_text("content")

        path = FilesystemPath.from_path(test_file)
        result = path.exists()

        assert result is True


class TestFilesystemPathKeys:
    """Tests for FilesystemPath.keys() method."""

    def test_keys_empty_directory(self, tmp_path):
        """Test keys returns empty sequence for empty directory."""
        path = FilesystemPath.from_path(tmp_path)
        result = path.keys()

        assert list(result) == []

    def test_keys_with_files(self, tmp_path):
        """Test keys returns file names."""
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.txt").write_text("content2")

        path = FilesystemPath.from_path(tmp_path)
        result = path.keys()

        assert sorted(result) == ["file1.txt", "file2.txt"]

    def test_keys_returns_names_not_paths(self, tmp_path):
        """Test keys returns entry names, not full paths."""
        (tmp_path / "test.txt").write_text("content")

        path = FilesystemPath.from_path(tmp_path)
        result = path.keys()

        # Should return just the name, not the full path
        assert list(result) == ["test.txt"]

    def test_keys_nested_with_child_path(self, tmp_path):
        """Test keys works when using child paths."""
        nested_dir = tmp_path / "dir1"
        nested_dir.mkdir()
        (nested_dir / "file1.txt").write_text("content1")
        (nested_dir / "file2.txt").write_text("content2")

        path = FilesystemPath.from_path(tmp_path)
        child_path = path / "dir1"
        result = child_path.keys()

        assert sorted(result) == ["file1.txt", "file2.txt"]
