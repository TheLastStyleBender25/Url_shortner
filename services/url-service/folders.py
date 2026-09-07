#!/usr/bin/env python3
"""
create_folders.py

Creates a set of folders inside a directory you specify.

USAGE:
    python create_folders.py "/path/to/base/directory"

If you don't pass a path as an argument, the script will ask you
to type one in when it runs.

CUSTOMIZE:
    Edit the FOLDER_NAMES list below to whatever folder names you want created.
"""

import os
import sys

# ---- Edit this list to control which folders get created ----
FOLDER_NAMES = ['models', 'api','repositories','schemas','core','db', 'dependencies','services','tasks', 'exceptions']
# ----------------------------------------------------------------


def get_base_directory() -> str:
    """Get the base directory from command-line args or user input."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    return input("Enter the path to the directory where folders should be created: ").strip()


def create_folders(base_dir: str, folder_names: list[str]) -> None:
    """Create each folder in folder_names inside base_dir."""
    base_dir = os.path.expanduser(base_dir)  # supports "~" for home dir

    if not os.path.exists(base_dir):
        print(f"Base directory does not exist. Creating it: {base_dir}")
        os.makedirs(base_dir, exist_ok=True)

    if not os.path.isdir(base_dir):
        print(f"Error: '{base_dir}' exists but is not a directory.")
        sys.exit(1)

    for name in folder_names:
        folder_path = os.path.join(base_dir, name)
        if os.path.exists(folder_path):
            print(f"Skipped (already exists): {folder_path}")
        else:
            os.makedirs(folder_path)
            print(f"Created: {folder_path}")


def main():
    base_dir = get_base_directory()
    if not base_dir:
        print("No directory provided. Exiting.")
        sys.exit(1)

    create_folders(base_dir, FOLDER_NAMES)
    print("\nDone.")


if __name__ == "__main__":
    main()