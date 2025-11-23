# Telar Demos Generator

Scripts for generating demo content.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

Generate demos for a specific version and language:

```bash
python build.py --version 0.6.0 --language en
python build.py --version 0.6.0 --language es
```

Generate for all languages:

```bash
python build.py --version 0.6.0 --all-languages
```

Regenerate manifest only (without copying files):

```bash
python build.py --version 0.6.0 --all-languages --manifest-only
```

## Configuration

Edit `config.yml` to configure:
- Demo source paths
- Demo titles and descriptions
- Google Sheets integration (future)

## Output

Generated content goes to `../demos/vX.X.X/`:

```
demos/v0.6.0/
├── manifest.json
├── en/
│   ├── telar-tutorial/
│   └── paisajes-demo/
└── es/
    ├── tutorial-telar/
    └── demo-paisajes/
```
