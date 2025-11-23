#!/usr/bin/env python3
"""
Telar Demos Generator

Generates manifest.json from existing demo content files.
Reads metadata from demo-project.csv files.

Usage:
    python build.py --version 0.6.0 --manifest-only

Version: v0.1.0
"""

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Version
GENERATOR_VERSION = "0.1.0"

# Paths
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
DEMOS_DIR = REPO_ROOT / "demos"


def read_project_csv(csv_path):
    """Read demo-project.csv and return list of story metadata"""
    stories = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                order = row.get('order', '').strip()
                title = row.get('title', '').strip()
                subtitle = row.get('subtitle', '').strip()

                if order and title:  # Skip empty rows
                    stories.append({
                        'order': int(order),
                        'title': title,
                        'description': subtitle
                    })
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"  Warning: Error reading {csv_path}: {e}")
        return None

    return stories


def generate_manifest(version):
    """Generate manifest.json for a version by scanning existing files"""
    manifest = {
        "version": version,
        "generated": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "generator_version": GENERATOR_VERSION,
        "languages": {}
    }

    version_dir = DEMOS_DIR / f"v{version}"

    if not version_dir.exists():
        print(f"Error: Version directory does not exist: {version_dir}")
        sys.exit(1)

    warnings = []

    # Scan each language directory
    for lang_dir in sorted(version_dir.iterdir()):
        if not lang_dir.is_dir() or lang_dir.name.startswith('.'):
            continue
        if lang_dir.name == 'manifest.json':
            continue

        lang = lang_dir.name
        print(f"\nProcessing language: {lang}")

        lang_data = {
            "files": {},
            "stories": {},
            "glossary": []
        }
        lang_has_content = False

        # Check for required CSV files
        project_csv = lang_dir / "demo-project.csv"
        objects_csv = lang_dir / "demo-objects.csv"

        if project_csv.exists():
            lang_data["files"]["project"] = "demo-project.csv"
            lang_has_content = True
        else:
            warnings.append(f"[{lang}] Missing demo-project.csv")

        if objects_csv.exists():
            lang_data["files"]["objects"] = "demo-objects.csv"
        else:
            warnings.append(f"[{lang}] Missing demo-objects.csv")

        # Read story metadata from project CSV
        story_metadata = read_project_csv(project_csv) if project_csv.exists() else []

        # Find story CSVs
        story_csvs = sorted(lang_dir.glob("demo-story-*.csv"))
        if not story_csvs:
            warnings.append(f"[{lang}] No demo-story-*.csv files found")

        # Find story text folders
        texts_stories_dir = lang_dir / "texts" / "stories"
        if not texts_stories_dir.exists():
            warnings.append(f"[{lang}] Missing texts/stories/ directory")
        else:
            story_folders = sorted([d for d in texts_stories_dir.iterdir() if d.is_dir()])

            for idx, story_dir in enumerate(story_folders):
                demo_id = story_dir.name
                story_texts = [f.name for f in sorted(story_dir.glob("*.md"))]

                if not story_texts:
                    warnings.append(f"[{lang}] No markdown files in texts/stories/{demo_id}/")
                    continue

                # Get metadata from project CSV (by order)
                order = idx + 1
                metadata = next((s for s in story_metadata if s['order'] == order), None)

                if metadata:
                    title = metadata['title']
                    description = metadata['description']
                else:
                    warnings.append(f"[{lang}] No metadata in demo-project.csv for story order {order} ({demo_id})")
                    title = demo_id.replace("-", " ").title()
                    description = ""

                # Find corresponding story CSV
                story_csv_name = f"demo-story-{order}.csv"
                if not (lang_dir / story_csv_name).exists():
                    warnings.append(f"[{lang}] Missing {story_csv_name} for {demo_id}")
                    story_csv_name = None

                lang_data["stories"][demo_id] = {
                    "title": title,
                    "description": description,
                    "order": order,
                    "csv": story_csv_name,
                    "texts": story_texts
                }
                lang_has_content = True
                print(f"  Found story: {demo_id} ({len(story_texts)} text files)")

        # Find glossary files
        glossary_dir = lang_dir / "texts" / "glossary"
        if glossary_dir.exists():
            glossary_files = [f.name for f in sorted(glossary_dir.glob("*.md"))]
            lang_data["glossary"] = glossary_files
            if glossary_files:
                print(f"  Found {len(glossary_files)} glossary files")
        else:
            warnings.append(f"[{lang}] Missing texts/glossary/ directory")

        # Only add language if it has actual content
        if lang_has_content:
            manifest["languages"][lang] = lang_data
        else:
            warnings.append(f"[{lang}] No content found, skipping language")

    return manifest, warnings


def main():
    parser = argparse.ArgumentParser(
        description="Generate manifest.json for Telar demo content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python build.py --version 0.6.0 --manifest-only
        """
    )
    parser.add_argument("--version", "-v", required=True, help="Telar version (e.g., 0.6.0)")
    parser.add_argument("--manifest-only", action="store_true", help="Generate manifest from existing files")

    args = parser.parse_args()

    print(f"Telar Demos Generator v{GENERATOR_VERSION}")
    print(f"Processing v{args.version}")
    print("-" * 40)

    if not args.manifest_only:
        print("Error: Currently only --manifest-only is supported.")
        print("Add demo content manually, then run with --manifest-only to generate manifest.")
        sys.exit(1)

    version_dir = DEMOS_DIR / f"v{args.version}"

    # Generate manifest
    manifest, warnings = generate_manifest(args.version)

    # Report warnings
    if warnings:
        print("\n" + "=" * 40)
        print("WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
        print("=" * 40)

    # Check if we have any content
    if not manifest["languages"]:
        print("\nError: No valid language content found. Cannot generate manifest.")
        sys.exit(1)

    # Write manifest
    manifest_path = version_dir / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\nManifest written to {manifest_path}")
    print(f"Languages: {', '.join(manifest['languages'].keys())}")
    print("\nDone!")


if __name__ == "__main__":
    main()
