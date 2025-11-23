# Versioning Strategy

## Repository Version

The telar-demos repository has its own version (v1.0.0, v1.1.0, etc.) tracking:
- Generator script changes
- Infrastructure updates
- Major additions

Tagged releases are created for significant changes.

## Demo Content Version

Demo content is organized by Telar version:
- `demos/v0.6.0/` - Demos for Telar v0.6.0
- `demos/v0.7.0/` - Demos for Telar v0.7.0
- etc.

The fetch script matches the user's Telar version to the appropriate demo version.

## Version Retention

All demo versions are retained permanently. No pruning.

## Files with Version Headers

- `generator/build.py` - Generator script version
- `CHANGELOG.md` - All changes tracked

## Creating a New Version

When a new Telar version is released:

1. Copy previous version's demo content if needed
2. Update content for new features
3. Run generator:
   ```bash
   python build.py --version X.X.X --all-languages
   ```
4. Update CHANGELOG.md
5. Commit and push

## Backwards Compatibility

Old demo versions remain available for users on older Telar versions. The fetch script will request demos matching the user's Telar version.
