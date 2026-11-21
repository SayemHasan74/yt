from pathlib import Path
import datetime,json,subprocess,sys,traceback
ROOT=Path(__file__).resolve().parents[1];RUN=ROOT/'workspace/runs/run_20261121_revised_3';OUT=RUN/'clips/out';STATUS=RUN/'render_status.json'
def save(stage,**extra):
 d={'stage':stage,'updated':datetime.datetime.now().isoformat(timespec='seconds'),**extra};p=STATUS.with_suffix('.tmp');p.write_text(json.dumps(d,indent=2)+'\n');p.replace(STATUS);print(stage,flush=True)
try:
 pf=RUN/'clips/picks.json';picks=json.loads(pf.read_text())
 save('Rendering locally — no GPT worker',total=3)
 with (RUN/'render.log').open('w') as log:
  subprocess.run([sys.executable,str(ROOT/'gta6-clipper/batch.py'),str(pf),str(OUT)],cwd=RUN,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,check=True)
 files=[OUT/f'{i:02d}_{p["name"]}.mp4' for i,p in enumerate(picks,1)]
 if not all(p.exists() and p.stat().st_size>0 for p in files):raise RuntimeError('Not all three videos rendered; inspect render.log')
 for p,f in zip(picks,files):f.with_suffix('.txt').write_text(f'{p["title"]}\n{p["hashtags"]}\nCredit: {p["credit"]} ({p["source_url"]})\n')
 qc=json.loads((OUT/'qc.json').read_text()) if (OUT/'qc.json').exists() else []
 save('Finished — review before publishing',completed=3,total=3,files=[str(p) for p in files],qc=qc)
except Exception as e:traceback.print_exc();save('Failed — inspect render.log',error=str(e));raise
