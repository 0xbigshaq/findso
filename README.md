# findso

Find exported symbols in .so files in a directory.

## Description

`findso` is a command-line tool designed to help reverse engineers and developers quickly locate shared library (.so) files that export specific symbols. This is particularly useful when:

- You're reverse engineering a binary and need to find which shared library contains a specific imported function
- You want to avoid manually checking each .so file in a directory
- You need to verify symbol availability across multiple shared libraries
- You're debugging dynamic linking issues

The tool recursively searches through all .so files in the specified directory and its subdirectories, making it easy to track down where specific symbols are exported from.

> [!NOTE]
> Currently, the tool only supports detecting exported methods/functions. Detection of const global variables is not yet supported.

## Requirements

This tool runs in a Linux environment (or WSL2 if you're on Windows) as it depends on nix commands like `file` and `find`.

## Installation (from source)

```bash
pip install .
```

## Usage

```bash
findso <dir_of_so_files> <name_of_export>
```

Example:

```bash
$ findso --all  --jobs 24 /usr/lib/x86_64-linux-gnu/ puts
2025-05-25 20:32:00,917 - findso - INFO - [MainProcess] :: Looking up puts
2025-05-25 20:32:04,871 - findso - INFO - [MainProcess] :: Found /usr/lib/x86_64-linux-gnu/libasan.so.8.0.0
2025-05-25 20:32:04,871 - findso - INFO - [MainProcess] :: Found /usr/lib/x86_64-linux-gnu/libtsan.so.2.0.0
2025-05-25 20:32:04,871 - findso - INFO - [MainProcess] :: Found /usr/lib/x86_64-linux-gnu/libasan.so.6.0.0
2025-05-25 20:32:04,871 - findso - INFO - [MainProcess] :: Found /usr/lib/x86_64-linux-gnu/libtsan.so.0.0.0
2025-05-25 20:32:04,871 - findso - INFO - [MainProcess] :: Found /usr/lib/x86_64-linux-gnu/libc.so.6
2025-05-25 20:32:04,871 - findso - INFO - [MainProcess] :: Total matches: 5
```
