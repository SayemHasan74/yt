"""Local-only revised renders. Uses saved selections; never invokes Codex or other cloud AI."""
from pathlib import Path
import datetime,json,os,subprocess,sys,traceback
import yt_dlp
ROOT=Path(__file__).resolve().parents[1];APP=ROOT/'gta6-clipper'
OLD=ROOT/'workspace/runs/run_20261121_004126'
RUN=ROOT/'workspace/runs/run_20261121_revised_3'
CLIPS=RUN/'clips';OUT=CLIPS/'out';SRC=CLIPS/'src'
for p in (OUT,SRC):p.mkdir(parents=True,exist_ok=True)
STATUS=RUN/'render_status.json'
def status(stage,**extra):
 d={'stage':stage,'updated':datetime.datetime.now().isoformat(timespec='seconds'),**extra}
 t=STATUS.with_suffix('.tmp');t.write_text(json.dumps(d,indent=2)+'\n');t.replace(STATUS)
 print(stage,extra,flush=True)
def run(cmd,log):
 with log.open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,stdin=subprocess.DEVNULL)
FF=str(ROOT/'tools/runtime/bin/ffmpeg')
URL='https://www.youtube.com/live/lBrGiDG_BVc'
NAMES=['lacy_kind_of','lacy_chat_rating','lacy_family_fund']
try:
 oldp=json.loads((OLD/'clips/picks.json').read_text());picks=[next(p for p in oldp if p['name']==n) for n in NAMES]
 status('Preparing source downloads',completed=0,total=3)
 ydl_opts={'quiet':True,'no_warnings':True,'format':'bv[height<=1080][vcodec^=avc1]/bv[height<=1080]/b[height<=1080]'}
 with yt_dlp.YoutubeDL(ydl_opts) as ydl:info=ydl.extract_info(URL,download=False)
 video_url=info['url'];headers=''.join(f'{k}: {v}\r\n' for k,v in info.get('http_headers',{}).items())
 original=json.loads((OLD/'clips/src/lBrGiDG_BVc_2000023000_refined.json').read_text())
 # Original coarse transcript has a later timestamp for the final rating reply.
 coarse=json.loads((OLD/'clips/src/lBrGiDG_BVc_2000023000.json').read_text())
 prepared=[]
 for index,p0 in enumerate(picks,1):
  p=dict(p0);start=float(p['start']);end=float(p['end'])
  if p['name']=='lacy_chat_rating':end=8832.0
  elif p['name']=='lacy_kind_of':end=8661.0
  a=max(7200,start-1);b=min(9000,end+1);asset=SRC/(p['name']+'.mp4');video=SRC/(p['name']+'_video.mp4')
  status('Downloading selected video section',clip=index,name=p['name'],completed=index-1,total=3)
  if not asset.exists():
   run([FF,'-y','-nostdin','-loglevel','error','-headers',headers,'-ss',str(a),'-i',video_url,'-t',str(b-a),'-map','0:v:0','-an','-c:v','libx264','-preset','veryfast','-crf','14',str(video)],CLIPS/(p['name']+'_download.log'))
   run([FF,'-y','-nostdin','-loglevel','error','-i',str(video),'-ss',str(a-7200),'-i',str(OLD/'clips/src/lBrGiDG_BVc_2000023000.m4a'),'-t',str(b-a),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k',str(asset)],CLIPS/(p['name']+'_mux.log'))
   video.unlink(missing_ok=True)
  tx=SRC/(p['name']+'.json');segments=[]
  for seg in original['segments']:
   words=[dict(w, s=round(w['s']-a,3),e=round(w['e']-a,3)) for w in seg.get('words',[]) if a<=w['s'] and w['e']<=b]
   if words:segments.append(dict(start=words[0]['s'],end=words[-1]['e'],text=seg['text'],words=words))
  if p['name']=='lacy_chat_rating':
   # Preserve the complete original final reply, rather than an early refined end.
   final=next((s for s in coarse['segments'] if 8827<s['start']<8829),None)
   if final:
    segments=[s for s in segments if s['start']+a<8827.9]
    words=[dict(w,s=round(w['s']-a,3),e=round(w['e']-a,3)) for w in final.get('words',[])]
    if words:segments.append(dict(start=words[0]['s'],end=words[-1]['e'],text=final['text'],words=words))
  tx.write_text(json.dumps({'lang':'en','segments':segments},indent=1))
  tx.with_suffix('.meta.json').write_text(json.dumps({'url':URL,'title':info.get('title',''),'channel':p['credit']}))
  p.update(url=str(asset),source_url=URL,transcript=str(tx),start=start-a,end=end-a,layout='stack',facecam_box=[0,0,.26,.26],again=True,preserve_ending=True,exact_end=True,fillers=False,lift=False,meme='none')
  p.pop('music',None)
  if p.get('parts'):p['parts']=[dict(q,start=q['start']-a,end=q['end']-a) for q in p['parts']]
  prepared.append(p)
 pf=CLIPS/'picks.json';pf.write_text(json.dumps(prepared,indent=2))
 status('Rendering three selected Shorts locally',completed=0,total=3)
 run([sys.executable,str(APP/'batch.py'),str(pf),str(OUT)],RUN/'render.log')
 expected=[OUT/f'{i:02d}_{p["name"]}.mp4' for i,p in enumerate(prepared,1)]
 if not all(p.exists() and p.stat().st_size>0 for p in expected):raise RuntimeError('One or more selected Shorts failed; inspect render.log')
 for p,out in zip(prepared,expected):
  out.with_suffix('.txt').write_text(f'{p["title"]}\n{p["hashtags"]}\nCredit: {p["credit"]} ({URL})\n')
 results=json.loads((OUT/'qc.json').read_text()) if (OUT/'qc.json').exists() else []
 status('Finished — review before publishing',completed=3,total=3,files=[str(p) for p in expected],qc=results)
except Exception as e:
 traceback.print_exc();status('Failed — inspect the local log',error=str(e));raise
