# telar-demos Architecture

Internal documentation for the telar-demos repository.

## Purpose

This repository serves two functions:
1. **Static file hosting**: Demo CSVs, markdown, and IIIF tiles fetched by Telar sites at build time
2. **Minimal landing page**: Simple Jekyll site at demos.telar.org

## Repository Structure

```
telar-demos/
├── _config.yml                 # Jekyll config
├── index.md                    # Landing page
├── _layouts/default.html       # Page layout
├── assets/
│   ├── css/style.scss          # Minimal styles
│   └── images/                 # Self-hosted demo images
│       └── paisajes-demo/      # Images for paisajes demo
│
├── generator/                  # Build scripts (not deployed)
│   └── build-demos.py         # Manifest and IIIF generator
│
├── demos/                      # Versioned demo content
│   └── v0.6.0/
│       ├── manifest.json       # Auto-generated
│       ├── en/
│       │   ├── demo-project.csv
│       │   ├── demo-objects.csv
│       │   ├── demo-story-1.csv
│       │   └── texts/
│       │       ├── stories/paisajes-demo/
│       │       └── glossary/
│       └── es/
│           └── (same structure)
│
├── iiif/                       # Self-hosted IIIF tiles
│   ├── objects.csv            # Metadata for IIIF generation
│   ├── sources/               # Raw source images
│   │   └── demo-bogota-1614.jpg
│   └── objects/               # Generated IIIF output
│       └── demo-bogota-1614/
│           ├── info.json      # IIIF Image API info
│           ├── manifest.json  # IIIF Presentation API manifest
│           └── *.jpg          # Tile images
│
├── dev-docs/                   # This folder (not deployed)
├── CHANGELOG.md
└── README.md
```

**Note**: Demo content uses flat structure per language with prefixed CSVs (`demo-project.csv`, `demo-objects.csv`, `demo-story-N.csv`) to avoid conflicts when multiple demos are present.

## How Demos Are Fetched

1. User enables `include_demo_content: true` in their Telar site
2. GitHub Actions runs `fetch_demo_content.py` before Jekyll build
3. Script fetches `demos.telar.org/demos/vX.X.X/manifest.json`
4. Downloads all files listed in manifest to temp directory
5. Jekyll processes demo content as collections
6. Site builds with demos included
7. Demo files are never committed to user repo

## Manifest Format

```json
{
  "version": "0.6.0",
  "generated": "2025-11-23T00:00:00Z",
  "generator_version": "0.1.0",
  "languages": {
    "en": {
      "files": {
        "project": "demo-project.csv",
        "objects": "demo-objects.csv"
      },
      "stories": {
        "paisajes-demo": {
          "title": "A Painting of the Savanna",
          "description": "Explore social and environmental transformations around 17th-century Bogotá",
          "order": 1,
          "csv": "demo-story-1.csv",
          "texts": ["bogota_savanna.md", "encomendero_biography.md", "..."]
        }
      },
      "glossary": ["jorge-tadeo-lozano.md", "kogi-loom.md", "livestock.md"]
    },
    "es": {
      "...": "same structure"
    }
  }
}
```

## URL Structure

- Landing: `https://demos.telar.org/`
- Manifest: `https://demos.telar.org/demos/v0.6.0/manifest.json`
- CSVs: `https://demos.telar.org/demos/v0.6.0/en/demo-story-1.csv`
- Texts: `https://demos.telar.org/demos/v0.6.0/en/texts/stories/paisajes-demo/bogota_savanna.md`
- Images: `https://demos.telar.org/assets/images/paisajes-demo/demo-*.jpg`
- IIIF Info: `https://demos.telar.org/iiif/objects/demo-bogota-1614/info.json`
- IIIF Manifest: `https://demos.telar.org/iiif/objects/demo-bogota-1614/manifest.json`
