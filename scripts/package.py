"""Package the already-published Windows app and record its contents."""
import pathlib,zipfile,hashlib,json,sys
root=pathlib.Path(__file__).resolve().parents[1]; folder=root/'dist'/(sys.argv[1] if len(sys.argv)>1 else 'Loteria')
folder=folder.resolve()
if not folder.is_relative_to((root/'dist').resolve()): raise SystemExit('Package folder must be inside dist')
if not (folder/'Loteria.exe').is_file(): raise SystemExit('Run scripts/publish.ps1 first')
target=root/'dist'/f'{folder.name}-Windows11.zip'
files=sorted(p for p in folder.rglob('*') if p.is_file())
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files: z.write(p,pathlib.Path(folder.name)/p.relative_to(folder))
with zipfile.ZipFile(target) as z:
    if z.testzip(): raise SystemExit('ZIP verification failed')
record=dict(package=target.name,bytes=target.stat().st_size,files=len(files),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),assets=dict(pixel=54,traditional=54,repo=54,loteriacard=54,generated_es=54,generated_en=54,generated_verses_es=54,effects=1))
(root/'dist'/('release.json' if folder.name=='Loteria' else f'{folder.name}-release.json')).write_text(json.dumps(record,indent=2),encoding='utf8')
print(json.dumps(record))
