import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

// Original teaching geometry, informed by Intel's tri-gate illustrations,
// Chenming Hu's MOSFET/FinFET figures and imec's interconnect cross-sections.
// Units are illustrative: no geometry represents a proprietary process layout.
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, Number(v) || 0));
const palette = {
  copper: 0xc8763f, copperLight: 0xeaa771, liner: 0x535c6b,
  gate: 0xbb9654, gateEdge: 0xe0c17e, silicon: 0x526e91,
  source: 0x528b94, drain: 0x6985a7, contact: 0x9ba6af,
  oxide: 0xade2d4, spacer: 0xe1cfa5, isolation: 0xd9e1e9,
  substrate: 0x33465d, top: 0x3abcb2, side: 0x659ee3,
  channel: 0x41d7ba, electron: 0xaffff0,
};

function kit(dark) {
  const group = new THREE.Group();
  const geometries = new Set();
  const materials = new Set();
  const materialCache = new Map();
  const animations = [];
  const mat = (key, extra = {}) => {
    const cacheKey = key + JSON.stringify(extra);
    if (!materialCache.has(cacheKey)) {
      const metallic = ['copper','copperLight','liner','gate','gateEdge','contact'].includes(key);
      const m = new THREE.MeshStandardMaterial({
        color: palette[key] ?? key,
        metalness: metallic ? 0.72 : 0.08,
        roughness: metallic ? 0.29 : 0.62,
        ...extra,
      });
      materialCache.set(cacheKey, m); materials.add(m);
    }
    return materialCache.get(cacheKey);
  };
  const mesh = (geometry, material, position, part, parent = group) => {
    geometries.add(geometry);
    const item = new THREE.Mesh(geometry, material);
    item.position.set(...position);
    item.castShadow = !material.transparent;
    item.receiveShadow = true;
    item.userData.part = part;
    parent.add(item);
    return item;
  };
  const box = (size, position, material, part, radius = 0.035, parent = group) => {
    const r = Math.min(radius, Math.min(...size) * 0.2);
    return mesh(r > 0 ? new RoundedBoxGeometry(...size, 2, r) : new THREE.BoxGeometry(...size), material, position, part, parent);
  };
  const cyl = (radius, height, position, material, part, parent = group, segments = 20) =>
    mesh(new THREE.CylinderGeometry(radius, radius, height, segments), material, position, part, parent);
  const line = (points, color, part, parent = group, dashed = false) => {
    const geometry = new THREE.BufferGeometry().setFromPoints(points.map(p => new THREE.Vector3(...p)));
    geometries.add(geometry);
    const material = dashed ? new THREE.LineDashedMaterial({ color, dashSize: .12, gapSize: .10, transparent: true, opacity: .65 }) : new THREE.LineBasicMaterial({ color, transparent: true, opacity: .72 });
    materials.add(material);
    const item = new THREE.Line(geometry, material);
    item.userData.part = part;
    if (dashed) item.computeLineDistances();
    parent.add(item);
    return item;
  };
  const arrow = (start, end, color, part, parent = group) => {
    const a = new THREE.Vector3(...start), b = new THREE.Vector3(...end);
    const d = b.clone().sub(a), length = d.length();
    const item = new THREE.ArrowHelper(d.normalize(), a, length, color, Math.min(.15, length * .25), .07);
    item.traverse(child => { child.userData.part = part; if (child.geometry) geometries.add(child.geometry); if (child.material) materials.add(child.material); });
    parent.add(item);
    return item;
  };
  const sphereGeometry = new THREE.SphereGeometry(.055, 10, 8);
  geometries.add(sphereGeometry);
  const bead = (position, part, size = 1, color = 'electron') => {
    const item = mesh(sphereGeometry, mat(color, { emissive: palette[color], emissiveIntensity: .45, roughness: .28 }), position, part);
    item.castShadow = false; // Symbolic markers do not alter the static structural shadows.
    item.scale.setScalar(size);
    return item;
  };
  return { group, mat, mesh, box, cyl, line, arrow, bead, animations,
    finish(bounds, anchors) {
      group.updateMatrixWorld(true);
      return { group, bounds, anchors,
        ...(animations.length ? { update(time) { animations.forEach(fn => fn(time)); } } : {}),
        dispose() { geometries.forEach(g => g.dispose()); materials.forEach(m => m.dispose()); }
      };
    }
  };
}

