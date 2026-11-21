"""Detached local rendering task. No agent, cloud AI, transcription or downloads."""
from pathlib import Path
import datetime,json,os,shutil,subprocess,sys,traceback
ROOT=Path(__file__).resolve().parents[1]
SPEC=json.loads(Path(sys.argv[1]).read_text());RUN=Path(SPEC['run']);DEST=Path(SPEC['destination']);OUT=RUN/'clips/out'
def save(stage,**extra):
 d={'stage':stage,'updated':datetime.datetime.now().isoformat(timespec='seconds'),'destination':str(DEST),'completed':extra.get('current', 0),'total':len(SPEC['filenames']),**extra}
 p=RUN/'render_status.json';t=p.with_suffix('.tmp');t.write_text(json.dumps(d,indent=2)+'\n');t.replace(p);print(stage,flush=True)
try:
 save('Rendering requested videos locally — no GPT worker')
 with (RUN/'render.log').open('w') as log:
  subprocess.run([sys.executable,str(ROOT/'gta6-clipper/batch.py'),str(RUN/'clips/picks.json'),str(OUT)],cwd=RUN,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,check=True)
 picks=json.loads((RUN/'clips/picks.json').read_text())
 checks=json.loads((OUT/'qc.json').read_text()) if (OUT/'qc.json').exists() else []
 for i,(p,name) in enumerate(zip(picks,SPEC['filenames']),1):
  src=OUT/f'{i:02d}_{p["name"]}.mp4'
  if not src.is_file():raise RuntimeError(f'Missing render: {src.name}; see render.log')
  info=json.loads(subprocess.check_output([str(ROOT/'tools/runtime/bin/ffprobe'),'-v','error','-show_entries','stream=codec_type,width,height:format=duration','-of','json',str(src)],text=True))
  video=next((s for s in info['streams'] if s['codec_type']=='video'),{})
  if (video.get('width'),video.get('height'))!=(1080,1920) or float(info['format']['duration'])<8 or not any(s['codec_type']=='audio' for s in info['streams']):raise RuntimeError(f'Invalid video/audio: {src.name}')
  subprocess.run([str(ROOT/'tools/runtime/bin/ffmpeg'),'-v','error','-i',str(src),'-f','null','-'],stdin=subprocess.DEVNULL,check=True)
  result=next((q for q in checks if q['file']==src.name),{})
  if result.get('status')=='FAIL':raise RuntimeError(f'{src.name} needs review: {result.get("fail")}')
  temp=RUN/(name+'.tmp');shutil.copy2(src,temp);os.replace(temp,DEST/name)
  save('Copying verified MP4s into clean folder',current=i)
 save('Finished — requested videos ready for your review',files=[str(DEST/n) for n in SPEC['filenames']],qc=checks,current=len(SPEC['filenames']))
except Exception as e:
 traceback.print_exc();save('Failed — inspect task log',error=str(e));raise
