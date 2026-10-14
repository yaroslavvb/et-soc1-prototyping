// Regression: turning a model must preserve actual projection scale, not only state.zoom.
// Expose camera measurements only in the in-memory browser test; shipped HTML has no test API.
import fs from 'node:fs/promises';
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const repo=new URL('../../../../',import.meta.url).pathname;
const current=await fs.readFile(new URL('../../chip-3d.html',import.meta.url),'utf8');
const baseline=execFileSync('git',['show','1aa8383e:docs/reports/chip-3d.html'],{cwd:repo,encoding:'utf8'});
const probe=`
window.__cameraQA={snapshot:()=>{
 const target=typeof camera==='undefined'?[0,0,0]:camera.target;
 const p=typeof fitPoint==='function'?fitPoint(project(target)):project(target);
 return {zoom:state.zoom,yaw:state.yaw,pitch:state.pitch,magnification:p.scale,x:p.x,y:p.y,width,height,
  camera:typeof camera==='undefined'?null:{...camera,target:[...camera.target]},
  vertices:faces.flatMap(f=>f.points||[]).map(p=>[p.x,p.y])};
}};`;
function instrument(html){const end='\n})();\n</script>';assert.equal(html.split(end).length,2);return html.replace(end,probe+end);}
const browser=await chromium.launch({...(process.env.CHROME_HEADLESS?{executablePath:process.env.CHROME_HEADLESS}:{channel:'chrome'}),headless:true});
const context=await browser.newContext({viewport:{width:1280,height:900},reducedMotion:'reduce'});
const page=await context.newPage(),errors=[],results=[];
page.on('pageerror',e=>errors.push(e.message));
let served=instrument(baseline);
await page.route('http://chip-camera.test/**',route=>route.fulfill({contentType:'text/html',body:served}));
const snapshot=()=>page.evaluate(()=>window.__cameraQA.snapshot());
const closeTo=(a,b)=>assert.ok(Math.abs(a-b)<1e-9,`${a} != ${b}`);
async function drag(){const box=await page.locator('canvas').boundingBox();await page.mouse.move(box.x+box.width*.5,box.y+box.height*.5);await page.mouse.down();await page.mouse.move(box.x+box.width*.5+85,box.y+box.height*.5+40,{steps:12});await page.mouse.up();await page.waitForTimeout(60);}
try{
 await page.goto('http://chip-camera.test/model#metal');
 const before=await snapshot();await drag();const after=await snapshot();
 assert.ok(Math.abs(after.magnification/before.magnification-1)>.001,'Baseline did not reproduce unintended scaling');
 results.push({baseline:'reproduced',magnificationRatio:after.magnification/before.magnification,zoomStateUnchanged:before.zoom===after.zoom});
 served=instrument(current);
 for(const width of [1280,390]){
  await page.setViewportSize({width,height:900});
  for(const [scene,control] of [['metal','spread'],['finfet','separation'],['fin','finCount'],['channel','gateDrive']]){
   await page.goto('http://chip-camera.test/model#'+scene);await page.reload();
   const start=await snapshot();await drag();const dragged=await snapshot();
   assert.ok(Math.abs(dragged.yaw-start.yaw)>.1);closeTo(dragged.magnification,start.magnification);closeTo(dragged.zoom,start.zoom);
   for(const preset of ['top','end','perspective']){await page.locator('[data-view="'+preset+'"]').click();const s=await snapshot();closeTo(s.magnification,start.magnification);closeTo(s.x,s.width/2);closeTo(s.y,s.height/2);}
   await page.locator('canvas').focus();await page.keyboard.press('ArrowRight');closeTo((await snapshot()).magnification,start.magnification);
   await page.locator('#'+control).evaluate(e=>{e.value=e.max;e.dispatchEvent(new Event('input',{bubbles:true}));});closeTo((await snapshot()).magnification,start.magnification);
   await page.locator('#zoomIn').click();closeTo((await snapshot()).magnification/start.magnification,1.15);
   await page.locator('#zoomOut').click();closeTo((await snapshot()).magnification,start.magnification);
   await page.locator('#rotateButton').click();await page.waitForTimeout(350);const auto=await snapshot();assert.ok(Math.abs(auto.yaw-start.yaw)>.05);closeTo(auto.magnification,start.magnification);await page.locator('#pauseButton').click();
   // All controls and angles fit the fixed bounding sphere at default zoom.
   await page.locator('#resetButton').click();
   for(let i=0;i<24;i++){await page.locator('canvas').focus();await page.keyboard.press('ArrowRight');await page.waitForTimeout(18);const s=await snapshot();closeTo(s.magnification,start.magnification);assert.ok(s.vertices.every(([x,y])=>Number.isFinite(x)&&Number.isFinite(y)&&x>=29&&x<=s.width-29&&y>=57&&y<=s.height-57));}
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   results.push({scene,width,drag:'stable',presets:'stable',keyboard:'stable',control:'stable',zoom:'1.15×',autoOrbit:'stable',bounds:'fit'});
  }
 }
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({pass:true,results,errors},null,2));
}finally{await browser.close();}
