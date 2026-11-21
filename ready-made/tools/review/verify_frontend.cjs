const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const acorn=require('acorn');const {JSDOM,VirtualConsole}=require('jsdom');
const root=path.resolve(__dirname,'../..'),html=fs.readFileSync(path.join(root,'gta6-clipper/app.html'),'utf8');
for(const m of html.matchAll(/<script>([\s\S]*?)<\/script>/g))acorn.parse(m[1],{ecmaVersion:'latest'});
const brand=JSON.parse(fs.readFileSync(path.join(root,'gta6-clipper/brand.example.json'),'utf8'));
const errors=[],calls=[],checks=[];
const vc=new VirtualConsole();vc.on('jsdomError',e=>{if(e.type!=='css-parsing')errors.push(e.message)});
const fixtures={
 '/api/runs':{runs:[]},'/api/library':{shorts:[]},'/api/schedule':[],
 '/api/brand':{brand,fonts:[]},'/api/lang':{lang:'en'},'/api/published':{total:0,by_platform:{},by_day:{}},
 '/api/connections':{twitch:{ok:true,steps:[]},youtube:{ok:true,steps:[]},kick:{ok:true,steps:[]},blotato:{ok:false,has_key:false,signup_url:'https://blotato.com/',steps:[]}},
 '/api/hunt':[], '/api/streamers':{streamers:[],langs:['en']},'/api/jobs':[], '/api/autopilot':{error:'Not configured in this UI check'},
 '/api/ai':{current:'codex',providers:[{id:'codex',label:'Codex CLI',installed:true,can_run_tools:true,cmd_preview:'codex exec'},{id:'none',label:'No AI',installed:true,can_run_tools:false}]},
 '/api/pickmode':{mode:'smart',live_mode:'free',live_cap:4,estimates:{},info:{},live_info:{}},
 '/api/yt/status':{has_key:false,has_oauth:false,signed_in:false},
 '/api/themes':JSON.parse(fs.readFileSync(path.join(root,'gta6-clipper/themes.json'),'utf8'))
};
const dom=new JSDOM(html,{url:'http://localhost:8765/?noob=1',runScripts:'dangerously',pretendToBeVisual:true,virtualConsole:vc,beforeParse(w){
 w.localStorage.setItem('clipper_ob','1');
 w.HTMLDialogElement.prototype.showModal=function(){this.setAttribute('open','')};
 w.HTMLDialogElement.prototype.close=function(){this.removeAttribute('open')};
 w.HTMLElement.prototype.scrollIntoView=function(){};
 w.setInterval=()=>0;w.clearInterval=()=>{};
 w.fetch=async(url,options={})=>{
  calls.push({url:String(url),method:options.method||'GET',...(options.body?{body:JSON.parse(options.body)}:{})});
  if((options.method||'GET')==='POST'){
   assert.equal(String(url),'/api/newrun');const body=JSON.parse(options.body);assert.equal(body.dry,true);assert.equal(body.ai,'codex');return {json:async()=>({error:'Preview captured by test; nothing started'})};
  }
  assert.ok(String(url).startsWith('/api/'),'Only local API requests allowed');
  const p=String(url).split('?')[0];assert.ok(p in fixtures,'Unexpected API path: '+p);
  return {json:async()=>fixtures[p]};
 };
 w.addEventListener('error',e=>errors.push(String(e.error||e.message)));
}});
const wait=()=>new Promise(r=>setTimeout(r,100));
(async()=>{
 await wait();const d=dom.window.document;
 assert.equal(d.title,'Shorts Studio');assert.ok(d.querySelector('#main button'));
 assert.equal(d.querySelector('#np'),null);assert.equal(d.querySelector('#nu'),null);assert.equal(d.querySelector('#blr'),null);
 checks.push('Dashboard boots with neutral logo and no author/promotion buttons');
 d.querySelector('#st').click();await wait();
 assert.ok(d.querySelector('#set').hasAttribute('open'));assert.ok(d.querySelector('#aisec').textContent.includes('Codex'));
 assert.ok(d.querySelector('#set_pick [data-pm="free"]'));assert.ok(d.querySelector('#set_pick [data-pm="smart"]'));
 assert.equal(d.querySelector('#su_c'),null);assert.equal(d.querySelector('#prop'),null);
 checks.push('Settings and AI/No AI controls render without removed update/feedback widgets');
 dom.window.eval('setLang("fr",false);fillSet()');await wait();
 dom.window.eval('setLang("en",false);fillSet()');await wait();
 checks.push('Language switching and settings still render');
 d.querySelector('#set').close();d.querySelector('[data-v=new]').click();await wait();
 assert.ok(d.querySelector('#n_go'));assert.ok(d.querySelector('#n_ai_cur'));
 assert.equal(d.querySelector('#n_ai').value,'codex');
 dom.window.eval('refAI()');assert.equal(d.querySelector('#n_ai').value,'codex');
 // Reproduce the old hidden-selector mismatch: requests must still use the displayed provider.
 d.querySelector('#n_ai').innerHTML='<option selected>claude</option>';
 d.querySelector('#n_src').value='https://www.youtube.com/live/lBrGiDG_BVc';
 d.querySelector('#n_cnt').value='5';d.querySelector('#n_win').value='2:00:00-2:30:00';
 d.querySelector('#n_dry').click();await wait();
 const preview=calls.find(c=>c.url==='/api/newrun');assert.ok(preview);
 checks.push('Cold startup selects saved Codex; dry-run request stays Codex even with a stale hidden Claude selector');
 checks.push('Make Shorts form still renders without running an AI or processing media');
 assert.deepEqual(errors,[]);assert.ok(!calls.some(c=>/update|proposals|changelog/.test(c.url)));
 const report={result:'PASS',checks,api_requests:calls.length,scope:'Mocked local API and DOM navigation; no real downloads, AI, rendering or publishing.'};
 fs.writeFileSync(path.join(root,'settings/local-fork-ui-validation.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));dom.window.close();
})().catch(e=>{console.error(e);console.error(errors);dom.window.close();process.exitCode=1});