function substrate(k, width = 8, depth = 4.8, finPositions = [0], finWidth = .60) {
  k.box([width,.46,depth], [0,-.55,0], k.mat('substrate'), 'fin', .07);
  // STI surrounds, rather than covering, the fins. The narrow silicon pedestal
  // continues through this insulating floor into the common bulk substrate.
  const min = -depth/2, max = depth/2;
  let cursor = min;
  for (const z of [...finPositions].sort((a,b) => a-b)) {
    const edge = z - finWidth/2;
    if (edge > cursor) k.box([width,.66,edge-cursor], [0,.01,(cursor+edge)/2], k.mat('isolation'), 'isolation', .025);
    cursor = z + finWidth/2;
  }
  if (cursor < max) k.box([width,.66,max-cursor], [0,.01,(cursor+max)/2], k.mat('isolation'), 'isolation', .025);
}

function finBody(k, z = 0, {length = 7, height = 2, width = .60, part = 'fin', material = 'silicon'} = {}) {
  // Visible fin height is above the STI top, y=.34; root enters the substrate.
  k.box([length,height+.32,width], [0,(height-.32)/2,z], k.mat(material), part, .035);
}

// A rectangular tri-gate saddle: two sidewalls and one top, never a bottom gate.
function saddle(k, {x = 0, z = 0, length = 1.72, width = .60, top = 2,
  bottom = .34, thickness = .10, gap = 0, material = 'oxide', part = 'oxide',
  section = false, lift = 0, parent = k.group}) {
  const outer = width/2 + gap;
  const height = top + gap - bottom;
  const topWidth = width + 2*(gap+thickness);
  k.box([length,height,thickness], [x,bottom+height/2+lift,z-outer-thickness/2], k.mat(material), part, .012, parent);
  if (!section) k.box([length,height,thickness], [x,bottom+height/2+lift,z+outer+thickness/2], k.mat(material), part, .012, parent);
  const capWidth = section ? topWidth/2 : topWidth;
  k.box([length,thickness,capWidth], [x,top+gap+thickness/2+lift,z-(section?capWidth/2:0)], k.mat(material), part, .012, parent);
}

function epitaxy(k, x, z, part, material, length = 1.80, width = 1.35, top = 2.30) {
  // Faceted raised source/drain volume, separated from the metal contact above.
  const half = width/2;
  const shape = new THREE.Shape();
  shape.moveTo(-half*.60,.34); shape.lineTo(-half,1.25);
  shape.lineTo(-half*.53,top); shape.lineTo(half*.53,top);
  shape.lineTo(half,1.25); shape.lineTo(half*.60,.34); shape.closePath();
  const geometry = new THREE.ExtrudeGeometry(shape, {depth:length, bevelEnabled:true, bevelThickness:.045, bevelSize:.025, bevelSegments:1, steps:1});
  // Shape x becomes world z; extrusion z becomes world x.
  const item = k.mesh(geometry, k.mat(material), [x-length/2,0,z], part);
  item.rotation.y = Math.PI/2;
  return item;
}

function contacts(k, z = 0, { sourceX = -2.55, drainX = 2.55, width = .80, top = 3.15, pads = true } = {}) {
  for (const x of [sourceX,drainX]) {
    k.box([width,top-2.24,width*.83], [x,(top+2.24)/2,z], k.mat('liner'), 'contact', .04);
    k.box([width*.79,top-2.20,width*.62], [x,(top+2.20)/2,z], k.mat('contact'), 'contact', .035);
    if (pads) k.box([width*1.45,.15,width*1.20], [x,top+.075,z], k.mat('copper'), 'contact', .04);
  }
}

