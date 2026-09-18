"""Validate identity, paths, decoded pixels/audio; report missing sets explicitly.
Usage: python scripts/verify-loteria-assets.py [--available-only]
Semantic correspondence requires human review, not just successful decoding.
"""
import pathlib,json,sys,subprocess,re,hashlib
from PIL import Image,ImageDraw
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'downloads/python-tools'))
import imageio_ffmpeg
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
base=ROOT/'assets/loteria'; output=ROOT/'artifacts'; output.mkdir(exist_ok=True)
cards=json.loads((base/'manifest.json').read_text(encoding='utf8'))
errors=[]; report=[]; missing=[]
if len(cards)!=54 or sorted(c['id'] for c in cards)!=list(range(1,55)): errors.append('Catalog must contain exactly IDs 1..54')
for c in cards:
    if c['number']!=c['id'] or not c['title'].strip(): errors.append(f'Invalid identity/title: {c["id"]}')
    for kind,expected in [('images',{'pixel','traditional'}),('audio',{'repo','loteriacard','generated-es','generated-en','generated-verses-es'})]:
        if set(c.get(kind,{}))!=expected: errors.append(f'Card {c["id"]}: expected {kind} sets {sorted(expected)}')
    for kind in ('images','audio'):
        for variant,relative in c[kind].items():
            p=(base/relative).resolve(); label=f'Card {c["id"]} - {c["title"]}: {relative}'
            if not p.is_relative_to(base.resolve()): errors.append('UNSAFE: '+label); continue
            if not p.exists(): missing.append('MISSING: '+label); continue
            if not p.stat().st_size: errors.append('EMPTY: '+label); continue
            info=dict(id=c['id'],kind=kind,variant=variant,path=relative,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
            try:
                if kind=='images':
                    with Image.open(p) as im: im.load(); info['size']=im.size
                else:
                    result=subprocess.run([ffmpeg,'-hide_banner','-i',str(p),'-af','volumedetect,silencedetect=noise=-45dB:d=0.15','-f','null','-'],capture_output=True,text=True)
                    if result.returncode: raise ValueError(result.stderr[-500:])
                    info['analysis']=result.stderr
                report.append(info)
            except Exception as e: errors.append('DECODE: '+label+' '+str(e))
effects=json.loads((base/'effects.json').read_text(encoding='utf8'))
for name,relative in effects.items():
    p=(base/relative).resolve()
    if not p.is_relative_to(base.resolve()): errors.append(f'UNSAFE effect: {name}'); continue
    if not p.exists(): missing.append(f'MISSING effect: {name}: {relative}'); continue
    result=subprocess.run([ffmpeg,'-v','error','-i',str(p),'-f','null','-'],capture_output=True,text=True)
    if result.returncode: errors.append(f'DECODE effect: {name}: {result.stderr}')
    else: report.append(dict(kind='effect',variant=name,path=relative,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
for kind,variants in [('images',('pixel','traditional')),('audio',('repo','loteriacard','generated-es','generated-en','generated-verses-es'))]:
    for variant in variants:
        paths=[c.get(kind,{}).get(variant) for c in cards]
        if len(set(paths))!=54: errors.append(f'Duplicate/missing paths in {kind}/{variant}')
        folder=base/kind/variant
        actual={p.resolve() for p in folder.iterdir() if p.is_file()} if folder.exists() else set()
        expected={(base/p).resolve() for p in paths if p}
        extras=actual-expected
        if extras: errors.append(f'Unexpected files in {kind}/{variant}: {sorted(str(p) for p in extras)}')
for variant in ('traditional','pixel'):
    sheet=Image.new('RGB',(1080,9*220),'#f5f0e5'); draw=ImageDraw.Draw(sheet)
    for i,c in enumerate(cards):
        x=(i%6)*180; y=(i//6)*220; p=base/c['images'][variant]
        if p.exists():
            with Image.open(p) as src:
                im=src.convert('RGBA'); im.thumbnail((150,180),Image.Resampling.NEAREST if variant=='pixel' else Image.Resampling.LANCZOS)
                sheet.paste(im,(x+(180-im.width)//2,y),im)
        draw.text((x+8,y+184),f'{c["id"]:02} {c["title"]}',fill='black')
    sheet.save(output/f'{variant}-contact-sheet.png')
(output/'asset-report.json').write_text(json.dumps(dict(decoded=report,missing=missing,errors=errors),ensure_ascii=False,indent=2),encoding='utf8')
print(f'Decoded: {len(report)}; missing: {len(missing)}; errors: {len(errors)}')
for line in errors+missing: print(line)
sys.exit(1 if errors or (missing and '--available-only' not in sys.argv) else 0)
