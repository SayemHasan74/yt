from pathlib import Path
import subprocess,os
root=Path(__file__).resolve().parents[1];run=root/'workspace/runs/run_20261121_revised_3';run.mkdir(parents=True,exist_ok=True)
py=root/'gta6-clipper/.venv/bin/python'
log=(run/'local-render.log').open('a')
p=subprocess.Popen([str(py),'-u',str(root/'tools/render_selected_three.py')],stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True,cwd=str(run),env=os.environ.copy())
(run/'render.pid').write_text(str(p.pid)+'\n');print('Started local render PID',p.pid);print(run)
