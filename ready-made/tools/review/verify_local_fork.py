"""Verify author-service removal without running AI, downloads or video processing."""
from pathlib import Path
import ast, importlib.util,json,os,sys,tempfile,urllib.request
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];APP=ROOT/'gta6-clipper';sys.path.insert(0,str(APP))
checks=[]
def ok(name):checks.append(name)
for p in APP.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
ok('All Python application files parse')
for p in APP.rglob('*.json'):
 if '.venv' not in p.parts:json.loads(p.read_text())
ok('All shipped JSON configuration parses')
assert not (APP/'update.py').exists()
ok('Upstream updater module removed')
html=(APP/'app.html').read_text()
for value in ('guide.nocodehack','nocodehack','BLACKFRIDAY2026','partner link','/api/update','/api/proposals','/api/changelog','updCheck','wnOnce','<button id=np','<button id=nu'):
 assert value.lower() not in html.lower(),value
ok('Interface has no author branding, feedback, updater requests or affiliate promotion')
with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as td:
 td=Path(td);env_file=td/'clipper.env';env_file.write_text('AI=codex\nPICK_MODE=smart\n')
 # Any unexpected outgoing request fails the review instead of contacting a server.
 with patch.dict(os.environ,CLIPPER_ENV_FILE=str(env_file)),patch.object(urllib.request,'urlopen',side_effect=AssertionError('Unexpected outgoing request')):
  import app
  app.WS=td;app.STATE=td/'app_state.json'
  assert app.cur_ai()=='codex' and app.pick_cfg()['mode']=='smart'
  assert app.current_version()=='1.0.14-local.1'
  for method,route in [('GET','/api/update/check'),('POST','/api/update/apply'),('GET','/api/changelog'),('POST','/api/proposals')]:
   code,body=app.api56(method,route,{},{});assert code==410,(route,code)
  assert app.connections()['blotato']['signup_url']=='https://blotato.com/'
  assert not list(td.glob('proposals*'))
  assert all(t['name']!='nocodehack' for t in app.themes_api()['themes']) if hasattr(app,'themes_api') else True
  b=app.brand_norm({});assert b['watermark']==''
  from http.server import ThreadingHTTPServer
  import threading,http.client
  server=ThreadingHTTPServer(('127.0.0.1',0),app.H);app.PORT=server.server_port
  worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
  try:
   def request(method,path,body=None,token=None):
    c=http.client.HTTPConnection('127.0.0.1',app.PORT,timeout=5)
    headers={}
    if token:headers['X-App']=token
    if body is not None:headers['Content-Type']='application/json'
    c.request(method,path,json.dumps(body) if body is not None else None,headers)
    r=c.getresponse();data=r.read();status=r.status;c.close();return status,data
   status,body=request('GET','/');assert status==200 and b'Shorts Studio' in body and b'__TOKEN__' not in body
   for route in ('/api/update/check','/api/changelog'):
    assert request('GET',route)[0]==410
   for route in ('/api/update/apply','/api/proposals'):
    assert request('POST',route,{},app.TOKEN)[0]==410
   assert request('POST','/api/proposals',{})[0]==403
   assert request('GET','/api/themes')[0]==200
  finally:server.shutdown();server.server_close();worker.join()
 ok('Local dashboard serves; removed routes return 410 without any outgoing request')
 ok('Existing request-token protection remains active')
 ok('Codex/Smart selection and neutral branding defaults preserved')
report={'result':'PASS','checks':checks,'scope':'Source/config and local API checks only; no AI, video rendering, publishing or scheduling.'}
(ROOT/'settings/local-fork-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
