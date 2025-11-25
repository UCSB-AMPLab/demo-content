---
term_id: demo-iiif-tiles
title: "IIIF Tiles"
related_terms: demo-iiif, demo-iiif-manifest
---

IIIF tiles are small, square image segments (typically 256×256 or 512×512 pixels) arranged in a multi-resolution pyramid structure that enables smooth pan and zoom functionality for large, high-resolution images on the web. This approach, commonly called "[deep zoom](https://en.wikipedia.org/wiki/Deep_Zoom)" or "tiled pyramids," addresses a key challenge in web-based image viewing: high-resolution photographs or manuscript scans can be far too large to download and display at once.

The tiling system works by creating multiple versions of the source image at different resolutions (a pyramid) and dividing each resolution level into a grid of small tiles. When a viewer displays this image, it only requests the specific tiles needed for the current viewport and zoom level.

This is the same technology used by [Google Maps](https://en.wikipedia.org/wiki/Google_Maps) (you don't download the entire map of the world to view your neighborhood). The IIIF [Image API](https://iiif.io/api/image/) standardizes how to request these tiles.

When Telar generates IIIF tiles from your local images, it creates this pyramid structure automatically, producing thousands of individual tile images from a single source photograph or scan.

**Learn more:**
- [IIIF Image API specification](https://iiif.io/api/image/3.0/)
- [Deep Zoom on Wikipedia](https://en.wikipedia.org/wiki/Deep_Zoom)
