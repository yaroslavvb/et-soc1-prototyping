// Track actual canvas text during rotation: the old collision layout snaps by 25 px.
// The measurement API exists only in the in-memory copy served by this test.
import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url),{chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const repo=new URL('../../../../',import.meta.url).pathname;
const current=await fs.readFile(new URL('../../chip-3d.html',import.meta.url),'utf8');
const baseline=execFileSync('git',['show','8814cf1e:docs/reports/chip-3d.html'],{cwd:repo,encoding:'utf8'});
const hook=`
window.__labelQA={rotate:(yaw,pitch,zoom)=>{state.yaw=yaw;state.pitch=pitch;state.zoom=zoom;draw();
 const gate=labels.find(l=>l.key==='gate');return {text:{...window.__canvasLabels},anchor:project(gate.p),
  scale:project(camera.target).scale,width,height};},controls:()=>{state.separation=100;state.gateDrive=100;draw();}};`;
function instrument(html){const end='\n})();\n</script>';assert.equal(html.split(end).length,2);return html.replace(end,hook+end);}
const browser=await chromium.launch({...(process.env.CHROME_HEADLESS?{executablePath:process.env.CHROME_HEADLESS}:{channel:'chrome'}),headless:true});
const context=await browser.newContext({viewport:{width:1280,height:900},reducedMotion:'reduce'});
const page=await context.newPage(),errors=[],results=[];
const screenshotDir=new URL('../../../../build/chip-3d-labels/',import.meta.url).pathname;
await fs.mkdir(screenshotDir,{recursive:true});
page.on('pageerror',e=>errors.push(e.message));
await page.addInitScript(()=>{
 window.__canvasLabels={};const fill=CanvasRenderingContext2D.prototype.fillText;
 CanvasRenderingContext2D.prototype.fillText=function(text,x,y,...rest){
  if(this.canvas.id==='sceneCanvas')window.__canvasLabels[text]={x,y,width:this.measureText(text).width};
  return fill.call(this,text,x,y,...rest);
 };
});
let served=instrument(baseline);
await page.route('http://chip-label.test/**',r=>r.fulfill({contentType:'text/html',body:served}));
try{
 await page.goto('http://chip-label.test/model#finfet');
 const old=await page.evaluate(()=>{
  let maxStep=0;
  for(const pitch of [-.5,0,.43,.9]){let previous=null;
   for(let i=0;i<=640;i++){const s=window.__labelQA.rotate(-Math.PI+i*Math.PI/320,pitch,1.8),g=s.text.Gate;
    if(previous&&g)maxStep=Math.max(maxStep,Math.abs(g.y-previous.y));previous=g;
   }
  }return {maxStep};
 });
 assert.ok(old.maxStep>15,'The old gate collision jump was not reproduced');results.push({baseline:'reproduced',...old});
 served=instrument(current);
 for(const width of [1280,390]){
  await page.setViewportSize({width,height:900});
  for(const scene of ['finfet','channel']){
   await page.goto('http://chip-label.test/model#'+scene);await page.reload();
   const sweep=await page.evaluate(()=>{
    let reference=null,maxLabelDrift=0,maxAnchorStep=0,anchorRange=0,scaleDrift=0,firstAnchor=null;
    for(const zoom of [.62,1,1.8])for(const pitch of [-.5,0,.43,.9,1.4]){
     let previous=null,baseScale=null;
     for(let i=0;i<=160;i++){
      const s=window.__labelQA.rotate(-Math.PI+i*Math.PI/80,pitch,zoom);
      const gate=s.text.Gate||s.text['Gate (cutaway)'];if(!gate)throw new Error('Gate label missing');
      if(!reference)reference=s.text;
      for(const [text,rect] of Object.entries(s.text)){
       maxLabelDrift=Math.max(maxLabelDrift,Math.hypot(rect.x-reference[text].x,rect.y-reference[text].y));
       if(rect.x<0||rect.x+rect.width>s.width||rect.y<0||rect.y>s.height)throw new Error('Label outside canvas');
      }
      if(previous)maxAnchorStep=Math.max(maxAnchorStep,Math.hypot(s.anchor.x-previous.x,s.anchor.y-previous.y));
      if(!firstAnchor)firstAnchor=s.anchor;
      anchorRange=Math.max(anchorRange,Math.hypot(s.anchor.x-firstAnchor.x,s.anchor.y-firstAnchor.y));
      if(baseScale===null)baseScale=s.scale;scaleDrift=Math.max(scaleDrift,Math.abs(s.scale-baseScale));previous=s.anchor;
     }
    }
    window.__labelQA.controls();const changed=window.__labelQA.rotate(0,.43,1);
    for(const [text,rect] of Object.entries(changed.text))maxLabelDrift=Math.max(maxLabelDrift,Math.hypot(rect.x-reference[text].x,rect.y-reference[text].y));
    return {maxLabelDrift,maxAnchorStep,anchorRange,scaleDrift};
   });
   assert.equal(sweep.maxLabelDrift,0);assert.equal(sweep.scaleDrift,0);assert.ok(sweep.anchorRange>20);assert.ok(sweep.maxAnchorStep<20);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   results.push({scene,width,...sweep});
   await page.screenshot({path:screenshotDir+`label-${scene}-${width}.png`,fullPage:true});
  }
 }
 assert.deepEqual(errors,[]);console.log(JSON.stringify({pass:true,results,errors},null,2));
}finally{await browser.close();}
