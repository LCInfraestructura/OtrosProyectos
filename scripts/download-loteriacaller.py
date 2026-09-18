"""Extract publicly served recordings referenced by loteriacaller.com's app.js.
Does not execute downloaded JavaScript or generate browser/TTS voices.
"""
import concurrent.futures,datetime,hashlib,json,pathlib,re,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='https://www.loteriacaller.com/'
OUT=ROOT/'assets/audio-packs/loteriacaller'
def fetch(url):
    request=urllib.request.Request(url,headers={'User-Agent':'LoteriaLC asset importer'})
    with urllib.request.urlopen(request,timeout=25) as response:
        data=response.read()
        if 'text/html' in response.headers.get('Content-Type',''): raise ValueError('Unexpected HTML instead of asset')
        return data
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source=fetch(BASE+'js/cards.js').decode('utf8')
    cards=[]
    for line in source.splitlines():
        if not re.match(r'\s*\{\s*id:',line): continue
        entry={}
        for field in ('id','es','en','group','dicho'):
            match=re.search(r'\b'+field+r':\s*("(?:[^"\\]|\\.)*")',line)
            if match: entry[field]=json.loads(match.group(1))
        entry['number']=int(re.search(r'\bnumber:\s*(\d+)',line).group(1))
        cards.append(entry)
    if len(cards)<54 or len({c['id'] for c in cards})!=len(cards): raise ValueError('Unexpected source catalog')
    tasks=[]
    for c in cards:
        stem=f'{c["number"]:02}-{c["id"]}'
        for lang in ('es','en'):
            tasks.append((c,f'names-{lang}',f'audio/{lang}/{c["id"]}.mp3',f'names-{lang}/{stem}.mp3'))
            tasks.append((c,f'numbers-{lang}',f'audio/{lang}/num-{c["number"]}.mp3',f'numbers-{lang}/{c["number"]:02}.mp3'))
        if c.get('dicho'): tasks.append((c,'verses-es',f'audio/dicho/{c["id"]}.mp3',f'verses-es/{stem}.mp3'))
    def download(task):
        c,kind,remote,relative=task; target=OUT/relative
        record=dict(number=c['number'],id=c['id'],group=c['group'],kind=kind,path=relative,url=BASE+remote)
        try:
            data=target.read_bytes() if target.exists() else fetch(BASE+remote)
            if not data: raise ValueError('Empty file')
            target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
            record.update(status='downloaded',bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        except Exception as e: record.update(status='unavailable',error=str(e))
        return record
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: records=list(pool.map(download,tasks))
    report=dict(source=BASE,retrieved=datetime.datetime.now(datetime.timezone.utc).isoformat(),cards=cards,files=records)
    (OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    for kind in sorted({r['kind'] for r in records}):
        group=[r for r in records if r['kind']==kind]; good=[r for r in group if r['status']=='downloaded']
        print(f'{kind}: {len(good)}/{len(group)} downloaded')
    for r in records:
        if r['status']!='downloaded': print(f'{r["path"]}: {r["error"]}')
if __name__=='__main__': main()
