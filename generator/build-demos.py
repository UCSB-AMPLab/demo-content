#!/usr/bin/env python3
"""
Telar Demos Generator

Generates demo content bundles and IIIF tiles for telar-demo-content repository.

Usage:
    python build-demos.py --version 0.6.0              # Generate both bundle and IIIF
    python build-demos.py --version 0.6.0 --bundle-only  # Just demo bundle
    python build-demos.py --iiif-only                  # Just IIIF tiles (no version needed)

Version: v0.3.0
"""

import argparse
import csv
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("Warning: markdown library not installed. Content will not be converted to HTML.")
    print("  Install with: pip install markdown")

# Version
GENERATOR_VERSION = "0.3.0"
BUNDLE_FORMAT_VERSION = "0.1"

# Paths
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
DEMOS_DIR = REPO_ROOT / "demos"
IIIF_DIR = REPO_ROOT / "iiif"

# Default base URL for demos site
DEFAULT_BASE_URL = "https://content.telar.org"


# =============================================================================
# DEMO BUNDLE GENERATION
# =============================================================================

def strip_yaml_frontmatter(content):
    """
    Strip YAML frontmatter from markdown content.

    Frontmatter is delimited by --- at the start and end.
    Returns the content without the frontmatter block.
    """
    content = content.strip()
    if not content.startswith('---'):
        return content

    # Find the closing ---
    lines = content.split('\n')
    end_index = None
    for i, line in enumerate(lines[1:], 1):  # Start from second line
        if line.strip() == '---':
            end_index = i
            break

    if end_index is None:
        # No closing ---, return as-is
        return content

    # Return content after the frontmatter
    return '\n'.join(lines[end_index + 1:]).strip()


def process_glossary_links(text, glossary_terms):
    """
    Transform [[term_id|display]] or [[term_id]] syntax into glossary link HTML.

    Args:
        text: HTML text to process (already converted from markdown)
        glossary_terms: Dictionary mapping term_id to term title

    Returns:
        str: Text with glossary links transformed to HTML
    """
    if not text or not glossary_terms:
        return text

    # Pattern: [[display|term]] or [[term]] with flexible spacing
    pattern = r'\[\[\s*([^|\]]+?)(?:\s*\|\s*([^|\]]+?))?\s*\]\]'

    def replace_glossary_link(match):
        # If pipe is present: [[term_id|display]], else [[term_id]]
        if match.group(2):  # Has pipe
            term_id = match.group(1).strip()
            display_text = match.group(2).strip()
        else:  # No pipe
            term_id = match.group(1).strip()
            # Use glossary title as display text
            display_text = glossary_terms.get(term_id, term_id)

        # Check if term exists in glossary
        if term_id in glossary_terms:
            # Valid term - create link
            return f'<a href="#" class="glossary-inline-link" data-term-id="{term_id}">{display_text}</a>'
        else:
            # Unknown term - still create link (may be valid in consuming site)
            return f'<a href="#" class="glossary-inline-link" data-term-id="{term_id}">{display_text}</a>'

    return re.sub(pattern, replace_glossary_link, text)


def convert_markdown_to_html(content, glossary_terms=None):
    """
    Convert markdown content to HTML with glossary link processing.

    Args:
        content: Raw markdown content
        glossary_terms: Optional dictionary of glossary terms for link processing

    Returns:
        str: HTML content with processed glossary links
    """
    if not content:
        return content

    if not MARKDOWN_AVAILABLE:
        # Fallback: just process glossary links in raw text
        if glossary_terms:
            return process_glossary_links(content, glossary_terms)
        return content

    # Convert markdown to HTML using same extensions as Telar
    html = markdown.markdown(content, extensions=['extra', 'nl2br'])

    # Process glossary links
    if glossary_terms:
        html = process_glossary_links(html, glossary_terms)

    return html


def read_project_csv(csv_path):
    """Read demo-project.csv and return list of project entries"""
    projects = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                order = row.get('order', '').strip()
                project_id = row.get('project_id', '').strip()
                title = row.get('title', '').strip()
                subtitle = row.get('subtitle', '').strip()
                byline = row.get('byline', '').strip()

                if order and title and project_id:  # Skip empty rows
                    projects.append({
                        'order': int(order),
                        'project_id': project_id,
                        'title': title,
                        'subtitle': subtitle,
                        'byline': byline
                    })
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"  Warning: Error reading {csv_path}: {e}")
        return None

    return projects


