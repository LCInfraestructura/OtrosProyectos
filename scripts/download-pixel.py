"""Use the publisher's free download flow; retain original ZIP locally."""
import urllib.request,urllib.parse,http.cookiejar,re,json,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
url='https://josemariagarciamarquez.itch.io/sprites-loteria'
session=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
session.addheaders=[('User-Agent','Mozilla/5.0')]
page=session.open(url,timeout=25).read().decode()
token=re.search(r'name="csrf_token"\s+value="([^"]+)"',page).group(1)
request=urllib.request.Request(url+'/download_url',data=urllib.parse.urlencode({'csrf_token':token}).encode(),headers={'Referer':url,'X-Requested-With':'XMLHttpRequest'})
result=json.load(session.open(request,timeout=25))
download=result.get('url')
if not download: raise SystemExit('Manual download required: mexican-loteria-sprites.zip from '+url)
page=session.open(download,timeout=25).read().decode()
(root/'downloads/pixel-download.html').write_text(page,encoding='utf-8')
upload=re.search(r'data-upload_id="(\d+)"',page).group(1)
token=re.search(r'name="csrf_token"\s+value="([^"]+)"',page).group(1)
request=urllib.request.Request(url+'/file/'+upload+'?source=game_download',data=urllib.parse.urlencode({'csrf_token':token}).encode(),headers={'Referer':download,'X-Requested-With':'XMLHttpRequest'})
result=json.load(session.open(request,timeout=25))
if not result.get('url'): raise SystemExit('Download did not return a file URL')
data=session.open(result['url'],timeout=30).read()
(root/'downloads/mexican-loteria-sprites.zip').write_bytes(data)
print(f'Original ZIP downloaded: {len(data)} bytes')
