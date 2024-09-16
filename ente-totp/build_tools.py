#!/usr/bin/env python3

import sys
import plistlib

def get_workflow_name():
    """Get the workflow name from info.plist"""
    plist_path = 'info.plist'
    with open(plist_path, 'rb') as f:
        plist = plistlib.load(f)
    return plist['name']

def update_version(version):
    """Update the version in info.plist"""
    plist_path = 'info.plist'
    with open(plist_path, 'rb') as f:
        plist = plistlib.load(f)

    plist['version'] = version

    with open(plist_path, 'wb') as f:
        plistlib.dump(plist, f)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 update_version.py [--get-name | --set-version <version>]")
        sys.exit(1)

    if sys.argv[1] == '--get-name':
        workflow_name = get_workflow_name()
        print(workflow_name)
    elif sys.argv[1] == '--set-version':
        if len(sys.argv) != 3:
            print("Usage: python3 update_version.py --set-version <version>")
            sys.exit(1)
        version = sys.argv[2]
        update_version(version)
    else:
        print("Invalid option. Use --get-name or --set-version.")
        sys.exit(1)
