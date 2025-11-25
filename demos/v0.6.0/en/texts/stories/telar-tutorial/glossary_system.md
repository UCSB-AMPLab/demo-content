Telar's glossary system provides **wiki-style automatic linking** of technical terms throughout your story content (see [glossary auto-linking](https://telar.org/docs/content-structure/#glossary-auto-linking) in the Telar docs).

**How it works:**
1. Create glossary entry files in `components/texts/glossary/`
2. Link terms in your text using double brackets: `[[iiif]]` or `[[iiif-tiles|IIIF tiles]]`
3. Telar automatically converts these to clickable links
4. Clicking a term opens a slide-over panel with the full definition

**Try it now:** Throughout this tutorial, you've seen several linked terms - [[iiif]], [[iiif-tiles]], [[iiif-manifest|IIIF manifests]], and [[markdown]]. Click any of them to see the full glossary definition.

**Multiple perspectives with tabs:**

:::tabs
## For Readers
The glossary helps readers understand technical concepts without cluttering the main narrative. Terms are linked the first time they appear in each step, providing definitions when needed.

## For Authors
You write glossary entries once and reuse them throughout your stories. This keeps definitions consistent and makes it easy to add context for specialized terminology.
:::

**Benefits:**
- Reduces repetition in your main text
- Provides consistent definitions
- Helps readers learn unfamiliar concepts
- Maintains narrative flow
