// Reuses tools/pagemotion's frame recorder in one Chrome. Compare on the same
// machine with interleaved old/new runs; these are browser timings, not devices.
import {createRequire} from 'node:module';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const out=resolve('build/chip-3d-quality');mkdirSync(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true,args:['--enable-webgl','--use-angle=metal']});
const results=[];
try{
 const context=await browser.newContext({viewport:{width:1280,height:1000},deviceScaleFactor:1,reducedMotion:'reduce'});
 await context.addInitScript({content:readFileSync('tools/pagemotion/recorder.js','utf8')});
 const page=await context.newPage();
 for(let round=0;round<2;round++)for(const version of ['before','after']){
  await page.goto('file://'+resolve(version==='before'?'build/chip-3d-before.html':'docs/reports/chip-3d.html')+'?qa#finfet');
  await page.waitForTimeout(700);await page.locator('#rotateButton').click();
  await page.waitForTimeout(700);await page.evaluate(()=>{window.__LOG=[];window.__LOAF=[];});
  const samples=await page.evaluate(()=>new Promise(resolve=>{const samples=[],start=performance.now();function sample(){if(window.__chip3d)samples.push(window.__chip3d.debug());if(performance.now()-start<3500)requestAnimationFrame(sample);else resolve(samples);}requestAnimationFrame(sample);}));
  const frames=await page.evaluate(()=>window.__LOG.map(x=>x[0]));
  const intervals=frames.slice(1).map((x,i)=>x-frames[i]).sort((a,b)=>a-b);
  if(version==='after'){
   assert.ok(samples.length>20,'animation produces frames');
   const first=samples[0];assert.ok(samples.at(-1).yaw!==first.yaw,'auto orbit advances');
   assert.ok(samples.every(s=>Math.abs(s.scale-first.scale)<1e-8),'auto orbit preserves zoom');
   assert.ok(samples.every(s=>s.labels.every((l,i)=>l.x===first.labels[i].x&&l.y===first.labels[i].y)),'labels stable on every sampled frame');
  }
  const r={version,round,frames:intervals.length,medianMs:intervals[Math.floor(intervals.length*.5)],p95Ms:intervals[Math.floor(intervals.length*.95)],over25ms:intervals.filter(x=>x>25).length,maxMs:Math.max(...intervals),scaleDrift:version==='after'?Math.max(...samples.map(s=>Math.abs(s.scale-samples[0].scale))):null};
  results.push(r);console.log(JSON.stringify(r));
 }
 // A full keyboard rotation samples all label slots and zoom after real input.
 await page.goto('file://'+resolve('docs/reports/chip-3d.html')+'?qa#channel');await page.waitForTimeout(300);
 const sweep=await page.evaluate(()=>new Promise(resolve=>{const rows=[],c=document.getElementById('sceneCanvas');function step(){c.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));requestAnimationFrame(()=>{rows.push(window.__chip3d.debug());if(rows.length<64)step();else resolve(rows);});}step();}));
 assert.ok(sweep.every(s=>Math.abs(s.scale-sweep[0].scale)<1e-8),'full-turn scale stability');
 assert.ok(sweep.every(s=>s.labels.every((l,i)=>l.x===sweep[0].labels[i].x&&l.y===sweep[0].labels[i].y)),'full-turn label stability');
 writeFileSync(resolve(out,'motion-results.json'),JSON.stringify({results,fullTurnSamples:sweep.length,fullTurnLabelDrift:0},null,2));
}finally{await browser.close();}
