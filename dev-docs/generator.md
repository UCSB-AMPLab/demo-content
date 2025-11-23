# Generator Documentation

The generator script (`generator/build.py`) creates demo content from source files.

## Workflow

```bash
cd telar-demos/generator

# Generate English demos
python build.py --version 0.6.0 --language en

# Generate Spanish demos
python build.py --version 0.6.0 --language es

# Or generate all at once
python build.py --version 0.6.0 --all-languages

# Review and commit
cd ..
git add demos/
git commit -m "Generate v0.6.0 demos"
git push
```

## What the Generator Does

1. Reads `config.yml` for demo sources and metadata
2. Copies CSV files (project.csv, story.csv, objects.csv)
3. Copies text files (texts/stories/*.md, texts/glossary/*.md)
4. Generates manifest.json listing all content

## Configuration

Edit `generator/config.yml`:

```yaml
demos:
  en:
    telar-tutorial:
      title: "Introduction to Telar"
      description: "Learn the basics..."
      source: "/path/to/tutorial/content"
```

## Adding a New Demo

1. Create source content with standard Telar structure
2. Add entry to `config.yml` with source path
3. Run generator for that version/language
4. Review output in `demos/vX.X.X/`
5. Commit and push

## Regenerating Manifest Only

If you manually edited demo files and need to update the manifest:

```bash
python build.py --version 0.6.0 --all-languages --manifest-only
```
