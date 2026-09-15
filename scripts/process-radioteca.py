"""Analyze originals and optionally normalize without destroying source recordings.
Requires a complete set of 54 original tracks. Defaults to analysis only.
Run with --normalize after inspecting the analysis report; trims no speech/silence.
"""
import pathlib,json,subprocess,sys,re
root=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'downloads/python-tools'))
import imageio_ffmpeg
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe(); base=root/'assets/loteria'
cards=json.loads((base/'manifest.json').read_text(encoding='utf8'))
originals=root/'downloads/radioteca-originals'; output=root/'artifacts'; output.mkdir(exist_ok=True)
missing=[c for c in cards if not (originals/pathlib.Path(c['audio']['radioteca']).name).exists()]
if missing: raise SystemExit('Missing Radioteca originals: '+', '.join(str(c['id']) for c in missing))
report=[]
for c in cards:
    source=originals/pathlib.Path(c['audio']['radioteca']).name
    result=subprocess.run([ffmpeg,'-hide_banner','-i',str(source),'-af','silencedetect=noise=-45dB:d=0.15,loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    entry=dict(id=c['id'],source=str(source),analysis=result.stderr,normalized=False)
    if '--normalize' in sys.argv:
        stats=json.loads(re.findall(r'\{[^{}]+\}',result.stderr)[-1])
        filt='loudnorm=I=-18:TP=-1.5:LRA=11:linear=true:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}'.format(**stats)
        target=base/c['audio']['radioteca']; target.parent.mkdir(parents=True,exist_ok=True)
        temp=target.with_suffix('.processing.mp3')
        subprocess.run([ffmpeg,'-v','error','-y','-i',str(source),'-af',filt,'-ar','44100','-codec:a','libmp3lame','-q:a','2',str(temp)],check=True)
        subprocess.run([ffmpeg,'-v','error','-i',str(temp),'-f','null','-'],check=True)
        temp.replace(target); entry['normalized']=True
    report.append(entry)
(output/'radioteca-processing.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('Analysis saved. No automatic silence trimming is performed; inspect before deciding trims.')
