#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Archive Reorganization Script
Reorganizes Archive from current structure to:

Archive/
├── raw/              # Original files (PDFs, images, CSVs)
│   ├── statements/
│   ├── tax/
│   ├── receipts/
│   └── exports/      # Rocket Money exports
├── processed/        # JSON data (from data/)
└── snapshots/        # Monthly archives (already exists)

This is a ONE-TIME migration script.
"""

import shutil
import sys
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32' and sys.stdout is not None:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
ARCHIVE_DIR = BASE_DIR / "Archive"

def create_new_structure():
    """Create new directory structure"""

    new_dirs = [
        ARCHIVE_DIR / "raw" / "statements",
        ARCHIVE_DIR / "raw" / "tax",
        ARCHIVE_DIR / "raw" / "receipts",
        ARCHIVE_DIR / "raw" / "exports",
        ARCHIVE_DIR / "processed"
    ]

    for dir_path in new_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created {dir_path.relative_to(BASE_DIR)}")

def migrate_files():
    """Migrate files to new structure"""

    migrations = []

    # Move data/ → processed/
    data_dir = ARCHIVE_DIR / "data"
    processed_dir = ARCHIVE_DIR / "processed"

    if data_dir.exists():
        for file in data_dir.glob("*.json"):
            dest = processed_dir / file.name
            migrations.append((file, dest, "JSON data"))

        for file in data_dir.glob("*.csv"):
            dest = ARCHIVE_DIR / "raw" / "exports" / file.name
            migrations.append((file, dest, "CSV export"))

    # Move tax/ → raw/tax/
    tax_dir = ARCHIVE_DIR / "tax"
    raw_tax_dir = ARCHIVE_DIR / "raw" / "tax"

    if tax_dir.exists():
        for file in tax_dir.rglob("*"):
            if file.is_file():
                rel_path = file.relative_to(tax_dir)
                dest = raw_tax_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                migrations.append((file, dest, "Tax document"))

    # Move property/ → raw/receipts/
    property_dir = ARCHIVE_DIR / "property"
    raw_receipts_dir = ARCHIVE_DIR / "raw" / "receipts"

    if property_dir.exists():
        for file in property_dir.rglob("*"):
            if file.is_file():
                rel_path = file.relative_to(property_dir)
                dest = raw_receipts_dir / "property" / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                migrations.append((file, dest, "Property document"))

    # Move screenshots/ → raw/screenshots/
    screenshots_dir = ARCHIVE_DIR / "screenshots"
    raw_screenshots_dir = ARCHIVE_DIR / "raw" / "screenshots"

    if screenshots_dir.exists():
        for file in screenshots_dir.rglob("*"):
            if file.is_file():
                rel_path = file.relative_to(screenshots_dir)
                dest = raw_screenshots_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                migrations.append((file, dest, "Screenshot"))

    return migrations

def preview_migrations(migrations):
    """Preview what will be migrated"""

    print()
    print("📋 Migration Preview:")
    print()

    for source, dest, file_type in migrations[:10]:
        print(f"  {file_type}:")
        print(f"    From: {source.relative_to(BASE_DIR)}")
        print(f"    To:   {dest.relative_to(BASE_DIR)}")
        print()

    if len(migrations) > 10:
        print(f"  ... and {len(migrations) - 10} more files")
        print()

def execute_migrations(migrations):
    """Execute the migrations"""

    for source, dest, file_type in migrations:
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            print(f"  ✅ Migrated: {source.name}")
        except Exception as e:
            print(f"  ❌ Failed: {source.name} - {e}")

def main():
    """Reorganize Archive"""

    print()
    print("=" * 70)
    print("📁 ARCHIVE REORGANIZATION")
    print("=" * 70)
    print()

    print("⚠️  WARNING: This will reorganize your Archive directory.")
    print("   Original files will be COPIED (not moved) for safety.")
    print()

    # Create new structure
    print("Creating new directory structure...")
    create_new_structure()
    print()

    # Plan migrations
    print("Scanning for files to migrate...")
    migrations = migrate_files()
    print(f"  ✅ Found {len(migrations)} files to migrate")
    print()

    # Preview
    preview_migrations(migrations)

    # Confirm
    response = input("Proceed with migration? (yes/no): ").strip().lower()

    if response != 'yes':
        print()
        print("❌ Migration cancelled")
        print()
        return

    print()
    print("Executing migration...")
    execute_migrations(migrations)
    print()

    print("=" * 70)
    print("✅ MIGRATION COMPLETE")
    print("=" * 70)
    print()
    print("📁 New structure:")
    print("   Archive/raw/       - Original files")
    print("   Archive/processed/ - JSON data")
    print("   Archive/snapshots/ - Monthly snapshots")
    print()
    print("⚠️  NEXT STEPS:")
    print("   1. Verify files migrated correctly")
    print("   2. Update script paths if needed")
    print("   3. Delete old directories (data/, tax/, property/, screenshots/)")
    print()

if __name__ == '__main__':
    main()