function gateStructure(k, opts, { z = 0, length = 1.72, width = .60, top = 2, lift = 0, wing = 1.55, contact = true } = {}) {
  // The oxide stays attached to silicon when the gate is lifted for inspection.
  saddle(k, {z,length,width,top,thickness:.075,material:'oxide',part:'oxide',section:opts.section});
  saddle(k, {z,length,width,top,thickness:.29,gap:.075,material:'gate',part:'gate',section:opts.section,lift});
  for (const sign of [-1,1]) {
    // Spacer at each channel end, outside the metal gate (along transport axis).
    saddle(k, {x:sign*(length/2+.13),z,length:.26,width,top:top+.03,thickness:.17,gap:.06,material:'spacer',part:'spacer',section:opts.section});
  }
  // Gate landing region over the STI, connected to its back sidewall.
  k.box([length,.33,wing-.55], [0,.505+lift,z-(wing+.55)/2], k.mat('gate'), 'gate', .04);
  if (!opts.section) k.box([length,.33,wing-.55], [0,.505+lift,z+(wing+.55)/2], k.mat('gate'), 'gate', .04);
  if (contact) {
    k.box([.58,1.60,.60], [0,1.43+lift,z-wing+.32], k.mat('gate'), 'gate', .055);
    k.box([.72,.13,.76], [0,2.29+lift,z-wing+.32], k.mat('gateEdge'), 'gate', .035);
  }
}

