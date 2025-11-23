---
layout: default
title: Telar Demos
description: Demo content for Telar scrollytelling sites
---

<p style="text-align: center; margin-bottom: 2rem;">
  <img src="{{ '/assets/images/telar.png' | relative_url }}" alt="Telar" style="max-height: 200px;">
</p>

# Telar Demos

Demo content for [Telar](https://github.com/UCSB-AMPLab/telar) scrollytelling sites.

## Available Demos

<ul class="demo-list">
  <li>
    <strong>Telar Tutorial</strong>
    Learn the basics: IIIF images, navigation, glossary linking, and widgets.
  </li>
  <li>
    <strong>Paisajes Coloniales</strong>
    A polished example exploring colonial landscapes through historical maps and documents.
  </li>
</ul>

## How to Use

Enable demo content in your Telar site by adding to `_config.yml`:

```yaml
include_demo_content: true
```

Demos will be fetched automatically when your site builds. They appear alongside your own stories but are never committed to your repository.

## Learn More

- [Telar Documentation](https://ampl.clair.ucsb.edu/telar-docs/)
- [Telar on GitHub](https://github.com/UCSB-AMPLab/telar)