def get_self_hosted_object_ids():
    """Get set of object_ids that have self-hosted IIIF tiles"""
    csv_path = IIIF_DIR / "all-demo-objects.csv"
    object_ids = set()

    if not csv_path.exists():
        return object_ids

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                object_id = row.get('object_id', '').strip()
                if object_id:
                    object_ids.add(object_id)
    except Exception:
        pass

    return object_ids


def read_objects_csv(csv_path, base_url):
    """
    Read demo-objects.csv and return dict of objects keyed by object_id.

    Auto-populates source_url for self-hosted IIIF objects.
    """
    objects = {}
    self_hosted = get_self_hosted_object_ids()

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                object_id = row.get('object_id', '').strip()
                if not object_id:
                    continue

                obj = {}
                # Add non-empty fields
                for field in ['title', 'description', 'source_url', 'creator',
                              'period', 'medium', 'dimensions', 'location',
                              'credit', 'thumbnail']:
                    value = row.get(field, '').strip()
                    if value:
                        obj[field] = value

                # Auto-populate source_url and thumbnail for self-hosted objects
                if object_id in self_hosted:
                    if not obj.get('source_url'):
                        obj['source_url'] = f"{base_url}/iiif/objects/{object_id}/manifest.json"

                    # Auto-populate thumbnail from info.json sizes
                    if not obj.get('thumbnail'):
                        info_path = IIIF_DIR / "objects" / object_id / "info.json"
                        if info_path.exists():
                            try:
                                with open(info_path, 'r') as f:
                                    info = json.load(f)
                                sizes = info.get('sizes', [])
                                if sizes:
                                    # Use largest available size (first in array)
                                    largest = sizes[0]
                                    obj['thumbnail'] = f"{base_url}/iiif/objects/{object_id}/full/{largest['width']},/0/default.jpg"
                            except Exception as e:
                                print(f"  Warning: Could not read info.json for {object_id}: {e}")

                objects[object_id] = obj
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"  Warning: Error reading {csv_path}: {e}")
        return None

    return objects


def read_story_csv(csv_path, texts_dir, glossary_terms=None):
    """
    Read a story CSV and return list of steps with embedded layer content.

    Args:
        csv_path: Path to the story CSV file
        texts_dir: Path to the texts/stories/{project_id}/ directory
        glossary_terms: Optional dictionary of term_id -> title for glossary link processing

    Returns:
        List of step dicts with layers containing HTML content (converted from markdown)
    """
    steps = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                step_num = row.get('step', '').strip()
                if not step_num:
                    continue

                step = {
                    'step': int(step_num),
                    'object': row.get('object', '').strip(),
                    'x': float(row.get('x', '0.5').strip() or '0.5'),
                    'y': float(row.get('y', '0.5').strip() or '0.5'),
                    'zoom': float(row.get('zoom', '1').strip() or '1'),
                }

                # Add question/answer if present
                question = row.get('question', '').strip()
                answer = row.get('answer', '').strip()
                if question:
                    step['question'] = question
                if answer:
                    step['answer'] = answer

                # Process layers (layer1, layer2)
                layers = {}
                for i in [1, 2]:
                    button = row.get(f'layer{i}_button', '').strip()
                    file_name = row.get(f'layer{i}_file', '').strip()

                    if button and file_name:
                        # Read the markdown file
                        md_path = texts_dir / file_name
                        content = ""
                        if md_path.exists():
                            with open(md_path, 'r', encoding='utf-8') as md_file:
                                raw_content = md_file.read().strip()
                                # Strip YAML frontmatter
                                md_content = strip_yaml_frontmatter(raw_content)
                                # Convert markdown to HTML with glossary links
                                content = convert_markdown_to_html(md_content, glossary_terms)
                        else:
                            print(f"    Warning: Layer file not found: {md_path}")

                        layers[f'layer{i}'] = {
                            'button': button,
                            'content': content
                        }

                if layers:
                    step['layers'] = layers

                steps.append(step)

    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"  Warning: Error reading {csv_path}: {e}")
        return None

    return steps