function metalModel(opts) {
  const k = kit(opts.dark), spread = opts.spread/100;
  k.box([8.6,.46,8.6], [0,-.55,0], k.mat('substrate'), 'silicon', .08);
  k.box([8.6,.48,8.6], [0,-.08,0], k.mat('isolation'), 'dielectric', .045);
  // Small transistor rows provide a readable device-to-wiring hierarchy.
  for (const x of [-2.8,-.9,.9,2.8]) for (const z of [-2.7,-.9,.9,2.7]) {
    k.box([1.15,.32,.15], [x,.28,z], k.mat('silicon'), 'silicon', .02);
    k.box([.22,.40,.55], [x,.34,z], k.mat('gate'), 'silicon', .025);
    for (const dx of [-.43,.43]) k.box([.16,.33,.20], [x+dx,.39,z], k.mat('contact'), 'via', .015);
  }
  const levels = [
    {y:1.12, h:.20, w:.29, axis:'x', tracks:[-2.4,-1.2,0,1.2,2.4], length:7.8},
    {y:2.20+.60*spread, h:.27, w:.40, axis:'z', tracks:[-2.5,-1.25,0,1.25,2.5], length:8.0},
    {y:3.40+1.20*spread, h:.36, w:.58, axis:'x', tracks:[-2.1,0,2.1], length:8.2},
    {y:4.80+1.80*spread, h:.49, w:.84, axis:'z', tracks:[-2.5,0,2.5], length:8.4},
  ];
  levels.forEach((level,i) => {
    for (const track of level.tracks) {
      const size = level.axis==='x' ? [level.length,level.h,level.w] : [level.w,level.h,level.length];
      const p = level.axis==='x' ? [0,level.y,track] : [track,level.y,0];
      // The dark barrier/liner is visible as a fine rim around the copper fill.
      k.box(size.map(v=>v+.035), p, k.mat('liner'), 'metal', .025);
      k.box([size[0]-.018,size[1]-.008,size[2]-.018], [p[0],p[1]+.022,p[2]], k.mat(i===3?'copperLight':'copper'), 'metal', .025);
    }
  });
  // One expanded contact chain shows how a device terminal reaches M1. Other
  // local connections are omitted so this hierarchy remains legible.
  k.cyl(.07,.29,[-.47,.665,.90],k.mat('contact'),'via');
  k.box([.15,.12,.43],[-.47,.78,1.05],k.mat('contact'),'via',.015);
  k.cyl(.075,.39,[-.47,.945,1.20],k.mat('liner'),'via');
  k.cyl(.055,.40,[-.47,.945,1.20],k.mat('copper'),'via');
  const viaPairs = [
    [[-2.5,-2.4],[-1.25,1.2],[0,0],[1.25,-1.2],[2.5,2.4]],
    [[-2.5,-2.1],[0,0],[0,2.1],[1.25,2.1],[2.5,-2.1]],
    [[-2.5,-2.1],[0,0],[2.5,2.1]],
  ];
  viaPairs.forEach((pairs,i) => {
    const lower=levels[i], upper=levels[i+1];
    // Endpoints penetrate each track: no floating or merely touching via.
    const bottom=lower.y-.035, top=upper.y+.035;
    pairs.forEach(([x,z]) => {
      const r=.11+i*.035;
      k.cyl(r+.028,top-bottom,[x,(top+bottom)/2,z],k.mat('liner'),'via');
      k.cyl(r,top-bottom+.025,[x,(top+bottom)/2,z],k.mat('copperLight'),'via');
      for (const y of [lower.y+lower.h/2,upper.y-upper.h/2]) k.cyl(r+.043,.055,[x,y,z],k.mat('gateEdge'),'via');
    });
  });
  if (opts.dielectric) {
    const top = levels[3].y + .38;
    if (opts.section) {
      // Opaque cutaway occupies the rear quarter, exposing the conductors ahead.
      k.box([4.35,top-.18,4.35],[-2.175,(top+.18)/2,-2.175],k.mat('isolation'),'dielectric',.035);
      for (const level of levels) k.line([[-4.37,level.y,-.01],[-.01,level.y,-.01],[-.01,level.y,-4.37]],0xa9bacb,'dielectric');
    } else {
      // An optional single transparent envelope, never a stack of alpha slabs.
      k.box([8.7,top-.18,8.7],[0,(top+.18)/2,0],k.mat('isolation',{transparent:true,opacity:.11,depthWrite:false}),'dielectric',.045);
    }
  }
  const route = [new THREE.Vector3(-3.8,levels[0].y+.14,0),new THREE.Vector3(0,levels[0].y+.14,0),new THREE.Vector3(0,levels[1].y+.17,0),new THREE.Vector3(0,levels[1].y+.17,2.1),new THREE.Vector3(0,levels[2].y+.22,2.1),new THREE.Vector3(2.5,levels[2].y+.22,2.1),new THREE.Vector3(2.5,levels[3].y+.29,2.1),new THREE.Vector3(2.5,levels[3].y+.29,4.05)];
  const lengths = route.slice(1).map((p,i)=>p.distanceTo(route[i]));
  const total = lengths.reduce((a,b)=>a+b,0);
  const pulses = Array.from({length:7},(_,i)=>k.bead([0,0,0],'metal',1.35,'electron'));
  // A pulse's place is a fraction of the route (a loop in 11.2 s: 1.3 units/s at the default separation), so a new
  // separation carries the pulses with their tracks instead of along them, and a paused flow stays put.
  k.animations.push(time=>pulses.forEach((p,i)=>{
    let distance=((time/11.2+i/pulses.length)%1)*total;
    for(let j=0;j<lengths.length;j++){if(distance<=lengths[j]){p.position.lerpVectors(route[j],route[j+1],distance/lengths[j]);break;} distance-=lengths[j];}
  }));
  return k.finish({center:[0,3.0,0],radius:7.9,groundY:-.78},[
    {key:'metal',text:'Copper wiring',position:[2.5,levels[3].y+.27,0],slot:'top'},
    {key:'via',text:'Via + liner',position:[2.5,(levels[2].y+levels[3].y)/2,2.1],slot:'right'},
    {key:'dielectric',text:'Insulating dielectric',position:opts.dielectric?[-3.4,levels[2].y,-1.2]:[-3.6,.16,2.9],slot:'left'},
    {key:'silicon',text:'Transistors below',position:[-.9,.40,.9],slot:'bottom'},
  ]);
}

