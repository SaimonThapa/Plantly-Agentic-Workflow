import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {mkdtemp,mkdir,writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
// Run with the frontend server already running. Uses installed Chrome, no dependencies.
const profile=await mkdtemp(path.join(tmpdir(),'plantly-browser-'));
const child=spawn(process.env.BROWSER_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe',['--headless=new','--remote-debugging-port=0','--user-data-dir='+profile,'--no-first-run','--disable-extensions','--disable-gpu','about:blank'],{windowsHide:true,stdio:['ignore','ignore','pipe']});
let ws;
try{
 const endpoint=await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('BLOCKED_BY_INFRA: browser startup timeout')),15000);child.on('error',reject);child.stderr.on('data',b=>{const m=b.toString().match(/DevTools listening on (ws:\/\/\S+)/);if(m){clearTimeout(timer);resolve(m[1]);}});});

 ws=new WebSocket(endpoint);await new Promise(r=>ws.addEventListener('open',r,{once:true}));
 let id=0;const pending=new Map(),errors=[];
 ws.addEventListener('close',()=>{for(const p of pending.values())p.reject(Error('BLOCKED_BY_INFRA: browser automation connection closed'));pending.clear();});
 ws.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(m.error.message)):p.resolve(m.result);}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text);});
 let sessionId; const send=(method,params={})=>new Promise((resolve,reject)=>{pending.set(++id,{resolve,reject});ws.send(JSON.stringify({id,method,params,sessionId}));});
 const run=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});assert.ok(!r.exceptionDetails,JSON.stringify(r.exceptionDetails));return r.result.value;};
 const wait=()=>new Promise(r=>setTimeout(r,350));
 const key=async(key,code)=>{await send('Input.dispatchKeyEvent',{type:'keyDown',key,code:key,windowsVirtualKeyCode:code});await send('Input.dispatchKeyEvent',{type:'keyUp',key,code:key,windowsVirtualKeyCode:code});await wait();};
 const target=await send('Target.createTarget',{url:'about:blank'});sessionId=(await send('Target.attachToTarget',{targetId:target.targetId,flatten:true})).sessionId;
 await send('Runtime.enable');await send('Page.enable');await send('Page.navigate',{url:process.env.BASE_URL||'http://127.0.0.1:3000'});
 for(let i=0;i<80;i++){if(await run('document.readyState==="complete" && !!document.querySelector(".benefit-trigger")'))break;await wait();}
 const shots=path.join(tmpdir(),'plantly-f010-browser');await mkdir(shots,{recursive:true});
 for(const [width,height] of [[320,700],[390,844],[768,1024],[1440,900],[1920,1080]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});await wait();
  assert.ok(await run('document.documentElement.scrollWidth<=innerWidth'),'Overflow '+width);
  assert.equal(await run('document.querySelectorAll("h1").length'),1);
  assert.ok(await run('[...document.querySelectorAll("a")].filter(a=>a.hash).every(a=>document.getElementById(a.hash.slice(1)))'));
  assert.ok(await run('[...document.images].every(i=>i.complete&&i.naturalWidth>0)'),'Images '+width);
  await run('scrollTo(0,0)');await wait();const s=await send('Page.captureScreenshot',{format:'png'});await writeFile(path.join(shots,width+'.png'),Buffer.from(s.data,'base64'));
  console.log('PASS layout '+width+'x'+height);
 }
 const state=()=>run('[...document.querySelectorAll(".benefit-trigger")].map(b=>b.getAttribute("aria-expanded"))');
 assert.deepEqual(await state(),['true','false','false']);
 await run('document.querySelectorAll(".benefit-trigger")[1].focus()');await key('Enter',13);assert.deepEqual(await state(),['false','true','false']);
 await run('document.querySelector(".carousel-controls button:last-child").click()');await wait();assert.ok(await run('document.querySelector(".carousel-rail").scrollLeft>0'));
 assert.notEqual(await run('document.querySelector(".carousel-track span").style.transform'),'translateX(0%)');
 await run('document.querySelectorAll(".benefit-trigger")[2].click()');await wait();assert.equal(await run('document.querySelector(".carousel-rail").scrollLeft'),0);
 await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:false});
 await run('document.querySelector(".menu-toggle").click()');await wait();assert.equal(await run('document.querySelector(".menu-toggle").getAttribute("aria-expanded")'),'true');
 await run('document.querySelector(".menu-toggle").focus()');await key('Escape',27);assert.equal(await run('document.querySelector(".menu-toggle").getAttribute("aria-expanded")'),'false');
 await run('document.querySelector(".menu-toggle").click()');await wait();await run('document.querySelector("#mobile-menu a").click()');await wait();assert.equal(await run('location.hash'),'#mission');assert.equal(await run('document.querySelector(".menu-toggle").getAttribute("aria-expanded")'),'false');
 assert.ok(await run('document.querySelector(".trial-pill").disabled'));assert.equal(await run('document.querySelectorAll("form").length'),0);
 await send('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});assert.ok(await run('matchMedia("(prefers-reduced-motion: reduce)").matches'));assert.equal(await run('getComputedStyle(document.querySelector(".carousel-rail")).scrollBehavior'),'auto');
 assert.deepEqual(errors,[]);console.log('PASS keyboard accordion, carousel progress/reset, mobile menu, honest CTA, reduced motion. Screenshots: '+shots);
}finally{ws?.close();child.kill();}




