Telar panels can include **rich media** alongside text (see the [Markdown syntax guide](https://telar.org/docs/reference/markdown-syntax/) in the Telar docs for embedding details):

**Images** can be embedded directly using [[demo-markdown]] syntax. Control image sizing with `{sm}`, `{md}`, `{lg}`, or `{full}` tags:

![AMPL Logo](/components/images/ampl-logo.png){sm}

**Videos** can also be embedded, allowing you to combine [[demo-iiif]] images with multimedia explanations, oral histories, or documentary footage:

<div style="padding:56.25% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/1139902893?h=e450fba07a&badge=0&autopause=0&player_id=0&app_id=58479" frameborder="0" allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media" style="position:absolute;top:0;left:0;width:100%;height:100%;" title="Telar Demo"></iframe></div>

**Combine everything** to create compelling scholarly narratives:

- [[demo-iiif|IIIF images]] from global repositories (see the [IIIF integration guide](https://telar.org/docs/iiif-integration/) in the Telar docs)
- Locally-hosted materials with auto-generated [[demo-iiif-tiles]] (see [Local IIIF images](https://telar.org/docs/iiif-integration/#option-1-local-images) in the Telar docs)
- Pan and zoom navigation to guide attention
- Two-layer panel system for progressive disclosure
- Full [[demo-markdown]] formatting with footnotes
- Glossary auto-linking for technical terms
- Interactive widgets (carousel, tabs, accordion)
- Embedded images and videos in panels

**The result:** A rich, interactive reading experience that combines archival materials, scholarly interpretation, and multimedia storytelling - all from a simple set of CSV files and markdown text.
