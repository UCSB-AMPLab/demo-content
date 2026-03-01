# Changelog

All notable changes to the telar-demo-content repository.

## [Unreleased]

### Demo Content (v0.8.1)
- allegorical-woman / mujer-alegorica: New story with 39 steps
- colonial-landscapes / paisajes: Updated bilingual demo with markdown panels
- Leviathan IIIF: Self-hosted tiles for allegorical woman painting
- Extended demo-objects catalog (51 EN / 100 ES objects)
- Extended glossary terms (21 entries)

### Demo Content (v0.6.0)
- paisajes-demo (EN) / demo-paisajes (ES): Colonial maps and land ownership in 17th-century Bogotá
- telar-tutorial: Bilingual tutorial story with rich media examples
- Step 5 CTA linking to full Colonial Landscapes project
- Self-hosted IIIF for demo-bogota-1614 painting
- Demo-prefixed glossary terms for namespace isolation
- Auto-generated thumbnails for self-hosted IIIF objects

### Changed
- Switched from multiple files to single JSON bundle format (telar-demo-bundle.json)
- Moved from demos.telar.org to content.telar.org subdomain
- Store raw markdown in bundles instead of HTML
- Aligned demo content with story_id feature

### Fixed
- Carousel image paths to use full URLs
- AMPL logo image path in rich_media tutorial
- IIIF URLs: content.telar.org instead of demos.telar.org
- Demo project CSV formatting
- Markdown bullet list spacing
- Caption formatting with italics

### Generator Features
- Demo manifest generation (--manifest-only)
- IIIF tile generation (--iiif-only)
- Multilingual IIIF manifests from all-demo-objects.csv
- Schema validation with --skip-validation option

---

## Version Format

This repository uses its own versioning separate from Telar versions.

Demo content is organized by Telar version (v0.6.0, v0.8.1, etc.).
