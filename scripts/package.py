"""Package the already-published Windows app and record its contents."""
import pathlib,zipfile,hashlib,json
root=pathlib.Path(__file__).resolve().parents[1]; folder=root/'dist/Loteria'
if not (folder/'Loteria.exe').is_file(): raise SystemExit('Run scripts/publish.ps1 first')
target=root/'dist/Loteria-Windows11.zip'
files=sorted(p for p in folder.rglob('*') if p.is_file())
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files: z.write(p,pathlib.Path('Loteria')/p.relative_to(folder))
with zipfile.ZipFile(target) as z:
    if z.testzip(): raise SystemExit('ZIP verification failed')
record=dict(package=target.name,bytes=target.stat().st_size,files=len(files),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),assets=dict(pixel=54,traditional=54,repo=54,loteriacard=54,effects=1,radioteca=0),radioteca='Pending: source download timeouts')
(root/'dist/release.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print(json.dumps(record))
