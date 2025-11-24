# Adding New Demos

## Prerequisites

Demo source content must follow standard Telar structure:
```
demo-source/
├── project.csv
├── story.csv
├── objects.csv
└── texts/
    ├── stories/
    │   └── *.md
    └── glossary/
        └── *.md
```

## Steps

### 1. Prepare Source Content

Create or locate your demo content with the structure above.

### 2. Update Generator Config

Edit `generator/config.yml`:

```yaml
demos:
  en:
    new-demo:
      title: "My New Demo"
      description: "Description of the demo."
      source: "/path/to/demo/source"
  es:
    demo-nuevo:
      title: "Mi Nuevo Demo"
      description: "Descripcion del demo."
      source: "/path/to/demo/source/spanish"
```

### 3. Run Generator

```bash
cd generator
python build.py --version 0.6.0 --all-languages
```

### 4. Verify Output

Check `demos/v0.6.0/`:
- New demo folders exist
- CSV files copied
- Text files copied
- manifest.json updated

### 5. Update Landing Page (if needed)

Edit `index.md` to list the new demo.

### 6. Commit and Deploy

```bash
git add .
git commit -m "Add new-demo to v0.6.0"
git push
```

## IIIF Images

If your demo uses self-hosted IIIF images:

1. Generate tiles using your preferred tool
2. Place in `iiif/demo-name/`
3. Update objects.csv to point to `https://telar.org/demo-content/iiif/demo-name/...`
