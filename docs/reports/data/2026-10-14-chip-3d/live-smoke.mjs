// Exercise the public viewer and its real embedded page, including hash routing.
import {createRequire} from 'node:module';
import {mkdirSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const browser=await chromium.launch({channel:'chrome',headless:true,args:['--enable-webgl','--use-angle=metal']});
const out=resolve('build/chip-3d-quality');mkdirSync(out,{recursive:true});const results=[];
try{
 const context=await browser.newContext({viewport:{width:1280,height:1000},deviceScaleFactor:1,reducedMotion:'reduce'});
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 for(const width of [1280,390]){
  await page.setViewportSize({width,height:1000});
  for(const name of ['metal','finfet','fin','channel']){
   await page.goto('https://spacesheep.dev/@yaroslavvb/et-soc1-in-3d#'+name,{waitUntil:'domcontentloaded'});
   await page.waitForSelector('iframe[src*="9018f695-7165-4852-9fbb-4f49cfcaefa1"]');
   const frame=await(await page.$('iframe[src*="9018f695-7165-4852-9fbb-4f49cfcaefa1"]')).contentFrame();
   await frame.waitForSelector('#labelOverlay span');await page.waitForTimeout(250);
   const data=await frame.evaluate(()=>({hash:location.hash,active:document.querySelector('[data-scene][aria-current]')?.dataset.scene,fallback:!document.getElementById('renderFallback').hidden,overflow:document.documentElement.scrollWidth>innerWidth,labels:[...document.querySelectorAll('#labelOverlay span')].map(e=>({text:e.textContent,x:e.offsetLeft,y:e.offsetTop}))}));
   assert.equal(data.active,name,'host forwards deep-link hash');assert.equal(data.fallback,false,'live WebGL');assert.equal(data.overflow,false,'live content fits');
   if(name==='finfet'||name==='channel'){
    const r=await frame.locator('#sceneCanvas').boundingBox();await page.mouse.move(r.x+r.width*.4,r.y+r.height*.45);await page.mouse.down();await page.mouse.move(r.x+r.width*.7,r.y+r.height*.5,{steps:16});await page.mouse.up();await page.waitForTimeout(100);
    const labels=await frame.evaluate(()=>[...document.querySelectorAll('#labelOverlay span')].map(e=>({text:e.textContent,x:e.offsetLeft,y:e.offsetTop})));
    assert.deepEqual(labels,data.labels,'live labels stable during pointer drag');
   }
   if(name==='finfet'||name==='metal')await frame.locator('#stage').screenshot({path:resolve(out,`live-${name}-${width}.png`)});
   results.push({scene:name,width,...data,errors:[...errors]});assert.equal(errors.length,0,'live page has no script errors');console.log(JSON.stringify({scene:name,width,hash:data.hash,errors}));
  }
 }
 writeFileSync(resolve(out,'live-results.json'),JSON.stringify(results,null,2));
}finally{await browser.close();}