def read_glossary_files(glossary_dir):
    """
    Read all glossary markdown files and return dict keyed by term slug.

    Glossary files have YAML front matter with term_id and title,
    followed by markdown content.
    """
    glossary = {}

    if not glossary_dir.exists():
        return glossary

    for md_file in sorted(glossary_dir.glob("*.md")):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse YAML front matter
            term_id = md_file.stem  # Default to filename without extension
            title = term_id.replace('-', ' ').title()
            body = content

            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    front_matter = parts[1]
                    body = parts[2].strip()

                    # Extract term_id
                    term_match = re.search(r'^term_id:\s*(.+)$', front_matter, re.MULTILINE)
                    if term_match:
                        term_id = term_match.group(1).strip().strip('"\'')

                    # Extract title
                    title_match = re.search(r'^title:\s*(.+)$', front_matter, re.MULTILINE)
                    if title_match:
                        title = title_match.group(1).strip().strip('"\'')

            # Convert markdown body to HTML
            html_content = convert_markdown_to_html(body)

            glossary[term_id] = {
                'term': title,
                'content': html_content
            }

        except Exception as e:
            print(f"    Warning: Error reading glossary file {md_file}: {e}")

    return glossary


def generate_bundle(version, lang, lang_dir, base_url):
    """
    Generate a complete telar-demo-bundle.json for a single language.

    Args:
        version: Telar version string (e.g., "0.6.0")
        lang: Language code (e.g., "en", "es")
        lang_dir: Path to the language directory
        base_url: Base URL for IIIF content

    Returns:
        Tuple of (bundle_dict, warnings_list)
    """
    warnings = []

    bundle = {
        "_meta": {
            "bundle_format": BUNDLE_FORMAT_VERSION,
            "telar_version": version,
            "language": lang,
            "generated": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "generator": f"telar-demo-content/build-demos.py v{GENERATOR_VERSION}",
            "source": "https://github.com/UCSB-AMPLab/telar-demo-content",
            "description": "Demo content bundle for Telar storytelling framework",
            "license": "CC BY-NC 4.0"
        },
        "iiif_base_url": f"{base_url}/iiif/objects",
        "project": [],
        "objects": {},
        "stories": {},
        "glossary": {}
    }

    print(f"\nProcessing language: {lang}")

    # Read project CSV
    project_csv = lang_dir / "demo-project.csv"
    if project_csv.exists():
        projects = read_project_csv(project_csv)
        if projects:
            bundle["project"] = projects
            print(f"  Found {len(projects)} project entries")
    else:
        warnings.append(f"[{lang}] Missing demo-project.csv")

    # Read objects CSV
    objects_csv = lang_dir / "demo-objects.csv"
    if objects_csv.exists():
        objects = read_objects_csv(objects_csv, base_url)
        if objects:
            bundle["objects"] = objects
            print(f"  Found {len(objects)} objects")
    else:
        warnings.append(f"[{lang}] Missing demo-objects.csv")

    # Read glossary FIRST (needed for processing story content)
    glossary_dir = lang_dir / "texts" / "glossary"
    glossary = {}
    glossary_terms = {}  # term_id -> title mapping for link processing
    if glossary_dir.exists():
        glossary = read_glossary_files(glossary_dir)
        if glossary:
            bundle["glossary"] = glossary
            # Build term_id -> title mapping
            glossary_terms = {term_id: data['term'] for term_id, data in glossary.items()}
            print(f"  Found {len(glossary)} glossary entries")
    else:
        warnings.append(f"[{lang}] Missing texts/glossary/ directory")

    # Read stories (with glossary terms for link processing)
    texts_stories_dir = lang_dir / "texts" / "stories"
    if not texts_stories_dir.exists():
        warnings.append(f"[{lang}] Missing texts/stories/ directory")
    else:
        for project in bundle["project"]:
            project_id = project['project_id']

            # Find story CSV
            story_csv = lang_dir / f"{project_id}.csv"
            if not story_csv.exists():
                warnings.append(f"[{lang}] Missing {project_id}.csv")
                continue

            # Find texts directory for this story
            story_texts_dir = texts_stories_dir / project_id
            if not story_texts_dir.exists():
                warnings.append(f"[{lang}] Missing texts/stories/{project_id}/ directory")
                story_texts_dir = texts_stories_dir  # Fall back to parent

            # Read story steps with embedded layer content
            steps = read_story_csv(story_csv, story_texts_dir, glossary_terms)
            if steps:
                bundle["stories"][project_id] = {"steps": steps}
                print(f"  Story '{project_id}': {len(steps)} steps")

    return bundle, warnings


