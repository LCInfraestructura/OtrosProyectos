"""Import numbered assets from the approved source ZIP, without its application."""
import json,pathlib,zipfile,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
base=ROOT/'assets/loteria'
cards=json.loads((base/'manifest.json').read_text(encoding='utf-8'))
provenance=[]
with zipfile.ZipFile(ROOT/'downloads/repo.zip') as z:
    prefix='LoteriaMexicana-master/'
    for card in cards:
        for source,target in [(f'cartas/{card["id"]}.jpg',card['images']['traditional']), (f'audio/pavel/{card["id"]}.m4a',card['audio']['repo'])]:
            data=z.read(prefix+source)
            if not data: raise ValueError(f'Empty: {source}')
            out=base/target; out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(data)
            provenance.append(dict(id=card['id'],source=source,target=target,sha256=hashlib.sha256(data).hexdigest()))
(base/'repo-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
print(f'Imported {len(provenance)} assets. Source voice: pavel. Original ZIP retained.')
