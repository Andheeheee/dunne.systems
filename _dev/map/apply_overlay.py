"""Regenerate the map overlay and inject it into index.html.

Run from the repo root:
    python3 _dev/map/landmarks.py        # writes _dev/map/overlay.svg
    python3 _dev/map/apply_overlay.py    # replaces <template id="map-tpl"> in index.html
"""
import pathlib, re
root = pathlib.Path(__file__).resolve().parents[2]
svg = (pathlib.Path(__file__).parent / "overlay.svg").read_text()
html_path = root / "index.html"
html = html_path.read_text()
new, n = re.subn(r'<template id="map-tpl">.*?</template>', lambda m: f'<template id="map-tpl">{svg}</template>', html, count=1, flags=re.S)
assert n == 1, "map-tpl template not found in index.html"
html_path.write_text(new)
print("Injected overlay.svg into index.html")