def validate_bundle(bundle, lang):
    """
    Validate generated bundle for common CSV parsing issues.

    Returns list of validation warnings.
    """
    warnings = []

    # Patterns that suggest CSV parsing errors (field got shifted)
    suspicious_bylines = ['navigation', 'glossary', 'widgets', 'linking']
    suspicious_buttons = ['md', '.md', 'true', 'false']

    # Validate project entries
    for proj in bundle.get("project", []):
        project_id = proj.get("project_id", "unknown")

        # Check for suspiciously short subtitle (might be truncated)
        subtitle = proj.get("subtitle", "")
        if subtitle and len(subtitle) < 20 and ',' not in subtitle:
            # Short subtitle without commas might be truncated
            byline = proj.get("byline", "")
            if byline.lower() in suspicious_bylines:
                warnings.append(
                    f"[{lang}] CSV PARSE ERROR in project '{project_id}': "
                    f"byline='{byline}' looks like part of subtitle. "
                    f"Check if subtitle field needs quotes."
                )

        # Check byline format
        byline = proj.get("byline", "")
        if byline and not byline.startswith("by") and byline.lower() in suspicious_bylines:
            warnings.append(
                f"[{lang}] CSV PARSE ERROR in project '{project_id}': "
                f"byline='{byline}' looks like part of subtitle got shifted. "
                f"Add quotes around subtitle field in demo-project.csv"
            )

    # Validate stories
    for story_id, story in bundle.get("stories", {}).items():
        for step in story.get("steps", []):
            step_num = step.get("step", "?")

            # Check for empty layer content when button is defined
            for layer_key in ["layer1", "layer2"]:
                layer = step.get("layers", {}).get(layer_key, {})
                if layer:
                    button = layer.get("button", "")
                    content = layer.get("content", "")

                    if button and not content:
                        warnings.append(
                            f"[{lang}] Empty layer content in '{story_id}' step {step_num}: "
                            f"button='{button}' but no content loaded"
                        )

                    # Check for suspicious button names (might be file extension)
                    if button.lower() in suspicious_buttons or button.endswith('.md'):
                        warnings.append(
                            f"[{lang}] CSV PARSE ERROR in '{story_id}' step {step_num}: "
                            f"button='{button}' looks like a filename. "
                            f"Check if answer field needs quotes."
                        )

            # Check for suspiciously short answers that might be truncated
            answer = step.get("answer", "")
            if answer and len(answer) < 30:
                # Very short answers after a question might indicate truncation
                question = step.get("question", "")
                if question and len(question) > len(answer) * 2:
                    # Question much longer than answer is suspicious
                    pass  # Could add warning but might have false positives

    # Validate objects
    for obj_id, obj in bundle.get("objects", {}).items():
        # Check for missing source_url
        if not obj.get("source_url"):
            warnings.append(
                f"[{lang}] Object '{obj_id}' missing source_url"
            )

    return warnings


def generate_bundles_for_version(version, base_url=None):
    """
    Generate telar-demo-bundle.json for all languages in a version.

    Args:
        version: Telar version string (e.g., "0.6.0")
        base_url: Base URL for IIIF content

    Returns:
        Tuple of (success_bool, all_warnings_list)
    """
    if not base_url:
        base_url = DEFAULT_BASE_URL

    version_dir = DEMOS_DIR / f"v{version}"

    if not version_dir.exists():
        print(f"Error: Version directory does not exist: {version_dir}")
        sys.exit(1)

    all_warnings = []
    bundles_generated = 0

    # Scan each language directory
    for lang_dir in sorted(version_dir.iterdir()):
        if not lang_dir.is_dir() or lang_dir.name.startswith('.'):
            continue
        # Skip non-language directories
        if lang_dir.name in ['manifest.json', 'telar-demo-bundle.json']:
            continue

        lang = lang_dir.name

        # Generate bundle for this language
        bundle, warnings = generate_bundle(version, lang, lang_dir, base_url)
        all_warnings.extend(warnings)

        # Validate bundle for common issues
        validation_warnings = validate_bundle(bundle, lang)
        all_warnings.extend(validation_warnings)

        # Check if bundle has content
        if not bundle["project"] and not bundle["objects"]:
            all_warnings.append(f"[{lang}] No content found, skipping language")
            continue

        # Write bundle file
        bundle_path = lang_dir / "telar-demo-bundle.json"
        with open(bundle_path, 'w', encoding='utf-8') as f:
            json.dump(bundle, f, indent=2, ensure_ascii=False)

        print(f"  Written: {bundle_path}")
        bundles_generated += 1

    return bundles_generated > 0, all_warnings


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


