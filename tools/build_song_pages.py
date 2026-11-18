"""Rebuild song/<slug>/index.html pages, sitemap.xml and robots.txt from songs.json + lyrics.json.
Run from the repo root: python3 tools/build_song_pages.py"""
import json,re,html,unicodedata,os
BASE='https://rellytadeort-png.github.io/newvizcayarecords'
h=open('index.html').read()
css=[b for b in re.findall(r'<style>(.*?)</style>',h,re.S) if '--pine' in b][0]
fonts=re.search(r'(<link rel="preconnect".*?rel="stylesheet">)',h,re.S).group(1)
S=json.load(open('songs.json'))['songs']
L=json.load(open('lyrics.json')) if os.path.exists('lyrics.json') else {}
def slug(t):
    t=unicodedata.normalize('NFD',t.lower());t=''.join(c for c in t if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',t).strip('-')
urls=[BASE+'/']
for s in S:
    sl=slug(s['title']);ly=L.get(s['title'],'')
    os.makedirs(f'song/{sl}',exist_ok=True)
    t=html.escape(s['title']);img=f"{BASE}/{s['cover']}" if s.get('cover') else f"{BASE}/logo-512.png"
    desc=f"{s['title']} by Vizcaya Sound"+(" - lyrics, Spotify and Apple Music links." if ly else " - stream on Spotify and Apple Music.")
    body=html.escape(ly) if ly else 'Lyrics for this song are coming soon.'
    cover=f'<img src="../../{s["cover"]}" alt="Cover art for {t}" width="240" height="240" style="border-radius:16px">' if s.get('cover') else ''
    apple=f'<a class="btn apple" href="{html.escape(s["apple"])}">&#9654; Apple Music</a>' if s.get('apple') else ''
    prev=f'<audio controls preload="none" src="../../{s["preview"]}" style="width:100%;max-width:420px;margin-top:16px"></audio>' if s.get('preview') else ''
    jsonld=json.dumps({"@context":"https://schema.org","@type":"MusicRecording","name":s['title'],"byArtist":{"@type":"MusicGroup","name":"Vizcaya Sound"},"datePublished":s.get('released'),"url":f"{BASE}/song/{sl}/","sameAs":[x for x in [s['spotify'],s.get('apple')] if x]},ensure_ascii=False)
    rel=(' · '+s['released']) if s.get('released') else ''
    page=f'''<!DOCTYPE html><html lang="tl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t} Lyrics · Vizcaya Sound</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{BASE}/song/{sl}/">
<meta property="og:type" content="music.song"><meta property="og:title" content="{t} · Vizcaya Sound"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:image" content="{img}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="../../logo-96.png">{fonts}<style>{css}
.songpage{{display:grid;grid-template-columns:260px 1fr;gap:36px;padding:48px 0}}@media (max-width:700px){{.songpage{{grid-template-columns:1fr;gap:20px;padding:28px 0}}}}
.lyrics{{white-space:pre-line;font-size:17px;line-height:1.75;max-width:60ch;margin-top:18px}}</style>
<script type="application/ld+json">{jsonld}</script></head><body>
<header class="top"><div class="wrap"><a class="mark" href="../../"><img src="../../logo-96.png" alt="" width="42" height="42">New Vizcaya Records</a><nav><a href="../../#songs">Songs</a><a href="../../#catalogue">Catalogue</a><a href="../../#fans">Fan list</a></nav></div></header>
<main class="wrap songpage"><div>{cover}{prev}</div><div><p class="eyebrow">Vizcaya Sound{rel}</p><h1 style="font-size:clamp(34px,5vw,56px)">{t}</h1>
<div class="cta"><a class="btn spot" href="{html.escape(s['spotify'])}">&#9654; Spotify</a>{apple}</div>
<h2 style="margin-top:32px;font-size:24px">Lyrics</h2><div class="lyrics">{body}</div>
<p class="sub" style="margin-top:28px"><a href="../../">More songs from New Vizcaya Records &rarr;</a></p></div></main>
<footer><div class="wrap"><span>&copy; 2026 New Vizcaya Records. All songs by Vizcaya Sound.</span></div></footer></body></html>'''
    open(f'song/{sl}/index.html','w').write(page);urls.append(f'{BASE}/song/{sl}/')
open('sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{u}</loc></url>\n' for u in urls)+'</urlset>\n')
open('robots.txt','w').write(f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
print('built',len(urls)-1,'song pages')
