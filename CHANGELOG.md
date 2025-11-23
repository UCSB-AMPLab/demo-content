# Changelog

All notable changes to the telar-demos repository.

## [Unreleased]

### Added
- Initial repository structure
- Minimal Jekyll site for demos.telar.org
- Generator script (build-demos.py) for creating demo content and IIIF tiles
- Developer documentation in dev-docs/
- Demo structure for v0.6.0 (en/es)
- Self-hosted panel images in assets/images/paisajes-demo/
- Self-hosted IIIF tiles with multilingual manifests (EN/ES)
- IIIF manifest validation against Presentation API 3.0 schema

### Generator Features
- Demo manifest generation (--manifest-only)
- IIIF tile generation (--iiif-only)
- Multilingual IIIF manifests from all-demo-objects.csv
- Schema validation with --skip-validation option

### Demo Content (v0.6.0)
- paisajes-demo (EN) / demo-paisajes (ES): Colonial maps and land ownership in 17th-century Bogotá
- Step 5 CTA linking to full Colonial Landscapes project
- Self-hosted IIIF for demo-bogota-1614 painting

---

## Version Format

This repository uses its own versioning (v1.0.0, v1.1.0, etc.) separate from Telar versions.

Demo content is organized by Telar version (v0.6.0, v0.7.0, etc.).
