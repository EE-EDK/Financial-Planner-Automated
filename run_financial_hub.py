#!/usr/bin/env python3
"""
Financial Hub Launcher
Wrapper script that ensures correct working directory before running build_all.py
Works with PyInstaller and prevents silent failures.
"""

import sys
import os
from pathlib import Path
import traceback

def main():
    try:
        # Get the directory where this script is located
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            script_dir = Path(sys.executable).parent
        else:
            # Running as normal Python script
            script_dir = Path(__file__).parent.absolute()

        print(f"Script directory: {script_dir}")
        print(f"Current working directory: {os.getcwd()}")

        # Detect if we're already inside financial_docs or at repository root
        if (script_dir / "build_all.py").exists():
            # We're inside financial_docs directory already
            print("Detected: Running from inside financial_docs directory")
            financial_docs = script_dir
            repo_root = script_dir.parent
        elif (script_dir / "financial_docs" / "build_all.py").exists():
            # We're at repository root
            print("Detected: Running from repository root")
            financial_docs = script_dir / "financial_docs"
            repo_root = script_dir
        else:
            print(f"ERROR: Cannot find build_all.py")
            print(f"Searched in:")
            print(f"  - {script_dir / 'build_all.py'}")
            print(f"  - {script_dir / 'financial_docs' / 'build_all.py'}")
            print(f"\nContents of {script_dir}:")
            for item in sorted(script_dir.iterdir()):
                print(f"  - {item.name}")
            input("Press Enter to exit...")
            return 1

        print(f"Repository root: {repo_root}")
        print(f"Financial docs: {financial_docs}")

        # Import and run build_all
        print("\nStarting Financial Hub Builder...")
        print("=" * 70)

        # Change to financial_docs directory for the build
        os.chdir(financial_docs)
        print(f"Working directory: {os.getcwd()}\n")

        # Add parent directory to path so we can import
        sys.path.insert(0, str(financial_docs.parent))

        # Import the module directly
        import importlib.util
        spec = importlib.util.spec_from_file_location("build_all", financial_docs / "build_all.py")
        build_all = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build_all)

        return build_all.main()

    except Exception as e:
        print("\n" + "=" * 70)
        print("FATAL ERROR:")
        print("=" * 70)
        print(traceback.format_exc())
        print("=" * 70)
        input("\nPress Enter to exit...")
        return 1

if __name__ == '__main__':
    exit_code = main()
    if exit_code != 0:
        input("\nBuild failed. Press Enter to exit...")
    sys.exit(exit_code)
