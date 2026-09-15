import pathlib,zipfile,json,unicodedata,hashlib
root=pathlib.Path(__file__).resolve().parents[1]; base=root/'assets/loteria'
cards=json.loads((base/'manifest.json').read_text(encoding='utf8'))
def key(s): return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if c.isalnum() and unicodedata.category(c)!='Mn')
records=[]
with zipfile.ZipFile(root/'downloads/mexican-loteria-sprites.zip') as z:
    names={key(pathlib.PurePosixPath(p).stem):p for p in z.namelist() if p.lower().endswith('.png')}
    for c in cards:
        # Publisher spells Cazo as Caso. This is an explicit alias, not a numeric reorder.
        source=names['elcaso' if c['id']==36 else key(c['name'])]
        data=z.read(source); out=base/c['images']['pixel']; out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(data)
        records.append(dict(id=c['id'],source=source,target=c['images']['pixel'],sha256=hashlib.sha256(data).hexdigest()))
(base/'pixel-provenance.json').write_text(json.dumps(records,indent=2),encoding='utf8')
print('54 canonical sprites imported. Extra elote and card backs excluded.')
