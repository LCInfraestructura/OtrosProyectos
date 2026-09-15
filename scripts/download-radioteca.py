"""Download verified URLs only; incomplete catalogs produce a nonzero exit."""
import json,pathlib,urllib.request,sys
root=pathlib.Path(__file__).resolve().parents[1]; base=root/'assets/loteria'
cards={c['id']:c for c in json.loads((base/'manifest.json').read_text(encoding='utf8'))}
links=json.loads((base/'radioteca-downloads.json').read_text(encoding='utf8'))
out=root/'downloads/radioteca-originals'; out.mkdir(parents=True,exist_ok=True)
errors=[]; seen=set()
for link in links:
    i=link['id']
    if i not in cards or i in seen: raise SystemExit(f'Invalid or duplicate ID: {i}')
    seen.add(i); target=out/pathlib.Path(cards[i]['audio']['radioteca']).name
    if target.exists() and target.stat().st_size: continue
    try:
        with urllib.request.urlopen(link['url'],timeout=12) as response:
            data=response.read()
            if not data or 'text/html' in response.headers.get('Content-Type',''): raise ValueError('Not an audio response')
        target.write_bytes(data); print(f'Downloaded card {i}',flush=True)
    except Exception as e: errors.append(f'Card {i}: {e}')
missing=[i for i,c in cards.items() if not (out/pathlib.Path(c['audio']['radioteca']).name).exists()]
for error in errors: print(error)
print(f'Missing original tracks: {missing}')
sys.exit(1 if missing else 0)