function finfetModel(opts) {
  const k = kit(opts.dark), lift=opts.separation/100*2.35;
  substrate(k); finBody(k);
  epitaxy(k,-2.50,0,'source','source'); epitaxy(k,2.50,0,'drain','drain');
  gateStructure(k,opts,{lift}); contacts(k);
  if (lift>.05) {
    for (const z of [-.70,.70]) k.line([[-.86,2.39,z],[-.86,2.39+lift,z]],0x9ba9b5,'gate',k.group,true);
  }
  return k.finish({center:[0,1.65,0],radius:5.35,groundY:-.78},[
    {key:'gate',text:'Metal gate',position:[0,2.37+lift,-.12],slot:'top'},
    {key:'source',text:'Raised source',position:[-2.50,1.70,.67],slot:'left'},
    {key:'drain',text:'Raised drain',position:[2.50,1.70,.67],slot:'right'},
    {key:'oxide',text:'High-k dielectric',position:[0,1.48,.34],slot:'bottom'},
  ]);
}

function finModel(opts) {
  const k = kit(opts.dark), n=opts.finCount, pitch=1.30;
  const zs=Array.from({length:n},(_,i)=>(i-(n-1)/2)*pitch);
  substrate(k,7.8,6.3,zs,.47);
  for(const z of zs){
    finBody(k,z,{length:6.6,width:.47});
    // These thin finite volumes mark the three gated faces, only in the gate span.
    k.box([1.72,.037,.47],[0,2.005,z],k.mat('top',{emissive:palette.top,emissiveIntensity:.15}),'top',.006);
    for(const sign of [-1,1]) k.box([1.72,1.66,.032],[0,1.17,z+sign*.238],k.mat('side',{emissive:palette.side,emissiveIntensity:.12}),'side',.006);
    saddle(k,{z,length:1.72,width:.47,thickness:.055,top:2.035,material:'oxide',part:'fin',section:opts.section});
    saddle(k,{z,length:1.72,width:.47,thickness:.20,gap:.055,top:2.035,material:'gate',part:'gate',section:opts.section});
  }
  const front=zs[zs.length-1], back=zs[0];
  // The common gate joins the saddles in the gaps over STI. It never passes
  // through the fin, and there is no gate underneath the bulk silicon.
  for(let i=0;i<zs.length-1;i++){
    const a=zs[i]+.45, b=zs[i+1]-.45;
    k.box([1.72,.25,b-a],[0,.465,(a+b)/2],k.mat('gate'),'gate',.02);
  }
  // Keep the source/drain connections visible as shared end rails on all fins.
  for(const x of [-2.48,2.48]){
    k.box([.72,.61,front-back+.70],[x,1.64,0],k.mat(x<0?'source':'drain'),'fin',.055);
    k.box([.52,.11,front-back+.86],[x,1.99,0],k.mat('contact'),'fin',.035);
  }
  // Symbolic dimensions are expressed on the visible front fin; no nm claim.
  const z=front+.43;
  k.line([[1.18,.34,z],[1.18,2,z]],0x6996bf,'side');
  for(const y of [.34,2]) k.line([[1.08,y,z],[1.28,y,z]],0x6996bf,'side');
  k.line([[1.18,2.22,front-.235],[1.18,2.22,front+.235]],0x33b4a8,'top');
  for(const z0 of [front-.235,front+.235]) k.line([[1.09,2.22,z0],[1.27,2.22,z0]],0x33b4a8,'top');
  return k.finish({center:[0,1.15,0],radius:5.5,groundY:-.78},[
    {key:'top',text:'Top surface · T',position:[0,2.025,front+.08],slot:'top'},
    {key:'gate',text:'One shared gate',position:[0,.59,back-.38],slot:'left'},
    {key:'side',text:'Two sidewalls · 2H',position:[.22,1.30,front+.255],slot:'right'},
    {key:'isolation',text:'STI isolation',position:[2.5,.34,front+.72],slot:'bottom'},
  ]);
}

