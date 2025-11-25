#!/usr/bin/env python3
"""
Telar Demos Generator

Generates demo content manifest and IIIF tiles for telar-demos repository.

Usage:
    python build-demos.py --version 0.6.0              # Generate both manifest and IIIF
    python build-demos.py --version 0.6.0 --manifest-only  # Just demo manifest
    python build-demos.py --iiif-only                  # Just IIIF tiles (no version needed)

Version: v0.2.0
"""

import argparse
import csv
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# Version
GENERATOR_VERSION = "0.2.0"

# Paths
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
DEMOS_DIR = REPO_ROOT / "demos"
IIIF_DIR = REPO_ROOT / "iiif"

# Default base URL for demos site
DEFAULT_BASE_URL = "https://content.telar.org"


# =============================================================================
# DEMO MANIFEST GENERATION
# =============================================================================

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


# =============================================================================
# IIIF GENERATION
# =============================================================================

def check_iiif_dependencies():
    """Check if required dependencies for IIIF generation are installed"""
    try:
        from iiif.static import IIIFStatic
        from PIL import Image, ImageOps
        return True
    except ImportError as e:
        print("Missing required dependencies for IIIF generation!")
        print("\nPlease install:")
        print("  pip install iiif Pillow")
        return False


def read_iiif_objects_csv():
    """Read iiif/all-demo-objects.csv and return list of objects with multilingual metadata"""
    csv_path = IIIF_DIR / "all-demo-objects.csv"
    objects = []

    if not csv_path.exists():
        print(f"Error: {csv_path} not found")
        return None

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                object_id = row.get('object_id', '').strip()
                if object_id:
                    objects.append({
                        'object_id': object_id,
                        'source_image': row.get('source_image', '').strip(),
                        'title_en': row.get('title_en', '').strip(),
                        'title_es': row.get('title_es', '').strip(),
                        'description_en': row.get('description_en', '').strip(),
                        'description_es': row.get('description_es', '').strip(),
                        'creator_en': row.get('creator_en', '').strip(),
                        'creator_es': row.get('creator_es', '').strip(),
                        'date_en': row.get('date_en', '').strip(),
                        'date_es': row.get('date_es', '').strip(),
                        'attribution_en': row.get('attribution_en', '').strip(),
                        'attribution_es': row.get('attribution_es', '').strip(),
                        'rights': row.get('rights', '').strip()
                    })
    except Exception as e:
        print(f"Error reading {csv_path}: {e}")
        return None

    return objects


def generate_iiif_for_image(image_path, output_dir, object_id, base_url):
    """Generate IIIF tiles for a single image"""
    from iiif.static import IIIFStatic
    from PIL import Image, ImageOps
    import tempfile

    # Preprocess image if needed
    processed_image_path = image_path
    temp_file = None

    try:
        img = Image.open(image_path)

        # Apply EXIF orientation if present
        img = ImageOps.exif_transpose(img) or img

        # Convert to RGB if needed
        converted_img = img
        needs_conversion = False

        if img.mode in ['RGBA', 'LA']:
            print(f"    Converting {img.mode} to RGB")
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1])
            converted_img = rgb_img
            needs_conversion = True
        elif img.mode == 'P':
            converted_img = img.convert('RGB')
            needs_conversion = True
        elif img.mode not in ['RGB', 'L']:
            converted_img = img.convert('RGB')
            needs_conversion = True

        # Convert to JPEG for IIIF processing
        file_ext = image_path.suffix.lower()
        if needs_conversion or file_ext not in ['.jpg', '.jpeg']:
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            converted_img.save(temp_file.name, 'JPEG', quality=95)
            processed_image_path = Path(temp_file.name)
            temp_file.close()

    except Exception as e:
        print(f"    Warning: Error preprocessing image: {e}")

    # Generate tiles
    parent_dir = output_dir.parent

    try:
        sg = IIIFStatic(
            dst=str(parent_dir),
            prefix=f"{base_url}/iiif/objects",
            tilesize=512,
            api_version='3.0'
        )
        sg.generate(src=str(processed_image_path), identifier=object_id)

        # Copy base image
        copy_base_image(processed_image_path, output_dir, object_id)

    finally:
        if temp_file and Path(temp_file.name).exists():
            Path(temp_file.name).unlink()


