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
├── assets/css/style.scss       # Minimal styles
│
├── generator/                  # Build scripts (not deployed)
│   ├── build.py               # Main generator
│   ├── config.yml             # Source paths and settings
│   ├── requirements.txt       # Python dependencies
│   └── README.md              # Generator docs
│
├── demos/                      # Generated demo content
│   └── v0.6.0/
│       ├── manifest.json
│       ├── en/{telar-tutorial,paisajes-demo}/
│       └── es/{tutorial-telar,demo-paisajes}/
│
├── iiif/                       # Self-hosted IIIF tiles
│   ├── tutorial/
│   └── paisajes/
│
├── dev-docs/                   # This folder (not deployed)
├── CHANGELOG.md
└── README.md
```

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
  "generator_version": "1.0.0",
  "demos": {
    "en": {
      "telar-tutorial": {
        "title": "Introduction to Telar",
        "description": "...",
        "files": ["project.csv", "story.csv", "objects.csv"],
        "texts": {
          "stories": ["step1.md", "step2.md"],
          "glossary": ["iiif.md", "manifest.md"]
        }
      }
    }
  }
}
```

## URL Structure

- Landing: `https://demos.telar.org/`
- Manifest: `https://demos.telar.org/demos/v0.6.0/manifest.json`
- Demo files: `https://demos.telar.org/demos/v0.6.0/en/telar-tutorial/story.csv`
- IIIF: `https://demos.telar.org/iiif/tutorial/image1/info.json`
