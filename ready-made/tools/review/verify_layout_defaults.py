"""Local geometry/encode regression: no AI calls, downloads, or re-rendering user clips."""
from pathlib import Path
import ast,json,sys,tempfile
import cv2,numpy as np
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];APP=ROOT/'gta6-clipper';sys.path.insert(0,str(APP))
for name in ('clip.py','reframe.py','formats.py'):ast.parse((APP/name).read_text())
import reframe as R
import clip as C
assert R.TOP_H==432 and R.stack_geom()['game']==(432,1488)
box=R.cam_box(500,300,100,1920,1080);assert abs((box[2]-box[0])/(box[3]-box[1])-1080/768)<.02
# A visible circle must remain circular inside a non-square webcam panel.
cam=np.full((240,400,3),180,np.uint8);cv2.circle(cam,(200,120),60,(0,0,255),-1)
panel=R.fit_facecam(cam);mask=(panel[:,:,2]>230)&(panel[:,:,1]<20)
y,x=np.where(mask);assert abs((x.max()-x.min())/(y.max()-y.min())-1)<.03
assert float(panel[:40].std())>10, 'Purple header must have gradient/glow detail'
# Full lower-panel cover uses uniform scale, without blur or padding bands.
f=np.zeros((1080,1920,3),np.uint8);cv2.rectangle(f,(950,530),(1050,630),(255,255,255),-1)
rect=(500,100,900,960);v=R.gameplay_view(f,rect,1488)
y,x=np.where(v[:,:,0]>230);expected=100*max(1080/1920,1488/1080)
assert abs((x.max()-x.min())-expected)<3
# The hook ends at the Short's end, not at three seconds.
a=C.ass([], 'PERSISTENT HOOK', 12, set(), 'classic');hook=next(l for l in a.splitlines() if l.startswith('Dialogue: 1,'))
assert '0:00:12.00' in hook,hook
# Exercise the actual stack encoder with deterministic layout analysis on four frames.
with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as td:
 td=Path(td);src=td/'source.mp4';dst=td/'stack.mp4'
 writer=cv2.VideoWriter(str(src),cv2.VideoWriter_fourcc(*'mp4v'),4,(960,540))
 for _ in range(4):
  frame=np.full((540,960,3),(90,110,130),np.uint8)
  frame[20:160,20:220]=cv2.resize(cam,(200,140));writer.write(frame)
 writer.release()
 encoder=lambda:['-c:v','libx264','-preset','ultrafast','-crf','16']
 with patch.object(R,'stack_runs',side_effect=AssertionError('Fixed stack must not auto-switch layouts')),patch.object(R,'reaction',return_value=None),patch.object(R,'clutter',return_value=[]),patch.object(R,'encoder',encoder):
  R.render_stack(src,dst,(20,20,220,160))
 cap=cv2.VideoCapture(str(dst));ok,frame=cap.read();cap.release()
 assert ok and frame.shape==(1920,1080,3)
 assert float(frame[:40].std())>10
 assert np.linalg.norm(frame[-10,540].astype(int)-np.array(R.PURPLE_BGR))>20, 'Bottom must contain actual video, not purple padding'
 # Keep tests separate from user-facing previews.
report={'result':'PASS','facecam_share':.225,'gameplay_share':.775,'gameplay_fit':'uniform cover without filler','facecam_fit':'contain, maximum 2x enlargement','hook':'full duration','checks':['Aspect preservation','Uniform cover scaling','Persistent ASS hook','Four-frame local stack encoding','Video fill reaches bottom edge without purple gap','Fixed stack never calls automatic full-screen switching'],'scope':'Synthetic local verification only; existing Shorts untouched; no AI calls or downloads.'}
(ROOT/'settings/layout-defaults-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