def copy_base_image(source_image_path, output_dir, object_id):
    """Copy full-resolution image for UniversalViewer"""
    from PIL import Image, ImageOps

    dest_path = output_dir / f"{object_id}.jpg"

    try:
        img = Image.open(source_image_path)
        img = ImageOps.exif_transpose(img) or img

        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                rgb_img.paste(img, mask=img.split()[-1])
            img = rgb_img

        img.save(dest_path, 'JPEG', quality=95)
        print(f"    Copied base image")
    except Exception as e:
        print(f"    Warning: Error copying base image: {e}")


def create_iiif_manifest(output_dir, object_id, metadata, base_url):
    """Create multilingual IIIF Presentation API manifest"""
    info_path = output_dir / 'info.json'
    if not info_path.exists():
        print(f"    Warning: info.json not found, skipping manifest")
        return

    with open(info_path, 'r') as f:
        info = json.load(f)

    width = info.get('width', 0)
    height = info.get('height', 0)

    # Build multilingual label
    label = {}
    if metadata.get('title_en'):
        label["en"] = [metadata['title_en']]
    if metadata.get('title_es'):
        label["es"] = [metadata['title_es']]
    if not label:
        label = {"en": [object_id]}

    manifest = {
        "@context": "http://iiif.io/api/presentation/3/context.json",
        "id": f"{base_url}/iiif/objects/{object_id}/manifest.json",
        "type": "Manifest",
        "label": label,
        "metadata": [],
        "items": [{
            "id": f"{base_url}/iiif/objects/{object_id}/canvas",
            "type": "Canvas",
            "label": label,
            "height": height,
            "width": width,
            "items": [{
                "id": f"{base_url}/iiif/objects/{object_id}/page",
                "type": "AnnotationPage",
                "items": [{
                    "id": f"{base_url}/iiif/objects/{object_id}/annotation",
                    "type": "Annotation",
                    "motivation": "painting",
                    "body": {
                        "id": f"{base_url}/iiif/objects/{object_id}/{object_id}.jpg",
                        "type": "Image",
                        "format": "image/jpeg",
                        "height": height,
                        "width": width,
                        "service": [{
                            "id": f"{base_url}/iiif/objects/{object_id}",
                            "type": "ImageService3",
                            "profile": "level0"
                        }]
                    },
                    "target": f"{base_url}/iiif/objects/{object_id}/canvas"
                }]
            }]
        }]
    }

    # Add multilingual summary if description exists
    summary = {}
    if metadata.get('description_en'):
        summary["en"] = [metadata['description_en']]
    if metadata.get('description_es'):
        summary["es"] = [metadata['description_es']]
    if summary:
        manifest["summary"] = summary

    # Add multilingual metadata fields
    if metadata.get('creator_en') or metadata.get('creator_es'):
        creator_value = {}
        if metadata.get('creator_en'):
            creator_value["en"] = [metadata['creator_en']]
        if metadata.get('creator_es'):
            creator_value["es"] = [metadata['creator_es']]
        manifest['metadata'].append({
            "label": {"en": ["Creator"], "es": ["Creador"]},
            "value": creator_value
        })

    if metadata.get('date_en') or metadata.get('date_es'):
        date_value = {}
        if metadata.get('date_en'):
            date_value["en"] = [metadata['date_en']]
        if metadata.get('date_es'):
            date_value["es"] = [metadata['date_es']]
        manifest['metadata'].append({
            "label": {"en": ["Date"], "es": ["Fecha"]},
            "value": date_value
        })

    if metadata.get('attribution_en') or metadata.get('attribution_es'):
        attr_value = {}
        if metadata.get('attribution_en'):
            attr_value["en"] = [metadata['attribution_en']]
        if metadata.get('attribution_es'):
            attr_value["es"] = [metadata['attribution_es']]
        manifest['metadata'].append({
            "label": {"en": ["Attribution"], "es": ["Atribución"]},
            "value": attr_value
        })

    manifest_path = output_dir / 'manifest.json'
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"    Created multilingual manifest.json")


