# telar-demos

Demo content hosting for [Telar](https://github.com/UCSB-AMPLab/telar) scrollytelling sites.

## Overview

This repository provides versioned, multilingual demo content that Telar sites can fetch at build time. Demo stories appear on user sites when enabled but are never committed to their repositories.

**Live site:** [demos.telar.org](https://demos.telar.org)

## Available Demos

### v0.6.0

| Demo | English | Spanish |
|------|---------|---------|
| Tutorial | `telar-tutorial` | `tutorial-telar` |
| Paisajes Coloniales | `paisajes-demo` | `demo-paisajes` |

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
│       └── es/
├── iiif/               # Self-hosted IIIF tiles
├── generator/          # Build scripts (internal)
└── dev-docs/           # Developer documentation (internal)
```

## For Developers

See `dev-docs/` for internal documentation on the generator script and adding new demos.

## License

MIT License - See [LICENSE](LICENSE) for details.

---

Part of the [Telar](https://github.com/UCSB-AMPLab/telar) project by [UCSB AMPLab](https://github.com/UCSB-AMPLab).
