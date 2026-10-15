// One browser, reused: visual checks plus real-input regressions for fixed zoom
// and fixed callouts. Run from the repo root with PLAYWRIGHT_MODULE if needed.
import {createRequire} from 'node:module';
import {mkdirSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const out=resolve('build/chip-3d-quality');mkdirSync(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true,args:['--enable-webgl','--use-angle=metal']});
const report=[];
try{
 const context=await browser.newContext({viewport:{width:1280,height:1000},deviceScaleFactor:1,reducedMotion:'reduce'});
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>{errors.push(e.message);console.log('PAGE ERROR: '+e.stack);});page.on('console',m=>{if(m.type()==='warning'||m.type()==='error')console.log(m.type()+': '+m.text());});
 const target=process.env.PAGE||'file://'+resolve('docs/reports/chip-3d.html');
 for(const width of [1280,390]){
  await page.setViewportSize({width,height:1000});
  for(const name of ['metal','finfet','fin','channel']){
   await page.goto(target+'?qa#'+name);
   await page.waitForFunction(()=>window.__chip3d?.debug()?.render?.calls>0||!document.getElementById('renderFallback').hidden,null,{timeout:20000});
   await page.waitForTimeout(400);
   const before=await page.evaluate(()=>({debug:window.__chip3d?.debug(),fallback:!document.getElementById('renderFallback').hidden,overflow:document.documentElement.scrollWidth>innerWidth}));
   assert.ok(before.debug,'viewer initialized');assert.equal(before.fallback,false,'WebGL available');assert.equal(before.overflow,false,'no horizontal overflow');
   await page.screenshot({path:resolve(out,`${name}-${width}.png`),fullPage:true});
   const bounds=await page.locator('#sceneCanvas').boundingBox();
   await page.mouse.move(bounds.x+bounds.width*.45,bounds.y+bounds.height*.45);await page.mouse.down();
   await page.mouse.move(bounds.x+bounds.width*.75,bounds.y+bounds.height*.6,{steps:20});await page.mouse.up();
   await page.waitForTimeout(120);
   const after=await page.evaluate(()=>window.__chip3d.debug());
   assert.ok(Math.abs(before.debug.scale-after.scale)<1e-8,'drag preserves target-plane magnification');
   assert.equal(before.debug.zoom,after.zoom,'drag preserves explicit zoom');
   const labelSlots=d=>d.labels.map(l=>[l.key,l.x,l.y,l.width,l.height]);
   assert.deepEqual(labelSlots(before.debug),labelSlots(after),'drag preserves label slots');
   await page.locator('#zoomIn').click();await page.waitForTimeout(80);
   const zoomed=await page.evaluate(()=>window.__chip3d.debug());
   assert.ok(zoomed.scale>after.scale*1.14,'explicit zoom changes scale');
   const primary={metal:'spread',finfet:'separation',fin:'finCount',channel:'gateDrive'}[name];
   await page.locator('#'+primary).fill(name==='fin'?'4':'100');await page.locator('#'+primary).dispatchEvent('input');await page.waitForTimeout(150);
   const controlled=await page.evaluate(()=>window.__chip3d.debug());
   assert.ok(Math.abs(zoomed.scale-controlled.scale)<1e-8,'geometry controls preserve scale');
   if(name==='metal')await page.locator('#dielectricButton').click();
   await page.locator('#sectionButton').click();
   await page.locator('[data-view="end"]').click();
   await page.waitForTimeout(100);
   assert.ok(Math.abs(zoomed.scale-(await page.evaluate(()=>window.__chip3d.debug())).scale)<1e-8,'preset preserves scale');
   await page.locator('#parts button').last().click();
   assert.ok((await page.locator('#selectedCopy').textContent()).length>50,'selectable explanation');
   report.push({scene:name,width,before:before.debug,after:controlled,errors:[...errors]});
   assert.equal(errors.length,0,'no script errors');
   console.log(JSON.stringify({scene:name,width,scaleDrift:Math.abs(before.debug.scale-after.scale),labels:before.debug.labels.length,errors}));
  }
 }
 await page.emulateMedia({colorScheme:'dark'});await page.setViewportSize({width:1280,height:1000});await page.goto(target+'?qa#finfet');await page.waitForTimeout(500);
 await page.screenshot({path:resolve(out,'finfet-dark.png'),fullPage:true});
 await page.setViewportSize({width:320,height:900});await page.goto(target+'?qa#channel');await page.waitForTimeout(350);
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'320px page width');
 await page.screenshot({path:resolve(out,'channel-320-dark.png'),fullPage:true});
 writeFileSync(resolve(out,'results.json'),JSON.stringify(report,null,2));
}finally{await browser.close();}
