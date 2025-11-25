# telar-demo-content

Demo content hosting for [Telar](https://github.com/UCSB-AMPLab/telar) scrollytelling sites.

## Overview

This repository provides versioned, multilingual demo content that Telar sites can fetch at build time. Demo stories appear on user sites when enabled but are never committed to their repositories.

**Live site:** [content.telar.org](https://content.telar.org)

## Available Demos

### v0.6.0

| Demo | English | Spanish | Description |
|------|---------|---------|-------------|
| Telar Tutorial | `telar-tutorial` | `tutorial-telar` | Learn Telar basics: IIIF images, navigation, widgets |
| Paisajes Coloniales | `paisajes-demo` | `demo-paisajes` | Colonial maps and land ownership in 17th-century Bogota |

## Using Demos in Your Telar Site

Add to your `_config.yml`:

```yaml
story_interface:
  include_demo_content: true
```

When your site builds, the fetch script downloads a single demo bundle matching your Telar version and language setting.

## Bundle Format

Demo content is delivered as a **single JSON bundle** (`telar-demo-bundle.json`) per language/version:

```json
{
  "_meta": {
    "bundle_format": "0.1",
    "telar_version": "0.6.0",
    "language": "en",
    "generated": "2025-11-25T...",
    "license": "CC BY-NC 4.0"
  },
  "iiif_base_url": "https://content.telar.org/iiif/objects",
  "project": [...],
  "objects": {...},
  "stories": {...},
  "glossary": {...}
}
```

**Key features:**
- One HTTP request instead of 30+
- Layer content embedded directly (no separate file fetches)
- Auto-populated IIIF source URLs for self-hosted objects
- Built-in validation catches CSV parsing issues

## Version Matching

Sites receive demo content compatible with their Telar version:

| Site Version | Available Demos | Result |
|--------------|-----------------|--------|
| 0.6.0 | 0.6.0 | Exact match: 0.6.0 |
| 0.6.3 | 0.6.0, 0.6.1 | Best match: 0.6.1 |
| 0.5.0 | 0.6.0, 0.7.0 | No compatible version |
| 0.8.0 | 0.6.0, 0.7.0 | Best match: 0.7.0 |

The fetch script finds the **highest available version that is <= site version**.

## Repository Structure

```
telar-demo-content/
├── demos/
│   ├── versions.json              # Auto-generated index
│   └── v0.6.0/
│       ├── en/
│       │   ├── telar-demo-bundle.json  # Complete bundle
│       │   ├── demo-project.csv        # Source files
│       │   ├── demo-objects.csv
│       │   ├── telar-tutorial.csv
│       │   └── texts/
│       └── es/
│           └── ...
├── iiif/
│   ├── all-demo-objects.csv       # IIIF object registry
│   ├── sources/                   # Source images
│   └── objects/                   # Generated tiles (shared)
│       └── demo-bogota-1614/
│           ├── info.json
│           ├── manifest.json
│           └── tiles/
├── generator/
│   └── build-demos.py             # Generation script
└── dev-docs/                      # Developer documentation
```

## For Developers

### Generating Bundles

```bash
# Generate bundle for a version and language
python generator/build-demos.py --version 0.6.0

# Generate IIIF tiles only
python generator/build-demos.py --iiif-only

# Force regeneration of existing tiles
python generator/build-demos.py --iiif-only --force
```

### Adding New Demo Content

1. Add/update source CSVs in `demos/vX.X.X/{lang}/`
2. Add markdown files in `texts/` subdirectories
3. For self-hosted images, add to `iiif/sources/` and `iiif/all-demo-objects.csv`
4. Run `python generator/build-demos.py --version X.X.X`

See `dev-docs/` for detailed documentation.

## License

MIT License - See [LICENSE](LICENSE) for details.

Demo content is licensed under CC BY-NC 4.0.

---

Part of the [Telar](https://github.com/UCSB-AMPLab/telar) project by [UCSB AMPLab](https://github.com/UCSB-AMPLab).
