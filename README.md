# telar-demo-content

Demo content hosting for [Telar](https://github.com/UCSB-AMPLab/telar) scrollytelling sites.

**Live site:** [content.telar.org](https://content.telar.org)

## Overview

This repository provides versioned, multilingual demo content that Telar sites can fetch at build time. Demo stories appear on user sites when enabled but are never committed to their repositories.

## Using Demos in Your Telar Site

Add to your `_config.yml`:

```yaml
story_interface:
  include_demo_content: true
```

When your site builds, the fetch script downloads a single demo bundle matching your Telar version and language setting.

### Version Matching

Sites receive demo content compatible with their Telar version. The fetch script finds the highest available version that is <= the site version.

| Site Version | Available Demos | Result |
|--------------|-----------------|--------|
| 0.9.0 | 0.6.0, 0.8.1, 0.9.0 | Exact match: 0.9.0 |
| 0.8.3 | 0.6.0, 0.8.1 | Best match: 0.8.1 |
| 0.5.0 | 0.6.0, 0.8.1 | No compatible version |

## Bundle Format

Demo content is delivered as a single JSON bundle (`telar-demo-bundle.json`) per language and version:

```json
{
  "_meta": {
    "bundle_format": "0.1",
    "telar_version": "0.9.0",
    "language": "en",
    "generated": "2026-02-28T...",
    "license": "CC BY-NC 4.0"
  },
  "iiif_base_url": "https://content.telar.org/iiif/objects",
  "project": [...],
  "objects": {...},
  "stories": {...},
  "glossary": {...}
}
```

Key features:
- One HTTP request instead of 30+
- Layer content embedded directly (no separate file fetches)
- Auto-populated IIIF source URLs for self-hosted objects
- Built-in validation catches CSV parsing issues

## Repository Structure

```
telar-demo-content/
├── demos/
│   ├── versions.json                  # Auto-generated version index
│   └── v0.9.0/
│       ├── en/
│       │   ├── telar-demo-bundle.json # Complete bundle
│       │   ├── demo-project.csv       # Source CSVs
│       │   ├── demo-objects.csv
│       │   ├── colonial-landscapes.csv
│       │   ├── glossary.csv
│       │   └── texts/stories/         # Markdown content files
│       └── es/
├── iiif/
│   ├── all-demo-objects.csv           # Object registry (multilingual metadata)
│   ├── sources/                       # Source images
│   └── objects/                       # Generated IIIF tiles and manifests
│       └── demo-bogota-1614/
│           ├── info.json
│           ├── manifest.json
│           └── full/, 0,0,.../ ...    # Tile directories
├── generator/
│   ├── build-demos.py                 # Generation script
│   ├── config.yml                     # Demo source paths
│   ├── requirements.txt               # Python dependencies
│   └── schemas/                       # IIIF validation schemas
└── dev-docs/                          # Internal documentation
```

## Generator

### Setup

```bash
pip install -r generator/requirements.txt
```

For IIIF tile generation you also need one of:
- **libvips** (recommended, much faster): `brew install vips` (macOS) or `sudo apt-get install libvips-dev` (Linux)
- **Python iiif library** (fallback): `pip install iiif`

Pillow is required for both backends: `pip install Pillow`

### Usage

```bash
# Generate both bundle and IIIF tiles for a version
python generator/build-demos.py --version 0.9.0

# Bundle only (no IIIF generation)
python generator/build-demos.py --version 0.9.0 --bundle-only

# IIIF tiles only (no version needed)
python generator/build-demos.py --iiif-only

# Force-regenerate existing tiles
python generator/build-demos.py --iiif-only --force

# Custom base URL for IIIF manifests (e.g. local development)
python generator/build-demos.py --iiif-only --base-url http://localhost:4000

# Skip IIIF manifest validation
python generator/build-demos.py --version 0.9.0 --skip-validation
```

### CLI Reference

| Flag | Description | Default |
|------|-------------|---------|
| `--version`, `-v` | Telar version number (required unless `--iiif-only`) | — |
| `--bundle-only` | Generate only the demo bundle | false |
| `--iiif-only` | Generate only IIIF tiles | false |
| `--force` | Regenerate tiles even if they already exist | false |
| `--base-url` | Base URL for IIIF manifest references | `https://content.telar.org` |
| `--skip-validation` | Skip IIIF manifest validation | false |

### IIIF Object Registry

`iiif/all-demo-objects.csv` lists all objects that need IIIF tiles, with multilingual metadata used to build manifests:

```
object_id, source_image, title_en, title_es, description_en, description_es,
creator_en, creator_es, date_en, date_es, attribution_en, attribution_es, rights
```

Source images go in `iiif/sources/`. The generator reads the CSV, tiles each image, and writes the output to `iiif/objects/{object_id}/`.

### Adding New Demo Content

1. Add or update source CSVs in `demos/vX.X.X/{lang}/`
2. Add markdown files in `texts/stories/` subdirectories
3. For self-hosted images, add to `iiif/sources/` and register in `iiif/all-demo-objects.csv`
4. Run `python generator/build-demos.py --version X.X.X`

See `dev-docs/` for detailed internal documentation.

## License

MIT License — see [LICENSE](LICENSE) for details.

Demo content is licensed under CC BY-NC 4.0.

---

Part of the [Telar](https://github.com/UCSB-AMPLab/telar) project by [UCSB AMPLab](https://github.com/UCSB-AMPLab).
