# Changelog

All notable changes to the telar-demo-content repository.

## [Unreleased]

### Demo Content (v0.8.1)
- allegorical-woman / mujer-alegorica: New story with 10 steps
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
- Carousel items in generated bundles declare `width` and `height`, read from the image files in this repository, so a site build no longer downloads each carousel image from content.telar.org to size the carousel. Regenerated for v0.9.0 and v0.8.1
- The three carousels in the v0.6.0 English bundle declare `width` and `height` for all sixteen of their items, read from the image files in this repository, so a site on 0.6.x no longer downloads sixteen images from content.telar.org on every build. The Spanish v0.6.0 bundle carries no stories and is unchanged
- The six panels of the colonial-landscapes / paisajes story in the v0.8.1 bundles, published as the names of their source files, carry the panels' text. The bundles are otherwise identical to the published ones apart from their generation stamp and format version, which no Telar version reads
- The `demo-livestock` and `demo-jorge-tadeo-lozano` glossary entries are in the v0.8.1 and v0.9.0 English glossary sources; they had been added to the published bundles only, and regenerating dropped them
- Story panel markdown loading: `.md` file references in layer content were rendered as literal file paths instead of loading the actual markdown files (column normalisation conflict in `build-demos.py`)
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
