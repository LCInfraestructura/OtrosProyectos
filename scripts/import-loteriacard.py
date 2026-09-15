"""Import the user-provided LoteriaCard audio by normalized names, never directory order."""
import pathlib,json,unicodedata,hashlib,sys
root=pathlib.Path(__file__).resolve().parents[1]; base=root/'assets/loteria'
source=pathlib.Path(sys.argv[1])
def key(s): return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if c.isalnum() and unicodedata.category(c)!='Mn')
files={key(p.stem):p for p in source.glob('*.mp3')}
cards=json.loads((base/'manifest.json').read_text(encoding='utf8')); records=[]
for c in cards:
    src=files[key(c['name'])]
    target=f'audio/loteriacard/{c["id"]:02}-{c["slug"]}.mp3'
    out=base/target; out.parent.mkdir(parents=True,exist_ok=True); data=src.read_bytes(); out.write_bytes(data)
    c['audio']['loteriacard']=target
    records.append(dict(id=c['id'],source=src.name,target=target,sha256=hashlib.sha256(data).hexdigest()))
src=files['flipcard']; data=src.read_bytes(); target='audio/effects/flipcard.mp3'
out=base/target; out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(data)
records.append(dict(effect='flipcard',source=src.name,target=target,sha256=hashlib.sha256(data).hexdigest()))
(base/'effects.json').write_text(json.dumps(dict(flipcard=target),indent=2),encoding='utf8')
(base/'manifest.json').write_text(json.dumps(cards,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(base/'loteriacard-provenance.json').write_text(json.dumps(records,indent=2),encoding='utf8')
print('Imported 54 voices and flipcard; existing titles preserved.')