// The channel's carriers keep their travel across rebuilds (each slider step builds a new model): it accumulates
// at the present drive's speed, so a new gate drive changes their speed, not their place, and paused they stay put.
const drift={phase:0,time:null};
function channelModel(opts) {
  const k=kit(opts.dark), drive=opts.gateDrive/100;
  const charge=THREE.MathUtils.smoothstep(drive,.23,.82);
  substrate(k,8,4.8,[0],.60);
  // In the gated span, bulk silicon and inversion slices are separate volumes.
  for(const x of [-2.18,2.18]) k.box([2.60,2.32,.60],[x,.84,0],k.mat('silicon'),'fin',.03);
  k.box([1.76,2.26,.53],[0,.81,0],k.mat('silicon'),'fin',.025);
  const chargeColor=new THREE.Color(palette.silicon).lerp(new THREE.Color(palette.channel),charge);
  // A deliberately translucent inversion slice reveals symbolic carrier dots
  // inside silicon. Their centers and radii never enter the gate dielectric.
  const layer=k.mat(chargeColor.getHex(),{emissive:palette.channel,emissiveIntensity:charge*.26,roughness:.48,transparent:charge>.035,opacity:1-charge*.40,depthWrite:charge<=.035});
  k.box([1.76,.060,.60],[0,1.97,0],layer,'channel',.008);
  for(const sign of [-1,1]) k.box([1.76,1.60,.035],[0,1.14,sign*.2825],layer,'channel',.006);
  epitaxy(k,-2.50,0,'source','source'); epitaxy(k,2.50,0,'drain','drain');
  gateStructure(k,opts,{length:1.76,contact:false});
  // The field crosses the oxide; no particles are emitted from the gate.
  if(opts.section && charge>.02){
    const color=0xd6b765;
    for(const x of [-.57,0,.57]){
      k.arrow([x,2.38,.13],[x,1.99,.13],color,'gate');
      k.arrow([x,1.12,.69],[x,1.12,.29],color,'gate');
    }
  }
  const electrons=[];
  for(let i=0;i<30;i++){
    const lane=i%3;
    const y=lane===0?1.97:.66+((i*7)%11)/11*1.16;
    const z=lane===0?-.19+((i*3)%7)/7*.38:(lane===1?.2825:-.2825);
    const bead=k.bead([0,y,z],'channel',.25+charge*.05);
    electrons.push({bead,y,z,phase:i/30});
  }
  k.animations.push(time=>{
    const dt=drift.time===null?0:clamp(time-drift.time,0,.05);
    drift.time=time; drift.phase=(drift.phase+dt*(.10+.30*charge))%1;
    electrons.forEach(({bead,y,z,phase})=>{
      bead.visible=charge>.035 && phase<.10+charge*.90;
      // Flow is source (-X) to drain (+X), with a fixed positive drain bias.
      bead.position.set(-2.95+((phase+drift.phase)%1)*5.9,y,z);
    });
  });
  return k.finish({center:[0,1.2,0],radius:5.1,groundY:-.78},[
    {key:'gate',text:'Gate electrode',position:[0,2.34,-.23],slot:'top'},
    {key:'source',text:'Source',position:[-2.50,1.55,.64],slot:'left'},
    {key:'drain',text:'Drain',position:[2.50,1.55,.64],slot:'right'},
    {key:'channel',text:'Inversion charge',position:[0,1.12,.30],slot:'bottom'},
  ]);
}

export function buildModel(name, options = {}) {
  const opts={
    spread:clamp(options.spread,0,100), separation:clamp(options.separation,0,100),
    finCount:Math.round(clamp(options.finCount??3,1,4)), gateDrive:clamp(options.gateDrive??65,0,100),
    section:Boolean(options.section), dielectric:Boolean(options.dielectric), dark:Boolean(options.dark),
  };
  const builders={metal:metalModel,finfet:finfetModel,fin:finModel,channel:channelModel};
  return (builders[name]??finfetModel)(opts);
}
