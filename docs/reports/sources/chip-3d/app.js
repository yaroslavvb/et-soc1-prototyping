import {createViewer} from './viewer.js';
import {buildModel} from './models.js';
import {scenes,colors,sectionSVG} from './content.js';

const $=id=>document.getElementById(id);
const dark=matchMedia('(prefers-color-scheme: dark)'),reduced=matchMedia('(prefers-reduced-motion: reduce)');
const state={scene:'metal',spread:18,separation:0,finCount:1,gateDrive:68,section:false,dielectric:false,dark:dark.matches,selected:'metal',paused:reduced.matches,auto:false};
let viewer=null,model=null,updateQueued=false;
function viewChange(view){
 state.auto=view.auto;
 $('modelStatus').textContent=({perspective:'Perspective',top:'Top view',end:'End view',custom:'Your viewpoint'})[view.view]||'Your viewpoint';
 document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view.view)));
 $('rotateButton').setAttribute('aria-pressed',String(state.auto));$('rotateButton').textContent=state.auto?'Stop orbit':'Auto orbit';
}
try{viewer=createViewer({canvas:$('sceneCanvas'),overlay:$('labelOverlay'),onPick:selectPart,onViewChange:viewChange});}catch(error){$('renderFallback').hidden=false;console.warn('3D unavailable:',error.message);}
function selectPart(key){
 const p=scenes[state.scene].parts.find(p=>p[0]===key);if(!p)return;
 state.selected=key;
 $('selectedCopy').replaceChildren();const title=document.createElement('strong');title.textContent=p[1]+'. ';
 $('selectedCopy').append(title,document.createTextNode(p[2]));
 document.querySelectorAll('[data-part]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.part===key)));
 viewer?.setSelected(key);
}
function rebuild(){
 updateQueued=false;
 if(viewer){model=buildModel(state.scene,state);viewer.setModel(model);viewer.setSelected(state.selected);}
 $('sectionFigure').innerHTML=sectionSVG(state.scene,state);
 if(state.scene==='fin')$('detailMetric').innerHTML=`W<sub>eff</sub> ≈ ${state.finCount} × (2H<sub>fin</sub> + T<sub>fin</sub>)<small>${scenes.fin.metricNote}</small>`;
}
function queueRebuild(){if(!updateQueued){updateQueued=true;requestAnimationFrame(rebuild);}}
function updateControl(){
 const s=scenes[state.scene],v=state[s.primary];
 $(s.primary+'Value').value=state.scene==='fin'?v+(v===1?' fin':' fins'):state.scene==='channel'?v+' / 100':v===0?'Assembled':v+'%';
 $('sectionButton').setAttribute('aria-pressed',String(state.section));
 $('sectionButton').textContent=state.section?'Close cutaway':'Open cutaway';
 $('dielectricButton').hidden=state.scene!=='metal';$('dielectricButton').setAttribute('aria-pressed',String(state.dielectric));
 $('dielectricButton').textContent=state.dielectric?'Hide dielectric':'Show dielectric';
 $('stateSummary').textContent=s.label+': '+$(s.primary+'Value').value+'. '+(state.section?'Cutaway open.':'Cutaway closed.');
}
function updateMotion(){
 $('pauseButton').textContent=state.paused?'Play flow':'Pause flow';$('pauseButton').setAttribute('aria-pressed',String(state.paused));
 $('pauseButton').hidden=state.scene==='finfet'||state.scene==='fin';
 $('motionNote').hidden=!reduced.matches;viewer?.setPaused(state.paused);viewer?.setAuto(state.auto);
 $('rotateButton').textContent=state.auto?'Stop orbit':'Auto orbit';$('rotateButton').setAttribute('aria-pressed',String(state.auto));
}
function setScene(name){
 if(!scenes[name])name='metal';state.scene=name;const s=scenes[name];
 state.selected=s.parts[0][0];state.section=name==='channel'||name==='fin';state.auto=false;
 for(const [id,value] of Object.entries({sceneTitle:s.title,sceneKicker:s.kicker,scenePurpose:s.purpose,modelTag:s.tag,lessonCopy:s.lesson,controlHint:s.hint,sectionEyebrow:s.section,detailTitle:s.detailTitle,detailCopy:s.detailCopy,detailFootnote:s.footnote,sceneSummary:s.purpose+' '+s.lesson}))$(id).textContent=value;
 $('sceneCanvas').setAttribute('aria-label',s.title+'. '+s.purpose);
 $('backLink').href='https://spacesheep.dev/@yaroslavvb/et-soc1-chip-diagram#at='+s.anchor;
 $('detailMetric').innerHTML=s.metric+'<small>'+s.metricNote+'</small>';
 $('sceneControls').innerHTML=`<h3 id="controlTitle">${s.controlTitle}</h3><label class="slider-heading" for="${s.primary}">${s.label}<output id="${s.primary}Value"></output></label><input id="${s.primary}" type="range" min="${s.min}" max="${s.max}" step="1" value="${state[s.primary]}"><div class="range-ends"><span>${s.ends[0]}</span><span>${s.ends[1]}</span></div>`;
 $(s.primary).addEventListener('input',e=>{state[s.primary]=+e.target.value;updateControl();queueRebuild();});
 document.querySelectorAll('[data-scene]').forEach(a=>{if(a.dataset.scene===name)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
 const parts=$('parts');parts.replaceChildren();
 for(const [key,label] of s.parts){const b=document.createElement('button');b.type='button';b.dataset.part=key;b.innerHTML=`<span class="swatch" style="--swatch:${colors[key]}"></span>`;b.append(document.createTextNode(label));b.addEventListener('click',()=>selectPart(key));parts.append(b);}
 updateControl();rebuild();viewer?.reset();viewer?.setTheme(state.dark);selectPart(state.selected);updateMotion();
}
// Metal's cutaway is a cut through the dielectric: opening it shows the dielectric, and hiding the dielectric closes it.
$('sectionButton').addEventListener('click',()=>{state.section=!state.section;if(state.section&&state.scene==='metal')state.dielectric=true;updateControl();rebuild();});
$('dielectricButton').addEventListener('click',()=>{state.dielectric=!state.dielectric;if(!state.dielectric&&state.scene==='metal')state.section=false;updateControl();rebuild();});
$('zoomOut').addEventListener('click',()=>viewer?.zoomBy(1/1.15));$('zoomIn').addEventListener('click',()=>viewer?.zoomBy(1.15));$('resetButton').addEventListener('click',()=>viewer?.reset());
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>viewer?.setView(b.dataset.view)));
$('pauseButton').addEventListener('click',()=>{state.paused=!state.paused;updateMotion();});
$('rotateButton').addEventListener('click',()=>{state.auto=!state.auto;updateMotion();});
dark.addEventListener('change',()=>{state.dark=dark.matches;viewer?.setTheme(state.dark);rebuild();});
reduced.addEventListener('change',()=>{if(reduced.matches){state.paused=true;state.auto=false;}updateMotion();});
window.addEventListener('hashchange',()=>setScene(location.hash.slice(1)));
// Test hooks are opt-in; the normal published experience exposes no scene internals.
if(new URLSearchParams(location.search).has('qa'))window.__chip3d={state,viewer,scenes,buildModel,setScene,rebuild,debug:()=>viewer?.debug()};
setScene(location.hash.slice(1));
