# Troubleshooting

## Generator Issues

### "Config file not found"

Ensure you're running from the `generator/` directory:
```bash
cd telar-demos/generator
python build.py --version 0.6.0 --language en
```

### "PyYAML not installed"

Install dependencies:
```bash
pip install -r requirements.txt
```

### "Source path does not exist"

Check the path in `config.yml`. Ensure:
- Path is absolute
- Directory exists
- You have read permissions

## Build Issues

### Jekyll build fails

Check:
- Ruby and Jekyll installed
- Run `bundle install` in repo root
- Check `_config.yml` syntax

### Styles not loading

Ensure `assets/css/style.scss` has front matter (two `---` lines at top).

## Fetch Issues (User Sites)

### "Manifest not found"

- Check telar.org/demo-content is accessible
- Verify version exists in `demos/`
- Check manifest.json was generated

### "Demo files missing"

Run generator with verbose output:
```bash
python build.py --version X.X.X --all-languages
```

Check that source paths have all required files.

### CORS errors

GitHub Pages should handle CORS. If issues persist:
- Check browser console for specific errors
- Verify files are accessible directly in browser

## Deployment Issues

### Changes not appearing on telar.org/demo-content

- Check GitHub Actions completed successfully
- Clear browser cache
- Wait a few minutes for GitHub Pages CDN
