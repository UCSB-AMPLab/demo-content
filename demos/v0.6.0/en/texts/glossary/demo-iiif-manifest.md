---
term_id: demo-iiif-manifest
title: "IIIF Manifest"
related_terms: demo-iiif, demo-iiif-tiles
---

A IIIF manifest is a [JSON-LD](https://json-ld.org/) file that describes one or more images and their metadata according to the [IIIF Presentation API](https://iiif.io/api/presentation/) specification. The manifest serves as a "recipe" that tells IIIF-compatible viewers and tools, like Telar, what images are available, how they're organized, and how to display them.

At a technical level, a manifest contains several key components: metadata about the object (title, description, attribution, rights, license), a sequence of "canvases" (each representing a page, view, or surface), and annotations that link these canvases to actual image resources served by a IIIF Image API server.

When you provide a manifest URL to Telar (or any IIIF viewer), the application fetches this JSON file, reads its structured data to understand what images are available, and then requests image tiles at appropriate sizes as users pan and zoom.

Because manifests follow a standardized format, any IIIF viewer can consume them, regardless of what institution created them—this is IIIF's core value proposition.

**Learn more:**

- [IIIF Presentation API 3.0 specification](https://iiif.io/api/presentation/3.0/)
- [IIIF Cookbook - Manifest recipes and examples](https://iiif.io/api/cookbook/)
