"""Decode all extracted clips and package the three available recordings sets."""
import concurrent.futures,hashlib,json,pathlib,subprocess,sys,zipfile
root=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'downloads/python-tools'))
import imageio_ffmpeg
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
base=root/'assets/audio-packs/loteriacaller'
manifest=json.loads((base/'manifest.json').read_text(encoding='utf8'))
files=[r for r in manifest['files'] if r['status']=='downloaded']
def verify(r):
    p=(base/r['path']).resolve()
    if not p.is_relative_to(base.resolve()): raise ValueError('Unsafe path')
    if hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']: raise ValueError('Hash mismatch: '+r['path'])
    result=subprocess.run([ffmpeg,'-v','error','-i',str(p),'-f','null','-'],capture_output=True,text=True)
    if result.returncode: raise ValueError(r['path']+': '+result.stderr)
    return r['path']
for kind in ('names-es','names-en','verses-es'):
    selected=[r for r in files if r['kind']==kind]
    if sorted(r['number'] for r in selected)!=list(range(1,61)): raise ValueError('Incomplete or duplicate set: '+kind)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool: verified=list(pool.map(verify,files))
report=dict(decoded=len(verified),sets={k:sum(r['kind']==k for r in files) for k in ('names-es','names-en','verses-es')},unavailableNumbers=120,verification='SHA-256 and full audio decode; semantic mapping from source catalog, not a human listening review')
(base/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
out=root/'dist/voice-packs'; out.mkdir(parents=True,exist_ok=True)
for kind in ('names-es','names-en','verses-es','all'):
    with zipfile.ZipFile(out/f'loteriacaller-{kind}.zip','w',zipfile.ZIP_DEFLATED) as z:
        for r in files:
            if kind=='all' or r['kind']==kind: z.write(base/r['path'],r['path'])
        for name in ('SOURCES.md','manifest.json','verification.json'): z.write(base/name,name)
    with zipfile.ZipFile(out/f'loteriacaller-{kind}.zip') as z:
        if z.testzip(): raise ValueError('Corrupt ZIP: '+kind)
print(json.dumps(report))
