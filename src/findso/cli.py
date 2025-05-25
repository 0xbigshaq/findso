"""Command line interface for the findso package."""

import argparse

from findso.core import SymbolFinder


def main():
    """Parse command line arguments and search for symbols in .so files."""
    parser = argparse.ArgumentParser(
        description="Find exported symbols in .so files in a directory",
        epilog="\n".join(
            [
                "Examples:",
                "# Find first occurrence of a symbol",
                "findso /usr/lib/x86_64-linux-gnu/ puts",
                "# Find all occurrences of a symbol",
                "findso /usr/lib/x86_64-linux-gnu/ puts --all",
                "# Enable verbose logging",
                "findso /usr/lib/x86_64-linux-gnu/ puts --verbose",
                "# Find all occurrences with verbose logging",
                "findso /usr/lib/x86_64-linux-gnu/ puts --all --verbose",
            ]
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("so_dir", help="Directory containing .so files")
    parser.add_argument("symbol", help="Symbol name to search for")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--all", action="store_true", help="Find all matches (default: stop after first match)")
    args = parser.parse_args()
    finder = SymbolFinder(args.so_dir, verbose=args.verbose)
    found_paths = finder.find_symbol(args.symbol, find_all=args.all)
    if found_paths:
        for path in found_paths:
            print(f"[*] {path}")
    else:
        print(f"[!] No matches found for {args.symbol} in {args.so_dir}")


if __name__ == "__main__":
    main()
