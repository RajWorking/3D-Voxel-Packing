#!/usr/bin/env python3
"""
Usage: python3 remove_object.py <name>

Removes a placed object from the workspace, allowing backtracking.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from common import load_objects, load_workspace, save_workspace, print_placement_summary


def main():
    if len(sys.argv) != 2:
        print("Usage: remove_object.py <name>")
        sys.exit(1)

    name = sys.argv[1]

    try:
        objects = load_objects()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    if name not in objects:
        print(f"ERROR: object '{name}' not found in objects.json")
        print(f"Available: {', '.join(sorted(objects.keys()))}")
        sys.exit(1)

    ws = load_workspace()

    if name not in ws["placed"]:
        print(f"ERROR: object '{name}' is not currently placed.")
        sys.exit(1)

    del ws["placed"][name]
    ws["unplaced"] = sorted(ws["unplaced"] + [name])
    save_workspace(ws)

    print(f"REMOVED {name}")
    print_placement_summary(ws)


if __name__ == "__main__":
    main()
