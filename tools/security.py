"""Adds/refreshes the security meta tags (Content-Security-Policy + referrer policy)
on index.html and returns the song-page versions. Safe to run repeatedly."""
import re, hashlib, base64, pathlib

FONTS_CSS = "https://fonts.googleapis.com"
FONTS = "https://fonts.gstatic.com"

def _csp(script_src):
    return ("default-src 'self'; "
            f"script-src {script_src}; "
            f"style-src 'self' 'unsafe-inline' {FONTS_CSS}; "
            f"font-src {FONTS}; "
            "img-src 'self' data:; media-src 'self'; connect-src 'self'; "
            "frame-src 'none'; object-src 'none'; base-uri 'self'; form-action 'none'; "
            "upgrade-insecure-requests")

def meta(script_src):
    return (f'<meta http-equiv="Content-Security-Policy" content="{_csp(script_src)}">'
            '<meta name="referrer" content="strict-origin-when-cross-origin">')

SONG_META = meta("'none'")
TAG = re.compile(r'<meta http-equiv="Content-Security-Policy"[^>]*><meta name="referrer"[^>]*>')

def refresh_index(path):
    p = pathlib.Path(path); h = p.read_text(encoding="utf-8")
    scripts = re.findall(r'<script>(.*?)</script>', h, re.S)
    hashes = " ".join("'sha256-%s'" % base64.b64encode(hashlib.sha256(s.encode("utf-8")).digest()).decode() for s in scripts)
    m = meta(hashes or "'none'")
    h = TAG.sub(m, h) if TAG.search(h) else h.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">' + m, 1)
    p.write_text(h, encoding="utf-8")

if __name__ == "__main__":
    refresh_index(pathlib.Path(__file__).resolve().parent.parent / "index.html")
