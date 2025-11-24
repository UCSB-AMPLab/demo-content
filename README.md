# telar-demos

Demo content hosting for [Telar](https://github.com/UCSB-AMPLab/telar) scrollytelling sites.

## Overview

This repository provides versioned, multilingual demo content that Telar sites can fetch at build time. Demo stories appear on user sites when enabled but are never committed to their repositories.

**Live site:** [telar.org/demo-content](https://telar.org/demo-content)

## Available Demos

### v0.6.0

| Demo | English | Spanish | Description |
|------|---------|---------|-------------|
| Paisajes Coloniales | `paisajes-demo` | `demo-paisajes` | Colonial maps and land ownership in 17th-century Bogotá |

*Tutorial demos coming soon.*

## Using Demos in Your Telar Site

Add to your `_config.yml`:

```yaml
include_demo_content: true
```

When your site builds, the fetch script will download demos matching your Telar version and language setting.

## Repository Structure

```
telar-demos/
├── demos/              # Versioned demo content
│   └── v0.6.0/
│       ├── manifest.json
│       ├── en/
│       │   ├── demo-project.csv
│       │   ├── demo-objects.csv
│       │   ├── demo-story-1.csv
│       │   └── texts/
│       └── es/
│           └── (same structure)
├── assets/             # Self-hosted images for demos
│   └── images/
│       └── paisajes-demo/
├── iiif/               # Self-hosted IIIF tiles
│   ├── sources/        # Source images
│   └── objects/        # Generated tiles and manifests
├── generator/          # Build scripts (internal)
└── dev-docs/           # Developer documentation (internal)
```

## For Developers

See `dev-docs/` for internal documentation on the generator script and adding new demos.

## License

MIT License - See [LICENSE](LICENSE) for details.

---

Part of the [Telar](https://github.com/UCSB-AMPLab/telar) project by [UCSB AMPLab](https://github.com/UCSB-AMPLab).
