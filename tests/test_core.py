import os

from findso.core import SymbolFinder

# Known test directory and symbol that exists in multiple files
TEST_DIR = '/usr/lib/x86_64-linux-gnu/'
TEST_SYMBOL = 'puts'


def test_symbol_finder_initialization():
    finder = SymbolFinder(TEST_DIR)
    assert finder.so_dir == TEST_DIR
    assert isinstance(finder.sofiles, list)
    assert len(finder.sofiles) > 0


def test_find_symbol_default_behavior():
    finder = SymbolFinder(TEST_DIR)
    found_paths = finder.find_symbol(TEST_SYMBOL)
    assert isinstance(found_paths, list)
    assert len(found_paths) == 1  # Should only return first match
    assert os.path.exists(found_paths[0])
    assert '.so' in found_paths[0]  # Check for .so anywhere in the path


def test_find_symbol_find_all():
    finder = SymbolFinder(TEST_DIR)
    found_paths = finder.find_symbol(TEST_SYMBOL, find_all=True)
    assert isinstance(found_paths, list)
    assert len(found_paths) > 1  # Should return multiple matches
    for path in found_paths:
        assert os.path.exists(path)
        assert '.so' in path  # Check for .so anywhere in the path


def test_find_nonexistent_symbol():
    finder = SymbolFinder(TEST_DIR)
    found_paths = finder.find_symbol('nonexistent_symbol_12345')
    assert isinstance(found_paths, list)
    assert len(found_paths) == 0


def test_find_symbol_in_nonexistent_directory():
    finder = SymbolFinder('/nonexistent/directory/12345')
    found_paths = finder.find_symbol(TEST_SYMBOL)
    assert isinstance(found_paths, list)
    assert len(found_paths) == 0


def test_verbose_logging():
    finder = SymbolFinder(TEST_DIR, verbose=True)
    found_paths = finder.find_symbol(TEST_SYMBOL)
    assert isinstance(found_paths, list)
    assert len(found_paths) == 1


def test_find_symbol_with_invalid_so_file(tmp_path):
    # Create an invalid .so file
    invalid_so = tmp_path / "invalid.so"
    invalid_so.write_bytes(b"not a valid ELF file")

    finder = SymbolFinder(str(tmp_path))
    found_paths = finder.find_symbol(TEST_SYMBOL)
    assert isinstance(found_paths, list)
    assert len(found_paths) == 0