def generate_iiif_tiles(base_url=None):
    """Generate IIIF tiles for all objects in iiif/all-demo-objects.csv"""
    if not check_iiif_dependencies():
        return False

    if not base_url:
        base_url = DEFAULT_BASE_URL

    sources_dir = IIIF_DIR / "sources"
    output_dir = IIIF_DIR / "objects"

    if not sources_dir.exists():
        print(f"Error: Source directory {sources_dir} does not exist")
        return False

    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("IIIF Tile Generator for telar-demos")
    print("=" * 60)
    print(f"Source: {sources_dir}")
    print(f"Output: {output_dir}")
    print(f"Base URL: {base_url}")
    print("=" * 60)
    print()

    # Read objects from CSV
    objects = read_iiif_objects_csv()
    if objects is None:
        return False

    if not objects:
        print("No objects found in iiif/objects.csv")
        return True

    print(f"Found {len(objects)} objects to process\n")

    processed = 0
    skipped = 0

    for i, obj in enumerate(objects, 1):
        object_id = obj['object_id']
        source_image = obj['source_image']

        print(f"[{i}/{len(objects)}] Processing {object_id}...")

        # Find source image
        image_path = IIIF_DIR / source_image
        if not image_path.exists():
            print(f"    Warning: Source image not found: {image_path}")
            skipped += 1
            continue

        print(f"    Found: {image_path.name}")

        # Output directory for this object
        object_output = output_dir / object_id

        try:
            # Remove existing output
            if object_output.exists():
                shutil.rmtree(object_output)
            object_output.mkdir(parents=True, exist_ok=True)

            # Generate tiles
            generate_iiif_for_image(image_path, object_output, object_id, base_url)

            # Create manifest with metadata
            create_iiif_manifest(object_output, object_id, obj, base_url)

            print(f"    Generated tiles for {object_id}")
            processed += 1

        except Exception as e:
            print(f"    Error: {e}")
            import traceback
            traceback.print_exc()
            skipped += 1

        print()

    print("=" * 60)
    print("IIIF generation complete!")
    print(f"  Processed: {processed} objects")
    if skipped > 0:
        print(f"  Skipped: {skipped} objects")
    print(f"  Output: {output_dir}")
    print("=" * 60)

    return True


# =============================================================================
# IIIF MANIFEST VALIDATION
# =============================================================================

def check_validation_dependencies():
    """Check if jsonschema is available"""
    try:
        import jsonschema
        return True
    except ImportError:
        print("Warning: jsonschema not installed. Skipping validation.")
        print("  Install with: pip install jsonschema")
        return False


def validate_iiif_manifest(manifest_path):
    """Validate a IIIF manifest against the Presentation API 3.0 schema"""
    import jsonschema

    schema_path = SCRIPT_DIR / "schemas" / "iiif_3_0.json"

    if not schema_path.exists():
        print(f"    Warning: Schema not found at {schema_path}")
        return None

    try:
        with open(schema_path, 'r') as f:
            schema = json.load(f)

        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        # The IIIF schema uses a custom structure with "classes" for validation
        # We need to validate against the Manifest class definition
        manifest_schema = schema.get("classes", {}).get("Manifest", {})

        if not manifest_schema:
            print("    Warning: Could not find Manifest schema definition")
            return None

        # Create a resolver for internal $ref references
        resolver = jsonschema.RefResolver.from_schema(schema)

        # Validate
        validator = jsonschema.Draft7Validator(manifest_schema, resolver=resolver)
        errors = list(validator.iter_errors(manifest))

        return errors

    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]
    except Exception as e:
        return [f"Validation error: {e}"]


