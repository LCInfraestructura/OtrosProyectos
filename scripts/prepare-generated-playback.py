"""Build PCM playback copies with 500 ms lead-in; preserve source MP3s in audio-packs.
The speech PCM is unchanged after decoding/resampling; no tempo/pitch filters.
"""
import hashlib,json,pathlib,subprocess,sys,wave
root=pathlib.Path(__file__).resolve().parents[1]; base=root/'assets/loteria'
sys.path.insert(0,str(root/'downloads/python-tools'))
import imageio_ffmpeg
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
pack=root/'assets/audio-packs/loteriacaller'
source=json.loads((pack/'manifest.json').read_text(encoding='utf8'))
catalog=json.loads((base/'manifest.json').read_text(encoding='utf8'))
variants={'generated-es':'names-es','generated-en':'names-en','generated-verses-es':'verses-es'}
report=[]
for c in catalog:
    for variant,kind in variants.items():
        record=next(r for r in source['files'] if r['number']==c['id'] and r['group']=='classic' and r['kind']==kind)
        original=pack/record['path']
        if hashlib.sha256(original.read_bytes()).hexdigest()!=record['sha256']: raise ValueError('Source changed')
        pcm=subprocess.run([ffmpeg,'-v','error','-i',str(original),'-ar','48000','-ac','1','-f','s16le','-'],capture_output=True,check=True).stdout
        lead=bytes(48000) # 0.5 seconds * 48,000 samples/second * 2 bytes/sample
        relative=f'audio/{variant}/{c["id"]:02}-{c["slug"]}.wav'
        target=base/relative; target.parent.mkdir(parents=True,exist_ok=True)
        with wave.open(str(target),'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000); w.writeframes(lead+pcm)
        with wave.open(str(target),'rb') as w:
            samples=w.readframes(w.getnframes())
            if samples[:len(lead)]!=lead or samples[len(lead):]!=pcm: raise ValueError('Speech samples changed')
        c['audio'][variant]=relative
        obsolete=target.with_suffix('.mp3').resolve()
        if not obsolete.is_relative_to((base/'audio').resolve()): raise ValueError('Unsafe removal path')
        if obsolete.exists(): obsolete.unlink() # Only redundant imported copy; original MP3 is retained in pack.
        report.append(dict(id=c['id'],variant=variant,source=record['url'],sourcePath=record['path'],sourceSha256=record['sha256'],target=relative,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),leadInSeconds=0.5,speechSeconds=len(pcm)/96000,playbackSeconds=(len(lead)+len(pcm))/96000,speechSamplesVerified=True))
(base/'manifest.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(base/'generated-provenance.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(f'Prepared and sample-verified {len(report)} PCM voices with 500 ms lead-in. Original MP3s preserved.')
