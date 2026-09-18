"""Integrate the classic 54 recordings without changing display titles or audio bytes."""
import hashlib,json,pathlib,shutil
root=pathlib.Path(__file__).resolve().parents[1]; base=root/'assets/loteria'
source=root/'assets/audio-packs/loteriacaller'
catalog=json.loads((base/'manifest.json').read_text(encoding='utf8'))
pack=json.loads((source/'manifest.json').read_text(encoding='utf8'))
variants={'generated-es':'names-es','generated-en':'names-en','generated-verses-es':'verses-es'}
records=[]
for card in catalog:
    card['audio'].pop('radioteca',None)
    for variant,kind in variants.items():
        matches=[r for r in pack['files'] if r['number']==card['id'] and r['group']=='classic' and r['kind']==kind and r['status']=='downloaded']
        if len(matches)!=1: raise ValueError(f'Card {card["id"]}: missing/ambiguous {kind}')
        entry=matches[0]; data=(source/entry['path']).read_bytes()
        if hashlib.sha256(data).hexdigest()!=entry['sha256']: raise ValueError('Source hash mismatch')
        relative=f'audio/{variant}/{card["id"]:02}-{card["slug"]}.mp3'
        target=base/relative; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
        card['audio'][variant]=relative
        records.append(dict(id=card['id'],variant=variant,source=entry['url'],target=relative,sha256=entry['sha256']))
(base/'manifest.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(base/'generated-provenance.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
print('Integrated 3 x 54 generated recordings; removed Radioteca references from catalog.')