def validate_all_iiif_manifests():
    """Validate all generated IIIF manifests"""
    if not check_validation_dependencies():
        return True  # Skip validation but don't fail

    objects_dir = IIIF_DIR / "objects"
    if not objects_dir.exists():
        print("No IIIF objects to validate")
        return True

    print("\n[IIIF Manifest Validation]")
    print("-" * 40)

    all_valid = True
    validated = 0
    failed = 0

    for object_dir in sorted(objects_dir.iterdir()):
        if not object_dir.is_dir():
            continue

        manifest_path = object_dir / "manifest.json"
        if not manifest_path.exists():
            continue

        object_id = object_dir.name
        errors = validate_iiif_manifest(manifest_path)

        if errors is None:
            print(f"  {object_id}: Skipped (schema issue)")
        elif len(errors) == 0:
            print(f"  {object_id}: Valid")
            validated += 1
        else:
            print(f"  {object_id}: INVALID ({len(errors)} errors)")
            for err in errors[:3]:  # Show first 3 errors
                if hasattr(err, 'message'):
                    print(f"    - {err.message}")
                else:
                    print(f"    - {err}")
            if len(errors) > 3:
                print(f"    ... and {len(errors) - 3} more errors")
            failed += 1
            all_valid = False

    print("-" * 40)
    print(f"Validated: {validated}, Failed: {failed}")

    return all_valid


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate manifest and IIIF tiles for Telar demo content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python build-demos.py --version 0.6.0              # Generate both
    python build-demos.py --version 0.6.0 --manifest-only  # Just manifest
    python build-demos.py --iiif-only                  # Just IIIF tiles
        """
    )
    parser.add_argument("--version", "-v", help="Telar version (e.g., 0.6.0)")
    parser.add_argument("--manifest-only", action="store_true", help="Generate only demo manifest")
    parser.add_argument("--iiif-only", action="store_true", help="Generate only IIIF tiles")
    parser.add_argument("--base-url", help=f"Base URL for IIIF (default: {DEFAULT_BASE_URL})")
    parser.add_argument("--skip-validation", action="store_true", help="Skip IIIF manifest validation")

    args = parser.parse_args()

    print(f"Telar Demos Generator v{GENERATOR_VERSION}")
    print("-" * 40)

    # Validate arguments
    if args.iiif_only and args.manifest_only:
        print("Error: Cannot use both --iiif-only and --manifest-only")
        sys.exit(1)

    if not args.iiif_only and not args.version:
        print("Error: --version is required unless using --iiif-only")
        sys.exit(1)

    success = True

    # Generate IIIF if not manifest-only
    if not args.manifest_only:
        print("\n[IIIF Generation]")
        if not generate_iiif_tiles(base_url=args.base_url):
            success = False

        # Validate IIIF manifests unless skipped
        if not args.skip_validation:
            if not validate_all_iiif_manifests():
                success = False

    # Generate manifest if not iiif-only
    if not args.iiif_only:
        print(f"\n[Manifest Generation for v{args.version}]")

        manifest, warnings = generate_manifest(args.version)

        if warnings:
            print("\n" + "=" * 40)
            print("WARNINGS:")
            for warning in warnings:
                print(f"  - {warning}")
            print("=" * 40)

        if not manifest["languages"]:
            print("\nError: No valid language content found.")
            success = False
        else:
            version_dir = DEMOS_DIR / f"v{args.version}"
            manifest_path = version_dir / "manifest.json"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)

            print(f"\nManifest written to {manifest_path}")
            print(f"Languages: {', '.join(manifest['languages'].keys())}")

    print("\nDone!")
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
