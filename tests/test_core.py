"""Tests for the core SymbolFinder functionality."""

import os
import logging

from findso.core import SymbolFinder, scan_so_files

# Known test directory and symbol that exists in multiple files
TEST_DIR = "/usr/lib/x86_64-linux-gnu/"
TEST_SYMBOL = "puts"


def test_symbol_finder_initialization():
    """Test basic initialization of SymbolFinder."""
    so_files = scan_so_files(TEST_DIR, logging.getLogger(__name__))
    finder = SymbolFinder(so_files)
    assert isinstance(finder.so_files, list)
    assert len(finder.so_files) > 0


def test_find_symbol_default_behavior():
    """Test finding first occurrence of a symbol."""
    so_files = scan_so_files(TEST_DIR, logging.getLogger(__name__))
    finder = SymbolFinder(so_files)
    found_paths = finder.find_symbol(TEST_SYMBOL)
    assert isinstance(found_paths, list)
    assert len(found_paths) == 1  # Should only return first match
    assert os.path.exists(found_paths[0])
    assert ".so" in found_paths[0]  # Check for .so anywhere in the path


def test_find_symbol_find_all():
    """Test finding all occurrences of a symbol."""
    so_files = scan_so_files(TEST_DIR, logging.getLogger(__name__))
    finder = SymbolFinder(so_files)
    found_paths = finder.find_symbol(TEST_SYMBOL, find_all=True)
    assert isinstance(found_paths, list)
    assert len(found_paths) > 1  # Should return multiple matches
    for path in found_paths:
        assert os.path.exists(path)
        assert ".so" in path  # Check for .so anywhere in the path


def test_find_nonexistent_symbol():
    """Test searching for a non-existent symbol."""
    so_files = scan_so_files(TEST_DIR, logging.getLogger(__name__))
    finder = SymbolFinder(so_files)
    found_paths = finder.find_symbol("nonexistent_symbol_12345")
    assert isinstance(found_paths, list)
    assert len(found_paths) == 0


def test_find_symbol_in_nonexistent_directory():
    """Test searching in a non-existent directory."""
    so_files = scan_so_files("/nonexistent/directory/12345", logging.getLogger(__name__))
    finder = SymbolFinder(so_files)
    found_paths = finder.find_symbol(TEST_SYMBOL)
    assert isinstance(found_paths, list)
    assert len(found_paths) == 0


def test_verbose_logging():
    """Test verbose logging mode."""
    so_files = scan_so_files(TEST_DIR, logging.getLogger(__name__))
    finder = SymbolFinder(so_files, verbose=True)
    found_paths = finder.find_symbol(TEST_SYMBOL)
    assert isinstance(found_paths, list)
    assert len(found_paths) == 1


def test_find_symbol_with_invalid_so_file(tmp_path):
    """Test handling of invalid .so files."""
    # Create an invalid .so file
    invalid_so = tmp_path / "invalid.so"
    invalid_so.write_bytes(b"not a valid ELF file")

    so_files = scan_so_files(str(tmp_path), logging.getLogger(__name__))
    finder = SymbolFinder(so_files)
    found_paths = finder.find_symbol(TEST_SYMBOL)
    assert isinstance(found_paths, list)
    assert len(found_paths) == 0