def generate_iiif_tiles(base_url=None, force=False):
    """
    Generate IIIF tiles for all objects in iiif/all-demo-objects.csv

    By default, skips objects that already have tiles (info.json exists).
    Use force=True to regenerate all tiles.
    """
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

        # Check if already generated (skip unless --force)
        info_json = object_output / "info.json"
        if info_json.exists() and not force:
            print(f"    Skipping (already exists, use --force to regenerate)")
            skipped += 1
            continue

        try:
            # Remove existing output if regenerating
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
# VERSIONS INDEX GENERATION
# =============================================================================

def generate_versions_index():
    """
    Generate demos/versions.json by scanning existing version directories.

    Scans the demos/ directory for version folders (v0.6.0, v0.7.0, etc.)
    and writes a versions.json index file.

    Returns:
        bool: True if successful, False otherwise
    """
    if not DEMOS_DIR.exists():
        print("Warning: demos/ directory does not exist")
        return False

    # Find all version directories (v0.6.0, v0.7.0, etc.)
    version_dirs = []
    for item in DEMOS_DIR.iterdir():
        if item.is_dir() and item.name.startswith('v'):
            # Extract version number (remove 'v' prefix)
            version_str = item.name[1:]
            # Validate it's a proper version (has at least one bundle file)
            has_bundle = any(
                (item / lang / 'telar-demo-bundle.json').exists()
                for lang in ['en', 'es']
                if (item / lang).exists()
            )
            if has_bundle:
                version_dirs.append(version_str)

    if not version_dirs:
        print("Warning: No version directories found in demos/")
        return False

    # Sort versions semantically
    def parse_version(v):
        try:
            parts = v.split('.')
            return tuple(int(p) for p in parts)
        except ValueError:
            return (0, 0, 0)

    version_dirs.sort(key=parse_version)

    # Write versions.json
    versions_data = {"versions": version_dirs}
    versions_path = DEMOS_DIR / "versions.json"

    with open(versions_path, 'w', encoding='utf-8') as f:
        json.dump(versions_data, f, indent=2, ensure_ascii=False)

    print(f"\n[Versions Index]")
    print(f"  Versions found: {', '.join(version_dirs)}")
    print(f"  Written to: {versions_path}")

    return True


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate demo bundles and IIIF tiles for Telar demo content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python build-demos.py --version 0.6.0              # Generate both bundle and IIIF
    python build-demos.py --version 0.6.0 --bundle-only  # Just demo bundle
    python build-demos.py --iiif-only                  # Just IIIF tiles (skips existing)
    python build-demos.py --iiif-only --force          # Regenerate all IIIF tiles
        """
    )
    parser.add_argument("--version", "-v", help="Telar version (e.g., 0.6.0)")
    parser.add_argument("--bundle-only", action="store_true", help="Generate only demo bundle")
    parser.add_argument("--iiif-only", action="store_true", help="Generate only IIIF tiles")
    parser.add_argument("--base-url", help=f"Base URL for IIIF (default: {DEFAULT_BASE_URL})")
    parser.add_argument("--skip-validation", action="store_true", help="Skip IIIF manifest validation")
    parser.add_argument("--force", action="store_true", help="Force regenerate IIIF tiles even if they exist")

    args = parser.parse_args()

    print(f"Telar Demos Generator v{GENERATOR_VERSION}")
    print("-" * 40)

    # Validate arguments
    if args.iiif_only and args.bundle_only:
        print("Error: Cannot use both --iiif-only and --bundle-only")
        sys.exit(1)

    if not args.iiif_only and not args.version:
        print("Error: --version is required unless using --iiif-only")
        sys.exit(1)

    success = True

    # Generate IIIF if not bundle-only
    if not args.bundle_only:
        print("\n[IIIF Generation]")
        if not generate_iiif_tiles(base_url=args.base_url, force=args.force):
            success = False

        # Validate IIIF manifests unless skipped
        if not args.skip_validation:
            if not validate_all_iiif_manifests():
                success = False

    # Generate bundle if not iiif-only
    if not args.iiif_only:
        print(f"\n[Bundle Generation for v{args.version}]")

        bundle_success, warnings = generate_bundles_for_version(
            args.version,
            base_url=args.base_url
        )

        if warnings:
            print("\n" + "=" * 40)
            print("WARNINGS:")
            for warning in warnings:
                print(f"  - {warning}")
            print("=" * 40)

        if not bundle_success:
            print("\nError: No valid language content found.")
            success = False
        else:
            # Update versions index after successful bundle generation
            generate_versions_index()

    print("\nDone!")
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
