"""Tests for video utilities."""

import pytest
from pathlib import Path
import tempfile
import os
from app.utils.video_utils import ensure_directory, clean_temp_files, get_output_path


def test_ensure_directory():
    """Test directory creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = os.path.join(tmpdir, "test", "nested", "dir")
        result = ensure_directory(test_dir)
        
        assert Path(test_dir).exists()
        assert Path(test_dir).is_dir()
        assert result == Path(test_dir)


def test_ensure_directory_exists():
    """Test directory creation when directory already exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create directory first
        test_dir = os.path.join(tmpdir, "existing")
        os.makedirs(test_dir)
        
        # Should not raise error
        result = ensure_directory(test_dir)
        assert Path(test_dir).exists()


def test_clean_temp_files():
    """Test cleaning temporary files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        file1 = os.path.join(tmpdir, "test1.txt")
        file2 = os.path.join(tmpdir, "test2.txt")
        
        Path(file1).touch()
        Path(file2).touch()
        
        assert Path(file1).exists()
        assert Path(file2).exists()
        
        clean_temp_files([file1, file2])
        
        assert not Path(file1).exists()
        assert not Path(file2).exists()


def test_clean_temp_files_nonexistent():
    """Test cleaning non-existent files (should not raise error)."""
    clean_temp_files(["/nonexistent/file.txt"])


def test_get_output_path():
    """Test getting output path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = get_output_path(tmpdir, "test.mp4")
        
        assert result == str(Path(tmpdir) / "test.mp4")
        assert Path(tmpdir).exists()  # Directory should be created


def test_get_output_path_no_create():
    """Test getting output path without creating directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = get_output_path(tmpdir, "test.mp4", ensure_exists=False)
        
        assert result == str(Path(tmpdir) / "test.mp4")

