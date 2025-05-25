"""Command line interface for the findso package."""

import argparse
import logging
import multiprocessing
import time
from typing import List

from findso import __version__
from findso.core import SymbolFinder, scan_so_files


def process_chunk(args: tuple) -> List[str]:
    """Process a chunk of files in a worker process."""
    files, symbol, find_all, verbose = args
    finder = SymbolFinder(files, verbose=verbose)
    return finder.find_symbol(symbol, find_all=find_all)


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
                "# Use multiple jobs",
                "findso /usr/lib/x86_64-linux-gnu/ puts --jobs 4",
            ]
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"v{__version__}")
    parser.add_argument("so_dir", help="Directory containing .so files")
    parser.add_argument("symbol", help="Symbol name to search for")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--all", action="store_true", help="Find all matches (default: stop after first match)")
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="Number of parallel jobs to use (default: 1)",
    )
    args = parser.parse_args()

    start_time = time.time()

    # Set up logging
    logger = logging.getLogger("findso")
    logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - [%(processName)s] :: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Log the initial search message
    logger.info("Looking up %s", args.symbol)

    # Scan for .so files
    scan_start = time.time()
    so_files = scan_so_files(args.so_dir, logger)
    scan_time = time.time() - scan_start
    logger.debug("Scanned %d files in %.2f seconds", len(so_files), scan_time)

    if not so_files:
        logger.warning("No .so files found in %s", args.so_dir)
        return

    # Process files in parallel if requested
    if args.jobs > 1:
        # Split files into chunks for parallel processing
        # Use smaller chunks for better load balancing
        chunk_size = max(1, min(50, len(so_files) // (args.jobs * 2)))
        chunks = [so_files[i : i + chunk_size] for i in range(0, len(so_files), chunk_size)]

        logger.debug("Processing %d chunks with %d processes", len(chunks), args.jobs)

        # Process chunks in parallel
        with multiprocessing.Pool(processes=args.jobs) as pool:
            process_start = time.time()
            found_paths = []

            # Submit all chunks and collect results
            results = []
            for chunk in chunks:
                result = pool.apply_async(process_chunk, ((chunk, args.symbol, args.all, args.verbose),))
                results.append(result)

            # Collect results as they complete
            for result in results:
                chunk_result = result.get()
                if chunk_result:
                    found_paths.extend(chunk_result)
                    if not args.all and found_paths:
                        # Terminate the pool to stop remaining tasks
                        pool.terminate()
                        break

            # Wait for remaining processes
            pool.close()
            pool.join()

            process_time = time.time() - process_start
            logger.debug("Processed chunks in %.2f seconds", process_time)
    else:
        # Single-process processing
        process_start = time.time()
        finder = SymbolFinder(so_files, verbose=args.verbose)
        found_paths = finder.find_symbol(args.symbol, find_all=args.all)
        process_time = time.time() - process_start
        logger.debug("Processed files in %.2f seconds", process_time)

    total_time = time.time() - start_time
    logger.debug("Total execution time: %.2f seconds", total_time)

    # Print results
    if found_paths:
        for path in found_paths:
            logger.info("Found %s", path)
    else:
        logger.info("No matches found for %s in %s", args.symbol, args.so_dir)

    logger.info("Total matches: %d", len(found_paths))


if __name__ == "__main__":
    main()
