"""Core functionality for finding symbols in shared object files."""

import logging
import multiprocessing
import subprocess
import time
import typing
from posixpath import basename

from colorama import Fore, init
from elftools.common.exceptions import ELFError
from elftools.elf.dynamic import DynamicSection
from elftools.elf.elffile import ELFFile


def scan_so_files(so_dir: str, logger: logging.Logger) -> typing.List[str]:
    """Scan directory for .so files and return list of valid ELF files."""
    try:
        # Find all .so* files
        result = subprocess.run(
            ["find", so_dir, "-name", "*.so*"],
            capture_output=True,
            text=True,
            check=False,  # Don't raise on non-zero exit
        )
        if result.returncode != 0:
            logger.warning("%sDirectory %s not found or not accessible%s", Fore.YELLOW, so_dir, Fore.RESET)
            return []

        sofiles = result.stdout.splitlines()
        if not sofiles:
            return []

        # Filter to ELF files only
        elf_files = []
        for path in sofiles:
            try:
                result = subprocess.run(["file", path], capture_output=True, text=True, check=False)
                if "ELF" in result.stdout:
                    elf_files.append(path)
            except (subprocess.SubprocessError, IOError) as e:
                logger.warning("%sError checking file %s: %s%s", Fore.YELLOW, path, str(e), Fore.RESET)
                continue
        return elf_files
    except (subprocess.SubprocessError, IOError, PermissionError) as e:
        logger.error("%sError scanning directory: %s%s", Fore.RED, str(e), Fore.RESET)
        return []


class SymbolFinder:
    """A class to find exported symbols in shared object files."""

    def __init__(self, so_files: typing.List[str], verbose: bool = False, stop_flag: int = 0):
        """Initialize SymbolFinder with a list of .so files to search."""
        init()  # Initialize colorama
        self.logger = logging.getLogger(__class__.__name__)
        self.logger.setLevel(logging.INFO if verbose else logging.WARNING)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - [%(processName)s] :: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.so_files = so_files
        self.stop_flag = stop_flag
        self._log_lock = multiprocessing.Lock()

    def find_symbol(self, target_symbol: str, find_all: bool = False) -> typing.List[str]:
        """Search for a symbol in .so files, optionally finding all occurrences."""
        found_paths = []

        for path in self.so_files:
            # Check if we should stop
            if self.stop_flag:
                break

            try:
                with open(path, "rb") as f:
                    elffile = ELFFile(f)
                    # Find the dynamic section
                    dynamic_section = None
                    for section in elffile.iter_sections():
                        if isinstance(section, DynamicSection):
                            dynamic_section = section
                            break
                    if not dynamic_section:
                        continue  # No dynamic section, skip
                    # Now get the dynamic symbol table
                    dynsym = elffile.get_section_by_name(".dynsym")
                    if not dynsym:
                        continue

                    for symbol in dynsym.iter_symbols():
                        # Check if we should stop
                        if self.stop_flag:
                            break

                        is_defined = symbol["st_shndx"] != "SHN_UNDEF"
                        is_function = symbol["st_info"]["type"] == "STT_FUNC"
                        has_addr = symbol["st_value"] != 0
                        if symbol.name == target_symbol and is_defined and is_function and has_addr:
                            with self._log_lock:
                                self._success("Found %s in %s", target_symbol, path)
                            found_paths.append(path)
                            if not find_all:
                                self.stop_flag = 1
                                return found_paths
                            break

                    if not found_paths:
                        with self._log_lock:
                            self._info("No %s in %s", target_symbol, basename(path))
            except (ELFError, IOError) as e:
                with self._log_lock:
                    self._error("Error processing %s: %s", path, str(e))
                continue  # skip malformed files

        return found_paths

    def _success(self, message: str, *args) -> None:
        formatted_message = message % args
        self.logger.info("%s%s%s", Fore.GREEN, formatted_message, Fore.RESET)

    def _warn(self, message: str, *args) -> None:
        formatted_message = message % args
        self.logger.warning("%s%s%s", Fore.YELLOW, formatted_message, Fore.RESET)

    def _error(self, message: str, *args) -> None:
        formatted_message = message % args
        self.logger.error("%s%s%s", Fore.RED, formatted_message, Fore.RESET)

    def _info(self, message: str, *args) -> None:
        formatted_message = message % args
        self.logger.info(formatted_message)
