/* The energy manual's page script. D is manual.json (tools/ettelem/build_energy_manual.py); CK is the shared chart
   toolkit (docs/reports/sources/chartkit.js). Every number the page prints is computed from D here, except the few
   typed constants that say where they come from. Every chart is drawn with CK: sized to its container, keyboard- and
   touch-reachable, tokens only. */
const f1=v=>v.toFixed(1),f2=v=>v.toFixed(2);
const f0=v=>v.toFixed(0),f3=v=>v.toFixed(3);
const fs=v=>Math.abs(v)>=10?v.toFixed(1):v.toFixed(2);   /* two decimals below 10, one above: no more digits than the bars carry */
const E=D.enercat.cards, A2=E.aifoundry2, A3=E.aifoundry3||[];
const key=r=>[r.pattern,r.operands,r.harts,r.scp].join('|');
const a2={},a3={}; A2.forEach(r=>a2[key(r)]=r); A3.forEach(r=>a3[key(r)]=r);
const g=(p,o,h,s)=>a2[[p,o,h,!!s].join('|')];
const R=D.rest, P80=R.P_fix_w+R.A_leak_80_w;
/* Confidence bars. CB[key] is the catalogue's pooled entry: mean over every pass on every card, lo-hi the range
   those passes spanned, per_card each card's mean and pass-to-pass standard error. cb() scales a per-instruction
   figure to per byte where needed; bt() renders "mean [lo-hi]"; pcs() the per-card column; ebar() draws a bar. */
const CB=(D.catalogue&&D.catalogue.combined)||{}, RR=D.reruns||{};
/* V3: the version-3 check's per-card results (build_energy_manual.py v3_block, from docs/reports/data/2026-09-25-claims-v3/results) */
const V3=D.v3||{}, VI=V3.idle||{};
/* AMENDMENTS.md C2: every card's V3-ABL-A switching carries a launch-temperature offset, leak x (t_launch - reference) per
   run (tensor.launch_offset); the registered values stay in the tables, and the text that compares cards states the offsets
   and gives the values at each run's actual launch (at_launch_w) */
/* C2 as revised: the launch temperatures are whole-degree readings, the references thermal-model temperatures at launches
   on a downward step of the reading; at_launch_step_w takes each launch to be on such a step (die = reading + step_c),
   at_launch_w takes the reading as the die temperature. The text gives each value as the range over the two. */
const LO=D.tensor.launch_offset||{};
const atL=(h,cfg)=>LO[h]&&LO[h].at_launch_w?LO[h].at_launch_w[cfg]:null;
const atLs=(h,cfg)=>LO[h]&&LO[h].at_launch_step_w?LO[h].at_launch_step_w[cfg]:null;
const rng2=(a,b,fn)=>{if(a==null||b==null)return fn(a==null?b:a); const lo=fn(Math.min(a,b)),hi=fn(Math.max(a,b)); return lo===hi?lo:`${lo}–${hi}`;};
const loOff=h=>{const a=LO[h].mean_w,b=LO[h].mean_w_step; if(b==null)return `${Math.abs(a).toFixed(2)} W ${a<0?'lower':'higher'}`;
 const lo=Math.min(a,b),hi=Math.max(a,b); return lo>=0?`${lo.toFixed(2)}–${hi.toFixed(2)} W higher`:hi<=0?`${(-hi).toFixed(2)}–${(-lo).toFixed(2)} W lower`:`between ${(-lo).toFixed(2)} W lower and ${hi.toFixed(2)} W higher`;};
const loNote=()=>{const hs=CK.cardsIn(LO); if(!hs.length)return ''; const by={}; hs.forEach(h=>{const r=LO[h].ref_c.toFixed(1); (by[r]=by[r]||[]).push(h);}); const st=LO[hs[0]].step_c;
 return `the registered switching values carry a launch-temperature offset (note C2 of the record's AMENDMENTS.md): they are referenced to ${andList(Object.keys(by).map(r=>`${r} °C (${andList(by[r].map(h=>CK.card(h).label))})`))} while the runs launched at whole-degree readings of ${andList(hs.map(h=>LO[h].launch_c.toFixed(1)))} °C in that order`+
  (st!=null?`; the references were taken at launches on a downward step of the reading, so the die at these launches was at the reading or up to ${st.toFixed(2)} °C above it, which the reading cannot tell apart,`:',')+` so at the die temperature of each launch ${andList(hs.map(h=>`${CK.card(h).label}'s are ${loOff(h)}`))}`;};
const cap1=t=>t?t[0].toUpperCase()+t.slice(1):t;
/* each card's launch temperature for the tensor rows (tensor.launch_c), as "80 °C (57 °C on aifoundry3)" */
function launchTxt(){const LC=D.tensor.launch_c||{}, hs=CK.cardsIn(LC), by={}; hs.forEach(h=>{const t=f0(LC[h]); (by[t]=by[t]||[]).push(h);});
 const ts=Object.keys(by).sort((a,b)=>by[b].length-by[a].length); if(!ts.length)return '80 °C';
 return `${ts[0]} °C`+(ts.length>1?` (${ts.slice(1).map(t=>`${t} °C on ${andList(by[t].map(h=>CK.card(h).label))}`).join('; ')})`:'');}
const cb=(k,sc)=>{const c=CB[k]; if(!c)return null; sc=sc||1; const pc={}; for(const h in c.per_card)pc[h]={mean:c.per_card[h].mean*sc,se:(c.per_card[h].se||0)*sc,n:c.per_card[h].n};
  return {mean:c.mean*sc,lo:c.lo*sc,hi:c.hi*sc,n:c.n,per_card:pc};};
const pick=(fn,v)=>fn===fs?(Math.abs(v)>=10?f1:f2):fn;   /* fs: one precision for a whole bar, set by its mean */
const bt=(c,fn)=>{if(!c)return '—'; const g=pick(fn,c.mean); return `<b>${g(c.mean)}</b> <span class="small">[${g(c.lo)}–${g(c.hi)}]</span>`;};
const more=(v,fn)=>{let s=fn(v); if(v>0&&+s===0){const d=(s.split('.')[1]||'').length; for(let k=d+1;k<=d+2&&+s===0;k++)s=v.toFixed(k);} return s;};
const pcs=(c,fn)=>c?CK.cardsIn(c.per_card).map(h=>{const g=pick(fn,c.per_card[h].mean); return `${cshort(h)} ${g(c.per_card[h].mean)} ± ${more(c.per_card[h].se||0,g)}`;}).join('<br>'):'—';
const sup=n=>String(n).split('').map(ch=>'⁰¹²³⁴⁵⁶⁷⁸⁹'['0123456789'.indexOf(ch)]||ch).join('');
const sci=v=>{const e=Math.floor(Math.log10(v)); return (v/10**e).toFixed(2)+' × 10'+sup(e);};
const nf=v=>Math.round(v).toLocaleString('en-US');
const WORD=['no','one','two','three','four','five','six','seven','eight'];
/* least-squares line through points [[x,y],...]: {a (intercept), b (slope), r2} */
function lfit(pts){const n=pts.length,mx=pts.reduce((s,p)=>s+p[0],0)/n,my=pts.reduce((s,p)=>s+p[1],0)/n;
 let sxx=0,sxy=0,syy=0; pts.forEach(p=>{sxx+=(p[0]-mx)**2;sxy+=(p[0]-mx)*(p[1]-my);syy+=(p[1]-my)**2;});
 const b=sxy/sxx,a=my-b*mx; return {a,b,r2:sxy*sxy/(sxx*syy)};}
function ebar(svg,x,y1,y2,col){const g2=CK.el('g',{},svg), st={stroke:col||'var(--ink)','stroke-width':1.5};
  CK.el('line',Object.assign({x1:x,x2:x,y1,y2},st),g2); CK.el('line',Object.assign({x1:x-3,x2:x+3,y1,y2:y1},st),g2); CK.el('line',Object.assign({x1:x-3,x2:x+3,y1:y2,y2},st),g2); return g2;}

/* ---------- shared for the CK charts ---------- */
const $=id=>document.getElementById(id);
const HUB='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability';
const lawAt=T=>R.P_fix_w+R.A_leak_80_w*Math.exp((T-80)/R.T_L_c);
/* The cards. CARDS: the catalogue's cards in the registry's order (chartkit CK.cards fixes each card's colour, mark and
   label); CARDLIST: every card any catalogue entry has a value for, which the card selectors offer. SA is the first
   card's summary (aifoundry2's), SB the second's. Nothing below names a card for a chart: a third card in the data is
   drawn and priced with no code change. */
const CARDS=CK.cardsIn(D.catalogue.cards), SA=D.catalogue.cards[CARDS[0]].summary, SB=CARDS[1]?D.catalogue.cards[CARDS[1]].summary:{};
const S2=SA;
const CARDLIST=CK.cardsIn([...new Set(CARDS.concat(...Object.values(CB).map(c=>Object.keys(c.per_card||{}))))]);
const ALLC=CARDLIST.length===2?'both cards':`all ${WORD[CARDLIST.length]||CARDLIST.length} cards`;
const cshort=h=>CK.card(h).short, cname=h=>h==null||h==='pooled'?ALLC:CK.card(h).label;
const andList=a=>a.length<2?a.join(''):a.slice(0,-1).join(', ')+' and '+a[a.length-1];
const SUMM=h=>(D.catalogue.cards[h]||{}).summary||{};
/* the median ratio of card h to the reference card over the catalogue's entries per instruction (byte false) or per byte */
const kindMed=(h,byte)=>{const R0=SUMM(CARDS[0]), Rh=SUMM(h), v=[]; for(const k in R0){const a=R0[k], b=Rh[k]; if(!b)continue; const isB=a.bytes_per_s.mean>0; if(isB!==byte)continue;
  const fld=isB?'pj_per_byte':'pj_per_op'; if(a[fld].mean>0&&b[fld].mean>0)v.push(b[fld].mean/a[fld].mean);}
 v.sort((x,y)=>x-y); return v.length?(v.length%2?v[v.length>>1]:(v[v.length/2-1]+v[v.length/2])/2):null;};
/* the card a single-card source was measured on, read from its data path (…-aifoundry2/…) */
const srcCard=p=>{const m=String((Array.isArray(p)?p[0]:p)||'').match(/aifoundry\d(?:-c\d)?/); return m?CK.card(m[0]).id:null;};
const LAWCARD=srcCard(R.source&&R.source.law)||CARDS[0];     /* the card the idle law of section 1 was fitted on */
/* one catalogue entry on card h, scaled like cb(): {mean, lo, hi, se, n}, lo–hi the range over that card's passes;
   h null or 'pooled' is cb() itself; null when the card has no value (never a zero) */
const cbc=(k,h,sc)=>{if(h==null||h==='pooled')return cb(k,sc); const c=CB[k], p=c&&CK.pick(c,h); if(!p)return null; sc=sc||1;
  const s=SUMM(h)[k], q=s&&(c.unit==='pJ/B'?s.pj_per_byte:s.pj_per_op);
  return {mean:p.mean*sc,lo:(q&&q.min!=null?q.min:p.mean)*sc,hi:(q&&q.max!=null?q.max:p.mean)*sc,se:p.se!=null?p.se*sc:null,n:p.n,card:h};};
/* a pooled value {mean, lo, hi, per_card} (reruns, tensor bars) on card h: that card's mean ± its pass-to-pass standard
   error (sebar), or the pooled bar itself when h is the only card behind it, or its mean alone (nobar) when neither is
   kept; null when h has no value */
const pcv=(v,h)=>{if(!v)return null; if(h==null||h==='pooled')return v; const p=CK.pick(v,h); if(!p)return null;
  const only=Object.keys(v.per_card||{}); if(only.length===1&&only[0]===h&&v.lo!=null)return Object.assign({},v,{card:h});
  return {mean:p.mean,lo:p.se!=null?p.mean-p.se:p.mean,hi:p.se!=null?p.mean+p.se:p.mean,se:p.se,n:p.n,card:h,sebar:p.se!=null,nobar:p.se==null};};
/* how a value's bar reads in a tooltip: [lo–hi], ± se, or the number of runs when no spread is kept per card */
const barOf=(c,fn)=>c.nobar?`(${c.n!=null?`${WORD[c.n]||c.n} run${c.n>1?'s':''}, `:''}no per-card spread kept)`:c.sebar?`± ${more(c.se,pick(fn,c.mean))}`:`[${pick(fn,c.mean)(c.lo)}–${pick(fn,c.mean)(c.hi)}]`;
/* what card h reached running one catalogue entry alone, per second (fld ops_per_s or bytes_per_s); pooled: the mean
   over the cards that ran it; null when h did not */
const rateC=(k,fld,h)=>{const v=(h==null||h==='pooled'?CARDLIST:[h]).map(c=>SUMM(c)[k]).filter(s=>s&&s[fld]&&s[fld].mean>0).map(s=>s[fld].mean);
  return v.length?v.reduce((a,b)=>a+b,0)/v.length:null;};
/* a mark in a card's registry colour and shape (dot, ring, diamond), with a larger hit target and a tooltip */
function cmark(f,parent,h,cx,cy,r,hitR,html){const gg=CK.el('g',{},parent); if(hitR)CK.el('circle',{cx,cy,r:hitR,class:'ck-hit'},gg);
 CK.cardMark(gg,h,cx,cy,r); CK.tip(f,gg,html); return gg;}
/* legend items for cards, in the card's registry mark, or hollow in another colour (CK.legend's swatches are filled
   diamonds: legendMarks redraws a hollow one, for aifoundry1-c1 in the wire chart) */
const cardItem=(h,label,hollowCol)=>{const c=CK.card(h); return {key:c.id,label,color:hollowCol||c.color,mark:hollowCol?'ring':c.mark,shape:c.mark,hollow:!!hollowCol};};
function legendMarks(host,items){const lis=$(host).querySelectorAll('.ck-li');
 items.forEach((it,k)=>{if(it.shape!=='diamond'||!it.hollow||!lis[k])return; const s=lis[k].querySelector('svg'); if(!s)return; while(s.firstChild)s.removeChild(s.firstChild);
  const p=CK.el('polygon',{points:'9,0 14,5 9,10 4,5'},s); p.style.fill='none'; p.style.stroke=it.color; p.style.strokeWidth='1.5';});}
const at={}; D.sync.atomics.runs.forEach(r=>at[r.label]=r);
const HOT=RR.hotline_over_idle_w&&RR.hotline_over_idle_w.contended;       /* 1,024 minions stalled on one line, W over idle */
const TB=D.tensor.bars||{};
const rp={}; D.relay.power.media.forEach(m=>rp[m.medium]=m);
const MH=D.comm.mesh_hops||{};
/* a mark: a group with a visible shape and a larger invisible hit target, carrying a tooltip */
function mark(f,parent,shape,attrs,hitR,html){const gg=CK.el('g',{},parent); if(hitR&&attrs.cx!=null)CK.el('circle',{cx:attrs.cx,cy:attrs.cy,r:hitR,class:'ck-hit'},gg);
 CK.el(shape,attrs,gg); CK.tip(f,gg,html); return gg;}
const CLASSES=[['Scalar integer, one cycle',['add','sub','and','or','xor','sll','srl','sra','slt','sltu','addw','subw','sllw','srlw','sraw','addi','andi','ori','xori','slli','srli','srai','slti','sltiu','addiw','lui','auipc','nop']],
  ['Scalar integer multiply and divide',['mul','mulh','mulhu','mulhsu','mulw','div','divu','rem','remu','divw','divuw','remw','remuw']],
  ['Scalar float',['fadd.s','fsub.s','fmul.s','fmin.s','fmax.s','fsgnj.s','fsgnjn.s','fsgnjx.s','fmadd.s','fmsub.s','fnmadd.s','fnmsub.s']],
  ['Between the float and integer register files',['feq.s','flt.s','fle.s','fclass.s','fcvt.w.s','fcvt.wu.s','fmv.x.w','fcvt.s.w','fcvt.s.wu','fmv.w.x']],
  ['Vector float, 8 lanes',['fadd.ps','fsub.ps','fmul.ps','fmin.ps','fmax.ps','fsgnj.ps','fsgnjn.ps','fsgnjx.ps','fmadd.ps','fmsub.ps','fnmadd.ps','fnmsub.ps','feq.ps','flt.ps','fle.ps','fcmov.ps','fcmovm.ps','fround.ps','ffrc.ps','fclass.ps','fcvt.ps.pw','fcvt.pw.ps','fswizz.ps']],
  ['Vector integer, 8 lanes',['fadd.pi','fsub.pi','fmul.pi','fmulh.pi','fmulhu.pi','fand.pi','for.pi','fxor.pi','fnot.pi','fsll.pi','fsrl.pi','fsra.pi','fmin.pi','fmax.pi','fminu.pi','fmaxu.pi','feq.pi','flt.pi','fltu.pi','fle.pi','faddi.pi','fandi.pi','fslli.pi','fsrli.pi','fsrai.pi','fpackrepb.pi','fpackreph.pi']],
  ['Transcendental unit, 8 lanes',['fexp.ps','flog.ps','frcp.ps']],['Masks and broadcasts',['feqm.ps','fltm.ps','flem.ps','fbcx.ps','fbci.ps','fbci.pi']],
  ['Loads and stores that hit the L1',['lb','lh','lw','ld','lbu','lhu','lwu','sb','sh','sw','sd','flw','fsw','flw.ps','fsw.ps']],['Loads and stores that bypass the L1',['flwl.ps','fswl.ps']],
  ['Branches and jumps',['beq_taken','bne_nottaken','blt_data','bge_data','bltu_data','bgeu_data','jal']],['Atomics on a private line',['amoaddl.w','amoswapl.w','amoorl.w','amomaxl.w','amoaddl.d','amoaddg.w','amoaddg.d']],
  ['System',['csrr_fccnb','fence']],['Compressed against full-width, in-place forms',['c.add','add_norvc','c.addi','addi_norvc','c.mv','c.li']]];
const LANES=new Set([...CLASSES[4][1],...CLASSES[5][1],...CLASSES[6][1],...CLASSES[7][1]]);
/* the wire read interpolated to a fractional hop count (the relay's next shire is 3.5 hops away on average); on card h
   (not pooled) its mean and the range over its passes */
const wireAt=(hh,o,h)=>{const lo=Math.floor(hh),hi=Math.ceil(hh),t0=hi>lo?(hh-lo)/(hi-lo):0;
 if(h!=null&&h!=='pooled'){const a=cbc(`wire/hop${lo}/${o}`,h),b=cbc(`wire/hop${hi}/${o}`,h); if(!a||!b)return null; const mx=k=>a[k]+(b[k]-a[k])*t0;
  return {mean:mx('mean'),lo:mx('lo'),hi:mx('hi'),n:Math.min(a.n,b.n),card:h};}
 const a=cb(`wire/hop${lo}/${o}`),b=cb(`wire/hop${hi}/${o}`); if(!a||!b)return null;
 const t=hi>lo?(hh-lo)/(hi-lo):0, mix=k=>a[k]+(b[k]-a[k])*t, pc={};
 for(const h in a.per_card)if(b.per_card[h])pc[h]={mean:a.per_card[h].mean+(b.per_card[h].mean-a.per_card[h].mean)*t,se:Math.max(a.per_card[h].se,b.per_card[h].se)};
 return {mean:mix('mean'),lo:mix('lo'),hi:mix('hi'),n:Math.min(a.n,b.n),per_card:pc};};
const HH=MH.xshire1?MH.xshire1.mean:3.5;
/* off-rail energy per byte on aifoundry2: power over idle less the three rails and the fitted delivery losses on them
   (the attribution of Limits of observability §4.2; coefficients in D.unmetered) */
const offRail=k=>{const u=D.unmetered&&D.unmetered.aifoundry2, e=SA[k]; if(!u||!e||!e.bytes_per_s.mean)return null;
 const r=e.rails_over_w, m=r.minion_w.mean, s=r.sram_w.mean, n=r.noc_w.mean, c=u.coef;
 return (e.over_idle_w.mean-m-s-n-(c.minion*m+c.sram*s+c.noc*n))/e.bytes_per_s.mean*1e12;};

/* place text labels next to points without overlapping each other or the given boxes; a label that fits nowhere
   is left out (the tooltip still names the point). items: {x, y, text}; boxes: [x0, y0, x1, y1]; bounds likewise */
function placeLabels(parent,items,boxes,bounds,cls){const bx=boxes.slice(), wOf=t=>t.length*6.3+2, H=12;
 const hit=b=>b[0]<bounds[0]||b[2]>bounds[2]||b[1]<bounds[1]||b[3]>bounds[3]||bx.some(o=>!(b[2]<=o[0]||b[0]>=o[2]||b[3]<=o[1]||b[1]>=o[3]));
 items.forEach(it=>{const w=wOf(it.text);
  for(const [dx,dy,an] of [[9,4,'start'],[-9,4,'end'],[0,-10,'middle'],[0,18,'middle'],[8,-8,'start'],[8,16,'start'],[-8,-8,'end'],[-8,16,'end'],[0,-22,'middle'],[0,30,'middle'],[-10,-20,'end'],[10,-20,'start'],[-10,28,'end'],[10,28,'start']]){
   const x0=an==='start'?it.x+dx:an==='end'?it.x+dx-w:it.x+dx-w/2, b=[x0,it.y+dy-10,x0+w,it.y+dy-10+H]; if(hit(b))continue;
   bx.push(b); const t=CK.txt(parent,it.x+dx,it.y+dy,it.text,cls||'lab',an); t.classList.add('halo'); if(it.series)t.setAttribute('data-series',it.series); return;}});}

/* ---------- KPIs ---------- */
/* a value with its 99% interval, {mean, ci99}: "0.10 [0.06–0.15]" */
const wci=(x,fn)=>x&&x.ci99&&x.ci99[0]!=null?`${fn(x.mean)} [${fn(x.ci99[0])}–${fn(x.ci99[1])}]`:x?fn(x.mean):'—';
const sgw=v=>(v<0?'−':'+')+f2(Math.abs(v));
const mf2=v=>(v<0?'−':'')+f2(Math.abs(v));   /* a signed value with a true minus sign */
const sg1=v=>(v<0?'−':'+')+f1(Math.abs(v));
/* a list joined with semicolons, the last with "and": for items that carry commas of their own */
const semiList=a=>a.length<2?a.join(''):a.slice(0,-1).join('; ')+'; and '+a[a.length-1];
(function(){
 /* D3 (version 3): the idle law is led by its measured slope; its split into fixed and leakage is the range over the
    e-foldings that fit the idle bins equally well (R.profile, build_energy_manual.py) */
 const PF=R.profile, lkr=PF?`${f0(PF.A_leak_80_w[0])}–${f0(PF.A_leak_80_w[1])} W`:'';
 /* the other cards' idle against the law, over their version-3 idle cycles (v3.idle.law_residual) */
 const LRv=VI.law_residual||{}, oth=CK.cardsIn(LRv).filter(h=>h!==LAWCARD);
 $('k1').textContent=`+${f2(R.lambda_80_w_per_c)} W/°C`;
 if(PF){$('k1sub').textContent=`on ${f1(P80)} W, of which ${lkr} is leakage (the data do not pin the split closer)`;
  $('restlede').textContent=`At rest ${LAWCARD} draws ${f1(P80)} W at 80 °C and ${f2(R.lambda_80_w_per_c)} W more per degree, ${lkr} of it leakage`+
   (oth.length?`; the other cards idle above that law, ${andList(oth.map(h=>`${cname(h)} by ${f1(LRv[h].mean)} W`))}.`:'.');}
 const fm=cb('fmadd.ps/random/h2'), fz=cb('fmadd.ps/zeros/h2'); if(fz)$('k2sub').textContent=`against ${f0(fz.mean)} pJ on zeros: the data decides`; $('k2').textContent=fm?`${f0(fm.mean)} pJ [${f0(fm.lo)}–${f0(fm.hi)}]`:f0(g('fmadd_ps','random',2).pj_per_op)+' pJ';
 const dl=cb('tload/dram/random'),sl=cb('tload/scp/random'); $('k3').textContent=dl&&sl?`${f0(dl.mean/sl.mean)}× [${f0(dl.lo/sl.hi)}–${f0(dl.hi/sl.lo)}]`:f0(g('tload','random',1,false).pj_per_byte/g('tload','random',1,true).pj_per_byte)+'×';
 /* every other card against the first (catalogue.cross_cards: analyze_catalogue.py's cross_card rule per card) */
 const XC=(D.catalogue&&D.catalogue.cross_cards)||{}, xo=CK.cardsIn(XC), DB=D.catalogue&&D.catalogue.die_c_busy_median, TP=(V3.catalogue||{}).temperature||{};
 const pc=v=>f0(Math.abs(100*(1-v))), lower=v=>v<=1?'lower':'higher';
 if(xo.length){$('k4lab').textContent=`${andList(xo.map(cname))} against ${CARDS[0]}, ${XC[xo[0]].n} catalogue entries`;
  $('k4').textContent=xo.map(h=>f3(XC[h].median)).join(' · ');
  $('k4sub').textContent=`median ratios, in that order, each card at its own die temperature (10–90%: ${xo.map(h=>`${f3(XC[h].p10)}–${f3(XC[h].p90)}`).join(' and ')})`;
  const tb=CK.cardsIn(TP).filter(h=>TP[h].decision==='temperature'), RM=(D.catalogue&&D.catalogue.rail_mv)||{}, r0=RM[CARDS[0]];
  /* a card whose median per byte departs from its median per instruction by more than 5% is described by kind */
  const split=h=>{const i=kindMed(h,false), b=kindMed(h,true); return i!=null&&b!=null&&Math.abs(b/i-1)>0.05?[i,b]:null;};
  const one=xo.filter(h=>!split(h)), two=xo.filter(h=>split(h));
  const mvd=(h,k)=>r0&&RM[h]?RM[h][k]-r0[k]:null, mvTxt=h=>{const a=mvd(h,'minion'), b=mvd(h,'sram'); return a==null?'':`, in line with its rails: its minion rail runs ${f0(Math.abs(a))} mV ${a<0?'lower':'higher'} than ${CARDS[0]}'s and its SRAM rail ${f0(Math.abs(b))} mV ${b<0?'lower':'higher'}`;};
  $('cardlede').textContent=(one.length?`Across the catalogue ${andList(one.map((h,i)=>`${cname(h)} reads ${pc(XC[h].median)}% ${lower(XC[h].median)}${i?'':` than ${CARDS[0]}`} (median ${f3(XC[h].median)})`))}, each card at its own die temperature`+
    (DB?` (under load, in the median: ${andList([CARDS[0]].concat(one).filter(h=>DB[h]!=null).map(h=>`${cname(h)} ${f0(DB[h])} °C`))})`:'')+
    (tb.length?`; the energy per operation rises with die temperature, ${andList(tb.map(h=>`${f2(TP[h].beta_pct_per_c.beta)}% per °C on ${cname(h)}`))} (the version-3 check), enough to account for a gap of this size, so that the two cards themselves differ is not established`:'')+'. ':'')+
   two.map(h=>{const [i,b]=split(h); return `${cname(h)} reads ${pc(i)}% ${lower(i)} per instruction (median ${f3(i)}) but ${pc(b)}% ${lower(b)} per byte (${f3(b)})${mvTxt(h)}.`;}).join(' ');}
 /* section 9: the unsensed remainder at idle, per card (catalogue idle stretches, build_energy_manual.py); the largest
    component of idle on a card when it exceeds each metered rail there (catalogue.idle_split) */
 const IU=D.catalogue&&D.catalogue.idle_unsensed, IS=(D.catalogue&&D.catalogue.idle_split)||{};
 const big=CK.cardsIn(IS).every(h=>['minion','sram','noc'].every(k=>IS[h].unsensed>IS[h][k]));
 if(IU)$('unsensed').textContent=`The unsensed remainder, about ${andList(CK.cardsIn(IU).map(h=>`${f0(IU[h].mean)} W on ${cname(h)}`))}${big?`, the largest single component of idle on ${CK.cardsIn(IS).length===CARDLIST.length?'every card':andList(CK.cardsIn(IS).map(cname))},`:','}`;
 /* the correction each burst of the three-pass catalogue received, per card (build_energy_manual.py) */
 const LC=D.catalogue&&D.catalogue.leak_correction;
 if(LC){const lh=CK.cardsIn(LC), a=LC[lh[0]];
  $('corr').textContent=`${f2(a.median_w)} W in the median and ${f2(a.max_w)} W at most over ${lh[0]}'s ${nf(a.bursts)} bursts`+(lh.length>1?` (${lh.slice(1).map(h=>`${f2(LC[h].median_w)} and ${f2(LC[h].max_w)} W over ${cname(h)}'s ${nf(LC[h].bursts)}`).join('; ')})`:'');}
 /* the board value's refresh per card (TEL-S, phase-folding the board-power stream): under the 10 Hz sampler and under a
    light one-command poller; and the service processor's own pass in its stats trace, quiet and under the sampler
    (TEL-P1/P3/P5, v3.sp_pass_ms), which the sampler lengthens on every card */
 const RF=V3.refresh_ms, SPP=V3.sp_pass_ms||{};
 if(RF){const rh=CK.cardsIn(RF), rng=v=>v[0]===v[1]?f0(v[0]):`${f0(v[0])}–${f0(v[1])}`, len=rh.filter(h=>RF[h].lengthens==='positive');
  const md=v=>{v=v.slice().sort((a,b)=>a-b); return v.length%2?v[v.length>>1]:(v[v.length/2-1]+v[v.length/2])/2;};
  const sh=CK.cardsIn(SPP).filter(h=>SPP[h].quiet&&SPP[h].sampled), dQ=h=>md(SPP[h].sampled)-md(SPP[h].quiet);
  const every=sh.length&&sh.every(h=>Math.min(...SPP[h].sampled)>Math.max(...SPP[h].quiet));
  $('refresh').textContent=`under that sampling it takes a new value about every ${andList(rh.map(h=>`${f0(RF[h].sampler_10hz)} ms on ${cname(h)}`))} (three passes each, 26 September). `+
   `Seen by a light poller (one query per 0.1 s), the board value's refresh is ${andList(rh.map(h=>`${rng(RF[h].light_poller)} ms`))} in that order; that the 10 Hz sampler lengthens this refresh is resolved at 99% ${len.length?`only on ${andList(len.map(cname))}`:'on no card'}`+
   (sh.length?`. The service processor's own pass, timed in its trace, lengthens under the sampler ${every?(sh.length===CARDLIST.length?'on every card':`on ${andList(sh.map(cname))}`):'on '+andList(sh.filter(h=>dQ(h)>0).map(cname))}: ${andList(sh.map(h=>`from ${f0(md(SPP[h].quiet))} to ${f0(md(SPP[h].sampled))} ms on ${cname(h)}`))} (the medians of three passes, TEL-P1, P3 and P5)`:'');}
 /* the sampler's own latency over the catalogue's bursts, per card (catalogue.sampler) */
 const SM=D.catalogue&&D.catalogue.sampler;
 if(SM){const sh=CK.cardsIn(SM), slow=sh.filter(h=>SM[h].over_60ms>0), none=sh.filter(h=>!SM[h].over_60ms);
  $('slowsampler').textContent=`Some DRAM-read bursts (tensor loads from DRAM and the 1 KB row walks) slowed the sampler itself, to a median of up to ${f0(Math.max(...sh.map(h=>SM[h].max_ms)))} ms per sample against the usual ${f0(SM[sh[0]].median_ms)} ms: ${andList(slow.map(h=>`${WORD[SM[h].over_60ms]||SM[h].over_60ms} of ${nf(SM[h].bursts)} bursts on ${cname(h)}`))} ran over 60 ms${none.length?`, none on ${andList(none.map(cname))}`:''}`;}
 /* the minion rail's voltage at 600 MHz and each card's firmware (v3.idle.clocks) */
 const CL=VI.clocks;
 if(CL){const ch=CK.cardsIn(CL), fw=[...new Set(ch.map(h=>CL[h].firmware))];
  $('railmv').textContent=`the minion rail reads ${andList(ch.map(h=>`${(CL[h].mv/1000).toFixed(3)} V on ${cname(h)}`))} at idle in the version-3 idle cycles (firmware ${andList(ch.map(h=>CL[h].firmware))}, in that order)`;}
 /* section 3's operating point: the minion rail over the catalogue's bursts, each card's median reading (catalogue.rail_mv) */
 const RMV=D.catalogue.rail_mv||{}, rmv=CK.cardsIn(RMV).map(h=>RMV[h].minion/1000);
 if(rmv.length){const lo=Math.min(...rmv).toFixed(2), hi=Math.max(...rmv).toFixed(2); $('instrmv').textContent=`${lo===hi?lo:lo+'–'+hi} V on the minion rail (each card's median reading over the catalogue; section 8 gives them)`;}
 /* section 10: the relay against the DRAM round trip, per card (reruns.relay_pj_per_byte) */
 const rr=RR.relay_pj_per_byte||{};
 if(rr.dram&&rr.hop){const rh=CK.cardsIn(rr.dram.per_card).filter(h=>rr.hop.per_card[h]);
  $('relayrel').textContent=`about a ${Math.round(rr.dram.mean/rr.hop.mean)===13?'thirteenth':Math.round(rr.dram.mean/rr.hop.mean)===12?'twelfth':'1/'+f0(rr.dram.mean/rr.hop.mean)} of the energy`;}
 /* the lede's round numbers, from the catalogue's pooled means: the awake core, three instructions, three byte paths */
 const cm=k=>(cb(k)||{}).mean, sp1=S2['spin/zeros/h1'], rngB=ks=>{const v=ks.map(cm).filter(x=>x!=null); return [Math.min(...v),Math.max(...v)];};
 const r5=(v,up)=>Math.round(v/5)*5, sc=rngB(['tload/scp/zeros','tload/scp/random','tstore/scp/zeros','tstore/scp/random']), dr=rngB(['tload/dram/zeros','tload/dram/random','tstore/dram/zeros','tstore/dram/random']), ws=rngB(['st_stream/dram/zeros','st_stream/dram/random']);
 if(sp1&&cm('add/zeros/h2')!=null)$('ledenums').textContent=`An awake minion is ${f0(sp1.over_idle_w.mean/1024*1e3)} mW. On zeros an integer add is ${f0(cm('add/zeros/h2'))} pJ, a float add ${f0(cm('fadd.s/zeros/h2'))} and an eight-lane multiply-add ${f0(cm('fmadd.ps/zeros/h2'))}; on random data ${f0(cm('add/random/h2'))}, ${f0(cm('fadd.s/random/h2'))} and ${f0(cm('fmadd.ps/random/h2'))}. A byte from the shire's own scratchpad is ${f0(Math.floor(sc[0]))}–${f0(Math.ceil(sc[1]))} pJ; from DRAM, ${r5(dr[0])}–${r5(dr[1])}; written back through the L1 to DRAM, ${Math.round(ws[0]/10)*10}–${Math.round(ws[1]/10)*10}.`;
 const t32=D.tensor.rows.find(r=>r.config==='fp32_randn');
 if(t32)$('flipsnow').textContent=` (${f1(t32.over_idle_w)} W in the four runs of 26 September)`;
})();

/* ---------- 1. the card at rest ---------- */
(function(){
 const rl=R.rails_73c;
 /* The unsensed blocks' and the metered rails' slopes come from the version-3 idle cycles (v3.idle: IDLE-c, 26 September;
    three heat-and-cool cycles per card, every sample at 600 MHz); until 25 September the page typed 0.033 and 0.548 W/°C
    from aifoundry2's 23 September catalogue idle gaps (no committed script wrote them). */
 const PF=R.profile, IU=D.catalogue&&D.catalogue.idle_unsensed, rg0=v=>`${f0(v[0])}–${f0(v[1])}`;
 const split=PF?`How much of the ${f1(P80)} W is leakage they do not: the idle bins fit equally well with the leakage e-folding anywhere from ${PF.T_L_window_c[0]} to ${PF.T_L_window_c[1]} °C (doubling every ${rg0(PF.doubling_c)} °C), which puts the leakage at 80 °C at ${rg0(PF.A_leak_80_w)} W and the fixed part at ${rg0(PF.P_fix_w)} W${PF.idle_spread_w_45_95!=null?`, though those fits' idle totals differ by at most ${f1(PF.idle_spread_w_45_95)} W between 45 and 95 °C`:''}. `:'';
 const uns=IU?`draw about ${andList(CK.cardsIn(IU).map(h=>`${f0(IU[h].mean)} W on ${cname(h)} (${rg0(IU[h].die_c)} °C)`))} at idle in the catalogue's idle stretches, and`:`draw about ${f0(rl.unsensed)} W at idle and`;
 const US=VI.unsensed_slope_74_88||{}, RS=VI.rails_slope_75_80||{}, a3u=VI.unsensed_slope_a3_cycles, uo=CK.cardsIn(US).filter(h=>h!==LAWCARD), ro=CK.cardsIn(RS).filter(h=>h!==LAWCARD);
 const slope=US[LAWCARD]?` move little with temperature: ${wci(US[LAWCARD],f2)} W per °C over 74–88 °C on ${LAWCARD} in the version-3 idle cycles (26 September, three per card; the 99% interval)`+
   ((a3u&&a3u.length)||uo.length?`, ${andList([].concat(a3u&&a3u.length?[`${f2(a3u.reduce((x,y)=>x+y,0)/a3u.length)} on aifoundry3`]:[],uo.map(h=>`${wci(US[h],f2)} on ${cname(h)}`)))}`:'')+
   `. The three metered rails carry the leakage, ${wci(RS[LAWCARD],f2)} W per °C between them at 75–80 °C on ${LAWCARD}${ro.length?` (${andList(ro.map(h=>`${wci(RS[h],f2)} on ${cname(h)}`))})`:''}.`
   :` barely move with temperature.`;
 $('resttext').innerHTML=`Everything below is <em>above</em> this. On ${LAWCARD} the idle card draws ${f1(P80)} W at 80 °C and ${f2(R.lambda_80_w_per_c)} W more for each degree there, and that slope is what the idle measurements pin down${PF?` (${f2(PF.lambda_80_w_per_c[0])}–${f2(PF.lambda_80_w_per_c[1])} W per °C for every e-folding that fits)`:''}. ${split}The law drawn below is the best fit, ${f1(R.P_fix_w)} W fixed and ${f1(R.A_leak_80_w)} W of leakage at 80 °C e-folding every ${f0(R.T_L_c)} °C: a fit, not a block-by-block account. The other cards idle above it (the chart). The blocks with no rail sensor (PCIe, the DDR PHY, the IO shire, the regulators) ${uns}${slope} What the unsensed blocks spend when a kernel uses them (DRAM traffic through the DDR PHY, the regulators' delivery loss) is counted in the per-event costs below, and <a href="${HUB}#the-unmetered-remainder-attributed">Limits of observability, §4.2</a> attributes it. The leakage answers to temperature, which the kernel sets.`;
 /* The dots: the whole-degree idle bins the law was fitted to (aifoundry2, 21 September), in ink; then every card's idle bins
    in the version-3 idle cycles (v3.idle.bins, 26 September), each in its registry colour and mark. The law is drawn in ink. */
 const VB=VI.bins||{}, FIT=R.measured_idle.map(p=>({T:p.T,W:p.P,n:p.n}));
 const IB=CK.cardsIn(VB).map(h=>({card:h,pts:VB[h].bins.map(b=>({T:b.T,W:b.W,n:b.cycles,r:b.resid}))}));
 const idleItems=[{key:'law',label:`the law, fitted on ${cname(LAWCARD)}`,mark:'line',color:'var(--ink)'},{key:'fix',label:'its constant, at the best fit',mark:'dash',color:'var(--ref)'},
   {key:'fitbins',label:`${cname(LAWCARD)}, 21 September: the bins it was fitted to`,mark:'dot',color:'var(--ink-2)'}]
   .concat(IB.map(s=>cardItem(s.card,`${cname(s.card)}, 26 September`)));
 CK.legend('idle-legend',idleItems); legendMarks('idle-legend',idleItems);
 const ymax=Math.max(50,...IB.flatMap(s=>s.pts.map(p=>p.W)))+2;
 CK.frame('idle',{height:W=>W<600?270:330,label:'Idle board power against die temperature: the law, the bins it was fitted to, and every card\'s idle in the version-3 cycles',draw:f=>{
  const L=40,Rr=12,T=24,B=40, x=CK.lin(40,95,L,f.W-Rr), y=CK.lin(10,Math.ceil(ymax/10)*10,f.H-B,T);
  CK.axes(f,{x,y,L,R:Rr,T,B,xt:[40,50,60,70,80,90],yt:[10,20,30,40,50,60].filter(v=>v<=Math.ceil(ymax/10)*10),xl:'die temperature, °C',yl:'idle board power, W'});
  const law=[]; for(let t=40;t<=95;t++) law.push([t,lawAt(t)]);
  CK.el('path',{d:CK.path(law,x,y),class:'ln',stroke:'var(--ink)'},f.svg);
  CK.el('line',{x1:L,x2:f.W-Rr,y1:y(R.P_fix_w),y2:y(R.P_fix_w),stroke:'var(--ref)','stroke-width':1.5,'stroke-dasharray':'5 4'},f.svg);
  CK.txt(f.svg,f.W-Rr-4,y(R.P_fix_w)-6,'best-fit constant '+f1(R.P_fix_w)+' W','lab','end');
  CK.keynav(f,FIT.map(p=>mark(f,f.svg,'circle',{cx:x(p.T),cy:y(p.W),r:2.6,fill:'var(--ink-2)'},7,`${cname(LAWCARD)}, 21 September, ${p.T} °C: <b>${f2(p.W)} W</b> (${nf(p.n)} samples), one of the bins the law was fitted to<br>the law: ${f2(lawAt(p.T))} W`)));
  IB.forEach(s=>{const nm=cname(s.card);
   CK.keynav(f,s.pts.map(p=>cmark(f,f.svg,s.card,x(p.T),y(p.W),s.card===LAWCARD?3.5:4,8,`${nm}, 26 September, ${p.T} °C: <b>${f2(p.W)} W</b> (the mean of ${WORD[p.n]||p.n} cycle${p.n>1?'s':''})<br>the ${s.card===LAWCARD?'':cname(LAWCARD)+' '}law: ${f2(lawAt(p.T))} W (${sgw(p.r)} W)`)));});
 }});
 /* the fitted bins as contiguous runs of whole degrees (64–67 and 81–88 °C) */
 const runs=[]; FIT.map(p=>p.T).sort((a,b)=>a-b).forEach(t=>{const r=runs[runs.length-1]; if(r&&t===r[1]+1)r[1]=t; else runs.push([t,t]);});
 const LRv=VI.law_residual||{}, L2=VI.law_residual_a2;
 const v3cap=(L2||CK.cardsIn(LRv).length)?` Coloured: each card's idle bins in the version-3 check's three heat-and-cool cycles (26 September, every sample at 600 MHz): `+
   semiList([].concat(L2?[`${LAWCARD} ${sgw(L2.mean)} W [${sgw(L2.ci99[0])}, ${sgw(L2.ci99[1])}] from the law at ${L2.T[0]}–${L2.T[1]} °C`]:[],
    CK.cardsIn(LRv).filter(h=>h!==LAWCARD).map(h=>`${cname(h)} ${sgw(LRv[h].mean)} W [${sgw(LRv[h].ci99[0])}, ${sgw(LRv[h].ci99[1])}] at ${LRv[h].T[0]}–${LRv[h].T[1]} °C, the gap growing ${LRv[h].slope_w_per_c.mean<0.1?f3(LRv[h].slope_w_per_c.mean):f2(LRv[h].slope_w_per_c.mean)} W per °C`)))+
   ` (the mean over the cycles and its 99% interval); section 7.1 prices each card with its own law.`:'';
 const lf=t=>PF.leak_frac[String(t)].map(v=>Math.round(100*v)).join('–')+'%';
 const share=PF?` Leakage share on ${LAWCARD} over the e-foldings that fit (${PF.T_L_window_c[0]}–${PF.T_L_window_c[1]} °C): ${lf(60)} at 60 °C, ${lf(80)} at 80 °C, ${lf(90)} at 90 °C (${Math.round(100*R.curve.find(c=>c.T===60).leak_frac)}%, ${Math.round(100*R.curve.find(c=>c.T===80).leak_frac)}% and ${Math.round(100*R.curve.find(c=>c.T===90).leak_frac)}% at the best fit).`:
  ` Leakage share: ${Math.round(100*R.curve.find(c=>c.T===60).leak_frac)}% at 60 °C, ${Math.round(100*R.curve.find(c=>c.T===80).leak_frac)}% at 80 °C, ${Math.round(100*R.curve.find(c=>c.T===90).leak_frac)}% at 90 °C.`;
 $('idlecap').textContent=`Line: the law fitted on 21 September, P = ${f1(R.P_fix_w)} W + ${f1(R.A_leak_80_w)} W·e^((T−80)/${f0(R.T_L_c)}), whose slope at 80 °C is ${f2(R.lambda_80_w_per_c)} W per °C. Grey dots: the whole-degree idle bins of that session on ${LAWCARD} the law was fitted to, ${andList(runs.map(r=>r[0]===r[1]?`${r[0]}`:`${r[0]}–${r[1]}`))} °C${runs.length>1?`, none between, so the law is interpolated from ${runs[0][1]} to ${runs[1][0]} °C`:''}.${v3cap}${share}`;
 /* the rail split at 73 °C: aifoundry2 on 22 September, and each card's 73 °C bin in the version-3 idle cycles (v3.idle.split_73c) */
 const SP=VI.split_73c||{}, sc=CK.cardsIn(SP), OUT=VI.outcomes||{};
 const rows=[['Minions','minion'],['SRAM: L2, L3, scratchpad','sram'],['Mesh','noc'],['No rail sensor: PCIe, DDR PHY, IO shire, regulators','unsensed']];
 const cyc=h=>SP[h].minion.n;
 $('rails').innerHTML=`<thead><tr><th>Idle at 73 °C, by rail</th><th class="num">W, ${cshort(LAWCARD)}, 22 Sep</th><th class="num">Share</th>`+sc.map(h=>`<th class="num">${cshort(h)}, 26 Sep (${WORD[cyc(h)]||cyc(h)} cycle${cyc(h)>1?'s':''})</th>`).join('')+'</tr></thead><tbody>'+
  rows.map(r=>`<tr><td>${r[0]}</td><td class="num">${f2(rl[r[1]])}</td><td class="num">${Math.round(100*rl[r[1]]/rl.board)}%</td>`+sc.map(h=>`<td class="num">${f2(SP[h][r[1]].mean)}</td>`).join('')+'</tr>').join('')+
  `<tr><td><b>Board</b> <span class="small">(${LAWCARD} on 22 September at ${f0(rl.die_c)} °C, ${rl.hours_idle!=null?f1(rl.hours_idle):'about 20'} hours after the last workload, apart from a 4.9 s single-hart probe a few minutes before: ${rl.samples||300} samples over a minute, sd ${f2(rl.board_sd!=null?rl.board_sd:0.04)} W; the rails' sd 0.01 W or less.`+
  (sc.length?` The 26 September columns are the 73 °C bin of the version-3 idle cycles, which ${andList(sc.map(h=>cyc(h)===3?`all three of ${cname(h)}'s`:`${WORD[cyc(h)]||cyc(h)} of ${cname(h)}'s three`))} reached; ${SP[LAWCARD]&&cyc(LAWCARD)<3?`${LAWCARD}'s agree with 22 September to within ${f2(Math.max(...rows.map(r=>Math.abs(SP[LAWCARD][r[1]].mean-rl[r[1]]))))} W, one cycle short of the three the check needed, so the split is not confirmed there`:''}${sc.filter(h=>h!==LAWCARD).length?`; ${andList(sc.filter(h=>h!==LAWCARD).map(h=>`${cname(h)} draws ${f1(SP[h].board.mean-rl.board)} W more`))}, on every rail`:''}.`:'')+
  `)</span></td><td class="num"><b>${f2(rl.board)}</b></td><td></td>`+sc.map(h=>`<td class="num"><b>${f2(SP[h].board.mean)}</b></td>`).join('')+'</tr></tbody>';
})();

/* ---------- 1.1 the SRAM arrays at rest ---------- */
(function(){
 const C=D.catalogue, sl=C.cards[CARDS[0]].sram_leakage; if(!(sl&&sl.fit&&sl.curve.length>2))return;
 const fit=sl.fit, lawS=t=>fit.P_fix_w+fit.A_leak_80_w*Math.exp((t-80)/36);
 const xs=sl.curve.map(c=>c.T), ys=sl.curve.map(c=>c.sram_w);
 /* every other card's idle bins, in its registry colour and mark; the fit in ink over its own range, dashed where extrapolated */
 const OS=CARDS.slice(1).map(h=>{const s=C.cards[h].sram_leakage; return {h,inr:s&&s.curve?s.curve:[]};}).filter(o=>o.inr.length);
 const allT=xs.concat(...OS.map(o=>o.inr.map(c=>c.T))), ys2=ys.concat(...OS.map(o=>o.inr.map(c=>c.sram_w)));
 const t0=Math.min(...allT)-1, t1=Math.max(...allT)+1, f0x=Math.min(...xs), f1x=Math.max(...xs);
 const sramItems=[{key:'fit',label:`fit on ${CARDS[0]}, 36 °C e-folding imposed (dashed: extrapolated)`,mark:'line',color:'var(--ink)'},cardItem(CARDS[0],cname(CARDS[0])+' idle bins')].concat(OS.map(o=>cardItem(o.h,cname(o.h)+' idle bins')));
 CK.legend('sram-legend',sramItems); legendMarks('sram-legend',sramItems);
 CK.frame('sram',{height:W=>W<600?240:280,label:'The SRAM rail at idle against die temperature, every card',draw:f=>{
  const L=44,Rr=12,T=24,B=40, x=CK.lin(t0,t1,L,f.W-Rr), y=CK.lin(Math.min(...ys2,lawS(t0))*0.9,Math.max(...ys2)*1.05,f.H-B,T);
  CK.axes(f,{x,y,L,R:Rr,T,B,xl:'die temperature, °C',yl:'SRAM rail at idle, W',yfmt:v=>f1(v)});
  const seg=(a,b,dash)=>{const pts=[]; for(let t=a;t<=b+1e-9;t+=0.5)pts.push([t,lawS(t)]); CK.el('path',Object.assign({d:CK.path(pts,x,y),class:'ln',stroke:'var(--ink)'},dash?{'stroke-dasharray':'5 4'}:{}),f.svg);};
  if(t0<f0x-1)seg(t0,f0x-1,true); seg(Math.max(t0,f0x-1),Math.min(t1,f1x+1),false); if(t1>f1x+1)seg(f1x+1,t1,true);
  CK.keynav(f,sl.curve.map(c=>cmark(f,f.svg,CARDS[0],x(c.T),y(c.sram_w),3.5,8,`${cname(CARDS[0])}, ${c.T} °C: <b>${f3(c.sram_w)} W</b> on the SRAM rail (${nf(c.n)} idle samples)<br>the fit: ${f3(lawS(c.T))} W`)));
  OS.forEach(o=>CK.keynav(f,o.inr.map(c=>cmark(f,f.svg,o.h,x(c.T),y(c.sram_w),4.5,8,`${cname(o.h)}, ${c.T} °C: <b>${f3(c.sram_w)} W</b> on the SRAM rail (${nf(c.n)} idle samples)<br>the ${CARDS[0]} fit${c.T<f0x?', extrapolated':''}: ${f3(lawS(c.T))} W`))));
 }});
 /* the other cards against the aifoundry2 fit, heated across its range in the version-3 idle cycles (v3.idle.sram_slope, IDLE-e;
    the excess is over the aifoundry2 law as registered, −0.32 + 2.81 W, from the 23 September catalogue) */
 const SS=VI.sram_slope||{}, so=CK.cardsIn(SS), top=VI.heater_top_c||{};
 const sl2note=so.length?` The ${CARDS[0]} fit does not describe the other cards: in the version-3 idle cycles, heated from about 55 °C into the fit's own range, ${semiList(so.map(h=>`${cname(h)}'s rail sat ${f2(SS[h].excess_over_a2_law[0])}–${f2(SS[h].excess_over_a2_law[1])} W above it at ${SS[h].T[0]}–${SS[h].T[1]} °C, rising ${f3(SS[h].mean)} W per °C`))}, so the difference is the card, not the fit's shape outside its range.`+
   (top.aifoundry3?` aifoundry3 idles cooler (${f0(C.idle_unsensed.aifoundry3.die_c[0])}–${f0(C.idle_unsensed.aifoundry3.die_c[1])} °C in the catalogue's idle stretches) but is not held cool: the heater took it to ${andList([...new Set(top.aifoundry3)].map(v=>v+' °C'))} in each of its three cycles.`:''):'';
 const c80=sl.curve.find(c=>c.T===80), rd=cb('tload/scp/random');
 const mb=c80?1000*c80.sram_w/128:fit.mw_per_mb_at_80, nj=mb/1048576*1e6;
 $('sramcap').textContent=`The rail feeding 128 MB of on-chip SRAM, at idle, in the catalogue's idle stretches (26 September). Fitted on ${CARDS[0]} (${f0x}–${f1x} °C) with the idle law's 36 °C e-folding imposed: ${f2(fit.P_fix_w).replace('-','−')} W + ${f2(fit.A_leak_80_w)} W·e^((T−80)/36); ${fit.P_fix_w<0?'the negative constant says the rail rises faster than that shape. ':''}`+
  (c80?`On ${CARDS[0]} the whole rail at 80 °C is ${f2(c80.sram_w)} W, ${f1(mb)} mW per MB, an upper bound on the arrays' leakage including the cache logic. `:'')+
  `At about ${f0(mb)} mW per MB, a byte held in scratchpad for one second at 80 °C leaks at most about ${f0(nj)} nJ on ${CARDS[0]} — as much as reading it ${rd?nf(Math.round(nj*1000/rd.mean/100)*100):'—'} times (${rd?f1(rd.mean):'—'} pJ per read).`+sl2note;
})();

/* ---------- 2. awake ---------- */
(function(){
 const s1=g('spin','zeros',1),s2=g('spin','zeros',2), c1=cb('spin/zeros/h1'), c2=cb('spin/zeros/h2');
 const w1=S2['spin/zeros/h1']?S2['spin/zeros/h1'].over_idle_w.mean:s1.over_idle_w, w2=S2['spin/zeros/h2']?S2['spin/zeros/h2'].over_idle_w.mean:s2.over_idle_w;
 const hw=at.contended.over_idle_w, h2w=HOT&&HOT.per_card.aifoundry2?HOT.per_card.aifoundry2.mean:hw;
 const ab=D.awake.spin_hart0_1024, SV=D.awake.spin_v3_w, t=D.tensor.rows.find(r=>r.config==='fp32_randn'), AV=D.tensor.activity_v3_mw_per_minion||{}, AT=D.tensor.activity_term_mw_per_minion||{};
 const lt=launchTxt();
 const WL='https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power';
 const two=(a,b)=>`${a}<br><span class="small">${b}</span>`;
 const avh=CK.cardsIn(AV), mw=(h,n)=>AV[h]&&AV[h][n]!=null?f1(AV[h][n]):'—';
 $('awake').innerHTML='<thead><tr><th>Minions awake, doing the least they can</th><th class="num">pJ per instruction</th><th class="num">per card</th><th class="num">W over idle, 1,024 minions (a2)</th><th class="num">per minion (a2)</th></tr></thead><tbody>'+
  `<tr><td>One hart per minion, an addi loop</td><td class="num">${c1?bt(c1,f1):f1(s1.pj_per_op)}</td><td class="num small">${pcs(c1,f1)}</td><td class="num">${f2(w1)}</td><td class="num">${f2(w1/1024*1e3)} mW</td></tr>`+
  `<tr><td>Both harts</td><td class="num">${c2?bt(c2,f1):f1(s2.pj_per_op)}</td><td class="num small">${pcs(c2,f1)}</td><td class="num">${f2(w2)}</td><td class="num">${f2(w2/1024*1e3)} mW</td></tr>`+
  `<tr><td>${two("The ablation's integer loop, hart 0",`four adds and a branch, about half the one-hart addi loop's issue rate; four 7 s runs on each card, launched at ${lt}; <a href="${WL}">Why is the ET-SoC-1 low power?</a>`)}</td><td class="num">${f1(ab.pj_marginal)} <span class="small">(a2)</span></td><td class="num small">${SV?CK.cardsIn(SV.per_card).map(h=>`${cshort(h)} ${f2(SV.per_card[h].mean)} ± ${f2(SV.per_card[h].se)} W`).join('<br>'):'a2 only, two runs'}</td><td class="num">${f2(ab.over_idle_w)}</td><td class="num">${f2(ab.over_idle_w/1024*1e3)} mW</td></tr>`+
  `<tr><td>${two('1,024 minions stalled on one contended atomic (less than a spinning minion)',`the hot line: each waits about ${nf(Math.round(1024*at.contended.cycles_per_op/1000)*1000)} cycles for its turn`)}</td><td class="num">—</td><td class="num small">${HOT?pcs(HOT,f2)+'<br>both '+bt(HOT,f2):'a2 only, 22 September'}</td><td class="num">${f2(h2w)}</td><td class="num">${f2(h2w/1024*1e3)} mW</td></tr>`+
  `<tr><td>${two('For scale: every minion running a random-data fp32 matmul',`the activity term, section 3.2; per minion with 256, 512 and 1,024 active: ${avh.length?avh.map(h=>`${cshort(h)} ${mw(h,'256')}, ${mw(h,'512')}, ${mw(h,'1024')}`).join('; ')+' mW (four runs each)':''}${AT.fp32_randn_24?`; ${f1(AT.fp32_randn_24)} with 768 (a2, 21 September)`:''}`)}</td><td class="num">—</td><td class="num small">${avh.length?avh.map(h=>`${cshort(h)} ${mw(h,'1024')} mW`).join('<br>'):'a2 only, two runs per point'}</td><td class="num">${f1(t.over_idle_w)}</td><td class="num">${AV[LAWCARD]?mw(LAWCARD,'1024'):f1(AT.fp32_randn||t.over_idle_w/1024*1e3)} mW</td></tr></tbody>`;
 const nop=cb('nop/zeros/h2'), fen=cb('fence/zeros/h2'), T6=(V3.tensor||{}).spin_w||{}, T7=(V3.tensor||{}).active_minions||{};
 const t6r=CK.cardsIn(T6).filter(h=>T6[h].lo>0), t6n=CK.cardsIn(T6).filter(h=>!(T6[h].lo>0));
 const ci3=x=>`${mf2(x.mean)} W [${mf2(x.lo)}, ${mf2(x.hi)}]`;
 const t7f=CK.cardsIn(T7).filter(h=>T7[h].ratio_1024_256>=0.98&&T7[h].ratio_1024_256<=1.10), t7u=CK.cardsIn(T7).filter(h=>!t7f.includes(h));
 if(nop&&fen) $('awaketext').innerHTML=
  `The addi loop is not the floor: it increments seven registers, so its operands change on every instruction. With both harts a <code>nop</code> costs ${f1(nop.mean)} pJ [${f1(nop.lo)}–${f1(nop.hi)}] and a <code>fence</code> ${f1(fen.mean)} [${f1(fen.lo)}–${f1(fen.hi)}] per instruction (section 3.1), so the awake core is about ${f1(fen.mean)}–${f1(nop.mean)} pJ per issue slot.`+
  (t6r.length?` The ablation's integer loop is resolved from idle on ${andList(t6r.map(h=>`${cname(h)} (${ci3(T6[h])})`))}${t6n.length?` but not on ${andList(t6n.map(h=>`${cname(h)} (${ci3(T6[h])})`))}`:''}: the version-3 check's 99% intervals over four runs.`+
   (CK.cardsIn(LO).length&&atL(LAWCARD,'spin')!=null?` But ${loNote()}, on some cards as large as the loop itself: at that temperature it draws ${andList(CK.cardsIn(LO).map(h=>`${rng2(atL(h,'spin'),atLs(h,'spin'),f2)} W on ${cname(h)}`))}.`:''):'')+
  (t7u.length?(()=>{const hs=CK.cardsIn(LO).filter(h=>atL(h,'fp32_randn')!=null&&atL(h,'fp32_randn_8')!=null), rt=h=>(atL(h,'fp32_randn')/1024)/(atL(h,'fp32_randn_8')/256),
     rtS=h=>atLs(h,'fp32_randn')!=null&&atLs(h,'fp32_randn_8')!=null?(atLs(h,'fp32_randn')/1024)/(atLs(h,'fp32_randn_8')/256):null, rts=hs.map(rt).concat(hs.map(rtS).filter(v=>v!=null));
    return ` Per minion, the matmul's power at 1,024 active minions against 256 is ${andList(CK.cardsIn(T7).map(h=>`${f2(T7[h].ratio_1024_256)} on ${cname(h)}`))} as registered, flat within the check's band (0.98–1.10) only on ${andList(t7f.map(cname))}`+
     (hs.length?`; at the die temperature of each launch, where the offset moves the smaller 256-minion runs most, it is ${andList(hs.map(h=>rng2(rt(h),rtS(h),f2)))} in that order, so which card is flat is not settled, and a per-minion figure measured on part of the chip can underprice the whole chip by up to ${f0(100*(Math.max(...rts,...CK.cardsIn(T7).map(h=>T7[h].ratio_1024_256))-1))}%.`:'.');})():'');
})();

/* ---------- 3. instructions ---------- */
(function(){
 const list=[['add','add',1],['xor','xor',1],['mul','mul',1],['fadd.s','fadd.s',1],['fmul.s','fmul.s',1],['fmadd.s','fmadd.s',1],
   ['fadd.ps','fadd.ps ×8',8],['fmul.ps','fmul.ps ×8',8],['fmadd.ps','fmadd.ps ×8',8],['fadd.pi','fadd.pi ×8',8],['fmul.pi','fmul.pi ×8',8],
   ['fexp.ps','fexp.ps ×8',8],['frcp.ps','frcp.ps ×8',8]];
 const q=(n,o)=>cb(`${n}/${o}/h2`), rate=n=>S2[`${n}/random/h2`]?S2[`${n}/random/h2`].ops_per_cycle_per_hart.mean:null;
 if(!q('add','random')){return;}
 const cols={zeros:'var(--c3)',const:'var(--c4)',random:'var(--c2)'}, OPS=[['zeros','zeros'],['const','one constant'],['random','random data']];
 CK.legend('instr-leg',OPS.map(([o,lab])=>({key:o,label:lab,mark:'box',color:cols[o]})));
 const mx=Math.max(...list.map(l=>q(l[0],'random').hi))*1.04;
 CK.frame('instr',{height:W=>W<600?320:360,minW:320,maxW:820,label:`Energy per instruction for ${list.length} scalar and vector instructions on zeros, one constant and random data`,draw:f=>{
  const narrow=f.W<600, L=40,R2=8,T=24,B=narrow?88:72, bw=(f.W-L-R2)/list.length, xg=i=>L+bw*i, y=CK.lin(0,mx,f.H-B,T);
  CK.axes(f,{x:CK.lin(0,list.length,L,f.W-R2),y,L,R:R2,T,B,xt:[],yl:'pJ per instruction, above idle'});
  const nav={}; OPS.forEach(([o])=>nav[o]=[]);
  list.forEach((l,i)=>{OPS.forEach(([o,lab],j)=>{const c=q(l[0],o); if(!c)return; const w=bw*0.26, xx=xg(i)+bw*(0.08+0.28*j);
    const gg=CK.el('g',{'data-series':o},f.svg);
    CK.el('rect',{x:xx,y:y(c.mean),width:w,height:f.H-B-y(c.mean),fill:cols[o]},gg); ebar(gg,xx+w/2,y(c.hi),y(c.lo));
    CK.tip(f,gg,`<b>${l[1]}</b>, ${lab}<br>${f1(c.mean)} pJ per instruction [${f1(c.lo)}–${f1(c.hi)}], n = ${c.n}${l[2]>1?' ('+f1(c.mean/l[2])+' per lane)':''}<br>${pcs(c,f1).replace(/<br>/g,' · ')}`);
    nav[o].push(gg);});
   const lx=xg(i)+bw*0.5, ly=f.H-B+12, t=CK.txt(f.svg,lx,ly,l[1],'tick','end'); t.setAttribute('transform',`rotate(${narrow?-60:-40} ${lx} ${ly})`);});
  OPS.forEach(([o])=>CK.keynav(f,nav[o]));
 }});
 const c0=q('add','random'), nc=Object.keys(c0.per_card).length;
 const r1=rate('add'), slowI=['mul','fexp.ps','frcp.ps'].map(n=>[n,rate(n)]).filter(x=>x[1]&&r1).sort((a,b)=>b[1]-a[1]);
 $('instrcap').innerHTML=`Both harts of every minion issuing the instruction back to back; the multiply and the transcendentals are multi-cycle`+(slowI.length>1?` and issue at ${f2(slowI[0][1]/r1)}× (<code>${slowI[0][0]}</code>) down to ${f2(slowI[slowI.length-1][1]/r1)}× (<code>${slowI[slowI.length-1][0]}</code>) of the one-cycle rate (${cname(CARDS[0])}'s rates, the table's)`:'')+`. Whiskers: the range over ${WORD[c0.n/nc]||c0.n/nc} passes on each of ${WORD[nc]||nc} cards.`;
 $('instrtab').innerHTML='<thead><tr><th>Instruction</th><th class="num">zeros</th><th class="num">constant</th><th class="num">random</th><th class="num">random / zeros</th><th class="num">per lane, random</th><th class="num">issue / hart / cycle</th></tr></thead><tbody>'+
  list.map(l=>{const z=q(l[0],'zeros'),c=q(l[0],'const'),r=q(l[0],'random'); if(!(z&&r))return '';
   return `<tr><td><code>${l[1]}</code></td><td class="num">${bt(z,f1)}</td><td class="num">${bt(c,f1)}</td><td class="num">${bt(r,f1)}</td><td class="num">${f2(r.mean/z.mean)}×</td><td class="num">${l[2]>1?f1(r.mean/l[2]):'—'}</td><td class="num">${rate(l[0])!=null?f2(rate(l[0])):'—'}</td></tr>`;}).join('')+'</tbody>';
 const ia=q('add','zeros'),fa=q('fadd.s','zeros'),vz=q('fadd.ps','zeros'),vr=q('fadd.ps','random'),fm=q('fmadd.ps','random'),ex=q('fexp.ps','random'),lg=q('flog.ps','random');
 const nop=cb('nop/zeros/h2'),fen=cb('fence/zeros/h2');
 const byp=['flwl.ps','fswl.ps'].map(n=>q(n,'random')).filter(Boolean).map(c=>c.mean), amo=['amoaddl.w','amoswapl.w','amoorl.w','amomaxl.w','amoaddl.d','amoaddg.w','amoaddg.d'].map(n=>q(n,'random')).filter(Boolean).map(c=>c.mean);
 const tz=D.tensor.rows.find(r=>r.config==='fp32_randn'), tb=TB.fp32_randn;
 const lane=[(fm.mean-nop.mean)/8,(fm.mean-fen.mean)/8], tref=tb?tb.mean:tz.pj_marginal;
 /* the issue share of the tensor unit's saving, per card: (issue / 8) / (fmadd.ps per lane - tensor unit), with the
    fence or the nop on zeros as the issue cost (the pooled bars mix two cards that differ) */
 const issueShare=tb&&tb.per_card?CK.cardsIn(tb.per_card).filter(h=>tb.per_card[h]&&fm.per_card[h]&&nop.per_card[h]&&fen.per_card[h]).map(h=>{
   const sv=fm.per_card[h].mean/8-tb.per_card[h].mean, sh=[fen,nop].map(c=>100*c.per_card[h].mean/8/sv); return `${f0(Math.min(...sh))}–${f0(Math.max(...sh))}% issue on ${CK.card(h).label}`;}):[];
 /* an integer add on zeros against a nop, per card: the difference of the card means */
 const iz=q('add','zeros'), dd=CK.cardsIn(iz.per_card).filter(h=>nop.per_card[h]).map(h=>iz.per_card[h].mean-nop.per_card[h].mean);
 const dvs=['div','divu','rem','remu'].map(n=>q(n,'random')).filter(Boolean).map(c=>c.mean), rc=q('frcp.ps','random');
 $('instrtext').innerHTML=
  `<b>An integer add on zeros, ${f1(ia.mean)} pJ [${f1(ia.lo)}–${f1(ia.hi)}], costs little more than a <code>nop</code></b> (${f1(nop.mean)} pJ; ${f1(Math.min(...dd))}–${f1(Math.max(...dd))} pJ more on each card): on zeros it is mostly the awake core that issues it. `+
  `<b>A scalar float add costs ${f1(fa.mean/ia.mean)}× an integer add</b> even on zeros; the FPU does not gate on zero. `+
  `<b>An eight-lane vector op on zeros costs the same as the scalar one</b> (${f1(vz.mean)} against ${f1(fa.mean)} pJ, bars overlapping): lanes computing on zeros add nothing, and on random data the lanes cost ${f1(vr.mean/vz.mean)}× — the data dependence of the tensor unit, in the vector unit. `+
  `<b>Per lane, a random-data <code>fmadd.ps</code> is ${f1(fm.mean/8)} pJ [${f1(fm.lo/8)}–${f1(fm.hi/8)}]; the tensor unit does the same multiply-add for ${tb?f1(tb.mean)+' ['+f1(tb.lo)+'–'+f1(tb.hi)+']':f2(tz.pj_marginal)}.</b> `+
  `Take out the vector instruction's issue — ${f1(fen.mean)}–${f1(nop.mean)} pJ, what a fence or a nop costs (section 2) — and the lane is ${f1(Math.min(...lane))}–${f1(Math.max(...lane))} pJ, about ${f0(100*(Math.min(...lane)+Math.max(...lane))/2/tref-100)}% above the tensor unit. Read that way, of the ${f1(fm.mean/8-tref)} pJ per multiply-add the tensor unit saves, roughly half is instruction issue and the rest datapath`+
  (issueShare.length>1?` (${andList(issueShare)}, with the fence or the nop as the issue cost)`:'')+
  `; that is arithmetic on rows whose operands differ (uniform in [0.5, 2) here, normal for the tensor unit), not a measured decomposition. `+
  `<b>The transcendentals rank with the 64-bit divides as the dearest arithmetic</b>: <code>flog.ps</code> is ${f0(lg.mean)} pJ and <code>fexp.ps</code> ${f0(ex.mean)} for eight lanes, at a quarter of the rate, against ${f0(Math.min(...dvs))}–${f0(Math.max(...dvs))} pJ for the 64-bit divides and remainders; <code>frcp.ps</code> (${f0(rc.mean)}) is cheaper. Only loads and stores that bypass the L1 (${f0(Math.min(...byp))}–${f0(Math.max(...byp))} pJ) and atomics (${nf(Math.min(...amo))}–${nf(Math.max(...amo))} pJ) cost more.`;
 $('tensor').innerHTML='<thead><tr><th>Tensor unit, 1,024 minions</th><th class="num">pJ per MAC, marginal</th><th class="num" data-nosort>per card</th><th class="num">pJ per MAC, loaded (a2)</th><th class="num">W over idle (a2)</th><th class="num">MACs per second</th></tr></thead><tbody>'+
  D.tensor.rows.map(t=>{const b=TB[t.config], bc=b?CK.cardsIn(b.per_card):[]; return `<tr><td>${t.label}</td><td class="num">${b?bt(b,f3):'<b>'+f3(t.pj_marginal)+'</b>'}</td><td class="num small">${b?bc.map(h=>`${cshort(h)} ${f3(b.per_card[h].mean)}`).join('<br>')+(b.cards>1?'':`<br>(${cshort(bc[0])} only)`):''}</td><td class="num">${f2(t.pj_loaded)}</td><td class="num">${f2(t.over_idle_w)}</td><td class="num" data-sort="${t.per_s}">${sci(t.per_s)}</td></tr>`;}).join('')+
  '</tbody>';
 /* the tensor rows: the version-3 ablation, four runs on each card (tensor.bars; tensor.rows are aifoundry2's means) */
 const nr=D.tensor.runs_per_card||{}, rcs=CK.cardsIn(nr), CY=(V3.tensor||{}).cycles_per_op||{};
 const hw=k=>TB[k]?100*(TB[k].hi-TB[k].lo)/2/TB[k].mean:null, rw=['fp32_randn','fp16_randn','int8_randn'].map(hw), zw=['fp32_zeros','fp16_zeros','int8_zeros'].map(hw);
 const nrs=[...new Set(rcs.map(h=>nr[h]))], runsTxt=!rcs.length?'its runs':nrs.length===1?`${WORD[nrs[0]]||nrs[0]} runs on ${rcs.length>1?`each of ${WORD[rcs.length]} cards`:cname(rcs[0])}`:andList(rcs.map(h=>`${WORD[nr[h]]||nr[h]} on ${cname(h)}`))+' runs';
 const cyOK=CK.cardsIn(CY).length&&CK.cardsIn(CY).every(h=>CY[h]&&CY[h].fp32&&CY[h].fp32.length===1&&CY[h].int8&&CY[h].int8.length===1);
 $('tensornote').innerHTML=`One instruction per tile: fp32 16×16×16 = 4,096 multiply-adds (MACs), fp16 8,192, int8 16,384, on all 1,024 minions, each run 7 s, launched at ${launchTxt()}: ${CK.card('aifoundry3').label}'s values compare a cool card with warm ones. <b>Marginal</b>: board power above the idle before the launch, per MAC. <b>Loaded</b>: total board power, idle included, per MAC — what a MAC costs when it is the only thing running (${cname(LAWCARD)}'s idle; aifoundry3's is lower and aifoundry1 card 1's higher, section 1). `+
  `The version-3 check's ablation, ${runsTxt} (26 September): the bars are the range over every run on every card, ±${f0(Math.min(...rw))}–${f0(Math.max(...rw))}% on random data and ±${f0(Math.min(...zw))}–${f0(Math.max(...zw))}% on zeros, most of it the difference between the cards.`+
  (cyOK?` The rates are the same on every card: ${f0(CY[CK.cardsIn(CY)[0]].fp32[0])} cycles per instruction (${f0(CY[CK.cardsIn(CY)[0]].int8[0])} for int8) in every timed launch.`:'')+
  (CK.cardsIn(LO).length>1?(()=>{const hs=CK.cardsIn(LO), ps=k=>D.tensor.rows.find(r=>r.config===k).per_s, pj=(h,k)=>f2(atL(h,k)/ps(k)*1e12);
    const a3=LO.aifoundry3||{mean_w:0}, a2=LO.aifoundry2||{mean_w:0}, pjS=(h,k)=>atLs(h,k)!=null?atLs(h,k)/ps(k)*1e12:null, pjR=(h,k)=>rng2(atL(h,k)/ps(k)*1e12,pjS(h,k),f2);
    return ` ${cap1(loNote())}: about ${rng2(Math.abs(a3.mean_w-a2.mean_w),a3.mean_w_step!=null&&a2.mean_w_step!=null?Math.abs(a3.mean_w_step-a2.mean_w_step):null,f1)} W of any difference between aifoundry3 and aifoundry2 comes from the reduction, which is most of the spread on the zeros rows. At the die temperature of each launch the fp32 rows read ${andList(hs.map(h=>pjR(h,'fp32_zeros')))} pJ per MAC on zeros and ${andList(hs.map(h=>pjR(h,'fp32_randn')))} on random data (${andList(hs.map(cname))}).`;})():'')+
  ` Until 25 September these rows were two runs on aifoundry2 and, for fp32, the 22 September card transfer.`;
 const fl=D.tensor.flips;
 $('flips').textContent=Object.keys(fl.e_fJ).map(c=>`${f3(fl.e_fJ[c])} fJ per ${fl.classes[c]}`).join(', ');
})();

/* ---------- 3.2 one multiply-add, by precision and data, on every card (pages-v5) ----------
   D.tensor.bars (the version-3 ablation: mean and range over every run on every card, per_card mean ± se) as
   registered, and each card's value at the die temperature of its launch (note C2: D.tensor.launch_offset, over its two
   readings of the launch temperature) divided by the row's rate (D.tensor.rows[].per_s, the same on every card). The
   dashed reference is one lane of a vector fmadd.ps (section 3, the catalogue: an eight-lane instruction over 8). */
(function(){
 if(!$('tmac'))return;
 const PREC=[['fp32','fp32'],['fp16','fp16'],['int8','int8']], OPS=[['zeros','zeros'],['ones','ones'],['randn','random']];
 const row=k=>D.tensor.rows.find(t=>t.config===k)||null;
 const G=PREC.map(([p,pl])=>({p,pl,rows:OPS.map(([o,ol])=>({k:`${p}_${o}`,o,ol,b:TB[`${p}_${o}`],r:row(`${p}_${o}`)})).filter(x=>x.b&&x.r)})).filter(g=>g.rows.length);
 if(!G.length)return;
 const all=G.flatMap(g=>g.rows), HS=CK.cardsIn(Object.assign({},...all.map(x=>x.b.per_card||{})));
 const pjAt=(h,k)=>{const r=row(k), a=atL(h,k), b=atLs(h,k); if(a==null||!r)return null; const v=[a,b==null?a:b].map(w=>w/r.per_s*1e12); return {lo:Math.min(...v),hi:Math.max(...v),reading:v[0]};};
 const hasLaunch=CK.cardsIn(LO).length>0&&all.every(x=>CK.cardsIn(LO).every(h=>pjAt(h,x.k)));
 const lane=CB['fmadd.ps/random/h2'], laneZ=CB['fmadd.ps/zeros/h2'], LN=[laneZ&&['zeros',laneZ.mean/8],lane&&['random data',lane.mean/8]].filter(Boolean);
 const f3s=v=>v>=10?f1(v):v>=1?f2(v):f3(v);
 const gOf=p=>G.find(g=>g.p===p), rOf=(p,o)=>{const g=gOf(p); return g&&g.rows.find(x=>x.o===o);};
 const ratio=p=>{const z=rOf(p,'zeros'), r=rOf(p,'randn'); return z&&r?r.b.mean/z.b.mean:null;};
 /* the lead: the data against the precision, both as ratios of the pooled means */
 const rz=ratio('fp32'), r32=rOf('fp32','randn'), r8=rOf('int8','randn'), rp=r32&&r8?r32.b.mean/r8.b.mean:null;
 if(rz&&rp){const cmp=rz/rp>1.5?'more than':rp/rz>1.5?'less than':'as much as';
  $('tmaclead').innerHTML=`<b>On the tensor unit the data moves the energy of a multiply-add ${cmp} the precision does</b>: on random data an fp32 multiply-add costs ${f0(rz)}× what it costs on zeros, and an int8 one on random data costs 1/${f0(rp)} of the fp32 one. Each row below is one operand set at one precision, on all 1,024 minions.`;}
 let view='reg';
 const lo0=Math.min(...all.flatMap(x=>[x.b.lo].concat(hasLaunch?HS.map(h=>pjAt(h,x.k)?pjAt(h,x.k).lo:x.b.lo):[]))), hi0=Math.max(...all.map(x=>x.b.hi).concat(LN.map(l=>l[1])));
 const X0=Math.pow(10,Math.floor(Math.log10(lo0*0.9))), X1=Math.pow(10,Math.ceil(Math.log10(hi0*1.1)));
 /* the legend follows the view: as registered, the pooled mean and range; at each launch's temperature, the registered
    range as a grey band behind the cards' bars */
 const REGBAND='color-mix(in srgb, var(--muted) 22%, transparent)';
 const legendFor=v=>CK.legend('tmac-legend',CK.cardLegend(HS).concat([v==='reg'?{key:'mean',label:'all cards: the mean, and the range over every run',color:'var(--ink)',mark:'line'}
  :{key:'regband',label:'all cards as registered: the range over every run',color:'color-mix(in srgb, var(--muted) 45%, var(--surface))',mark:'box'}],LN.length?[{key:'lane',label:'one lane of a vector fmadd.ps (section 3)',color:'var(--ref)',mark:'dash'}]:[]));
 legendFor(view);
 const f=CK.frame('tmac',{label:'Energy per multiply-add on the tensor unit, by precision and operand set, each card and all cards',height:W=>10+G.length*(22+3*27+10)+(W<600?40:34),draw:f=>{
  const L=f.narrow?58:84, Rr=f.narrow?10:16, T=10, B=f.narrow?40:34, x=CK.log(X0,X1,L,f.W-Rr), nodes=[], gh=22, pitch=27, gap=10;
  /* grid: every decade labelled, 2 and 5 between them unlabelled */
  for(let d=Math.log10(X0); d<=Math.log10(X1)+1e-9; d++){const v=Math.pow(10,d);
   CK.el('line',{x1:x(v),x2:x(v),y1:T-6,y2:f.H-B,class:'grid-line'},f.svg); CK.txt(f.svg,x(v),f.H-B+16,CK.fmt.num(v,Math.max(0,-d)),'tick','middle');
   [2,5].forEach(m=>{const u=m*v; if(u<X1)CK.el('line',{x1:x(u),x2:x(u),y1:T-6,y2:f.H-B,class:'grid-line','stroke-dasharray':'2 3'},f.svg);});}
  CK.txt(f.svg,(L+f.W-Rr)/2,f.H-4,'pJ per multiply-add above idle (log)','lab','middle');
  let y=T;
  G.forEach((g,gi)=>{
   const rz2=ratio(g.p), macs=g.p==='fp32'?4096:g.p==='fp16'?8192:16384;
   const gl=CK.txt(f.svg,4,y+14,`${g.pl}`+(rz2?`: random data costs ${f0(rz2)}× zeros`:''),'lab-strong');
   /* the instruction's size follows the group's name, leaving the right of the fp32 header to the lane's label */
   const tw=t=>{let w=0; try{w=t.getComputedTextLength();}catch(_){} return w>0?w:7*t.textContent.length;};
   let hEnd=4+tw(gl);
   if(!f.narrow){const mt=CK.txt(f.svg,hEnd+10,y+14,`${nf(macs)} multiply-adds an instruction`,'tick'); hEnd+=10+tw(mt);}
   /* the vector lane's two values in one label, over its lines at the right of the fp32 header: the longest form that
      clears the header's own text */
   if(g.p==='fp32'&&LN.length){const nm=w=>w==='random data'?'random':'zeros';
    const forms=[(f.narrow?'lane: ':'one lane of a vector fmadd.ps (dashed): ')+LN.map(([w,v])=>`${f1(v)}${f.narrow?'':' pJ'} on ${nm(w)}`).join(', '),
     'lane: '+LN.map(([w,v])=>`${f1(v)} ${nm(w)}`).join(', '),'lane: '+LN.map(([w,v])=>f1(v)).join(', ')];
    const lt=CK.txt(f.svg,f.W-Rr,y+14,forms[0],'tick','end');
    for(const s of forms){lt.textContent=s; if(f.W-Rr-tw(lt)>hEnd+12)break;}}
   const y0g=y+gh;
   /* the vector lane, for scale, across the fp32 rows only (the same multiply-add in fp32) */
   if(g.p==='fp32')LN.forEach(([what,v],j)=>{const gg=CK.el('g',{},f.svg), X=x(v);
    CK.el('rect',{x:X-5,y:y0g,width:10,height:3*pitch,class:'ck-hit'},gg);
    CK.el('line',{x1:X,x2:X,y1:y0g,y2:y0g+3*pitch,stroke:'var(--ref)','stroke-width':1.5,'stroke-dasharray':'4 3'},gg);
    CK.tip(f,gg,`<b>One lane of a vector <code>fmadd.ps</code></b>, ${what}: ${f2(v)} pJ (an eight-lane instruction, ${f1(8*v)} pJ, section 3), what the vector unit pays for the same fp32 multiply-add`);
    nodes.push(gg);});
   g.rows.forEach((r,i)=>{const yc=y0g+pitch*(i+0.5), b=r.b;
    CK.txt(f.svg,L-8,yc+4,r.ol,'lab','end');
    if(i>0)CK.el('line',{x1:L,x2:f.W-Rr,y1:y0g+pitch*i,y2:y0g+pitch*i,class:'grid-line','stroke-opacity':0.5},f.svg);
    const reg=view==='reg';
    /* all cards: the range over every run and the mean (registered values) */
    const rg=CK.el('g',{},f.svg), st={stroke:'var(--ink-2)','stroke-width':1.5};
    if(reg)CK.el('line',Object.assign({x1:x(b.lo),x2:x(b.hi),y1:yc,y2:yc},st),rg);
    else CK.el('rect',{x:x(b.lo),y:yc-9,width:Math.max(2,x(b.hi)-x(b.lo)),height:18,rx:3,fill:REGBAND},rg);
    if(reg){[b.lo,b.hi].forEach(v=>CK.el('line',Object.assign({x1:x(v),x2:x(v),y1:yc-4,y2:yc+4},st),rg));
     CK.el('rect',{x:x(b.mean)-1.5,y:yc-10,width:3,height:20,fill:'var(--ink)'},rg);}
    CK.el('rect',{x:x(b.lo)-4,y:yc-10,width:Math.max(8,x(b.hi)-x(b.lo)+8),height:20,class:'ck-hit'},rg);
    if(reg){const ld=r.r, idleSh=ld&&ld.pj_loaded>0?1-ld.pj_marginal/ld.pj_loaded:null;
     CK.tip(f,rg,`<b>${g.pl}, ${r.ol}</b>, all cards: <b>${f3s(b.mean)}</b> pJ per multiply-add [${f3s(b.lo)}–${f3s(b.hi)}] over ${b.n} runs`+
      (ld?`<br>loaded, ${cname(LAWCARD)}'s idle included: ${f2(ld.pj_loaded)} pJ, ${f0(100*idleSh)}% of it the idle`:'')+`<br>${sci(ld?ld.per_s:0)} multiply-adds a second`);
     nodes.push(rg);}
    else{CK.tip(f,rg,`<b>${g.pl}, ${r.ol}</b>: the registered range over every run on every card, ${f3s(b.lo)}–${f3s(b.hi)} pJ (the grey band, for comparison)`); nodes.push(rg);}
    /* each card: its registered mean, or its value at the die temperature of each launch (a bar over the two readings) */
    HS.forEach((h,j)=>{const p=CK.pick(b,h); if(!p)return; const yy=yc+(j-(HS.length-1)/2)*6, c=CK.card(h);
     if(reg){nodes.push(cmark(f,f.svg,h,x(p.mean),yy,3.5,7,`<b>${g.pl}, ${r.ol}</b>, ${cname(h)}: <b>${f3s(p.mean)}</b> ± ${more(p.se||0,f3s)} pJ per multiply-add (${p.n} runs, as registered)`+(hasLaunch&&pjAt(h,r.k)?`<br>at the die temperature of each launch: ${rng2(pjAt(h,r.k).lo,pjAt(h,r.k).hi,f3s)}`:'')));}
     else{const q=pjAt(h,r.k); if(!q)return; const gg=CK.el('g',{},f.svg), x1=x(q.lo), x2=Math.max(x(q.hi),x1+2);
      CK.el('rect',{x:x1-5,y:yy-5,width:x2-x1+10,height:10,class:'ck-hit'},gg);
      CK.el('line',{x1,x2,y1:yy,y2:yy,stroke:c.color,'stroke-width':3,'stroke-linecap':'round'},gg);
      CK.cardMark(gg,h,x(q.reading),yy,3);
      CK.tip(f,gg,`<b>${g.pl}, ${r.ol}</b>, ${cname(h)}: ${rng2(q.lo,q.hi,f3s)} pJ per multiply-add at the die temperature of each launch (the mark: the whole-degree reading; the bar reaches the reading + ${f2(LO[h].step_c||0)} °C)<br>as registered: ${f3s(p.mean)}`);
      nodes.push(gg);}});
   });
   y=y0g+3*pitch+gap;});
  CK.keynav(f,nodes);
  readout();
 }});
 function readout(){
  const out=$('tmac-readout'); if(!out)return;
  const rr=o=>G.map(g=>rOf(g.p,o)).filter(Boolean), sp=xs=>{const a=Math.min(...xs), b=Math.max(...xs); return [a,b];};
  if(view==='reg'){
   const rand=rr('randn'), zer=rr('zeros'), spr=r=>{const v=HS.map(h=>CK.pick(r.b,h)).filter(Boolean).map(p=>p.mean); return Math.max(...v)/Math.min(...v);};
   out.innerHTML=`As registered (${runsN()}, launched at ${launchTxt()}): on random data a multiply-add costs ${andList(rand.map(r=>`${f3s(r.b.mean)} pJ in ${gOf(r.k.split('_')[0]).pl}`))}; on zeros ${andList(G.map(g=>ratio(g.p)).filter(Boolean).map(v=>f1(v)+'×'))} less. The cards' own means agree within ${f0(100*(Math.max(...rand.map(spr))-1))}% on random data and differ up to ${f1(Math.max(...zer.map(spr)))}× on zeros, where the launch-temperature offset of note C2 is as large as the signal: switch the view to see each card at the die temperature of its launch.`;}
  else{
   const mv=(o)=>{let m=0; rr(o).forEach(r=>HS.forEach(h=>{const p=CK.pick(r.b,h), q=pjAt(h,r.k); if(p&&q)m=Math.max(m,Math.abs(q.lo-p.mean)/p.mean,Math.abs(q.hi-p.mean)/p.mean);})); return m;};
   const r32=rOf('fp32','randn'), z32=rOf('fp32','zeros'), at=r=>sp(HS.map(h=>pjAt(h,r.k)).filter(Boolean).flatMap(q=>[q.lo,q.hi])), rg=r=>sp(HS.map(h=>CK.pick(r.b,h)).filter(Boolean).map(p=>p.mean));
   out.innerHTML=`At the die temperature of each launch (note C2; each card's bar spans its two readings of the launch temperature): fp32 on random data ${f2(at(r32)[0])}–${f2(at(r32)[1])} pJ over the ${WORD[HS.length]} cards (as registered ${f2(rg(r32)[0])}–${f2(rg(r32)[1])}), on zeros ${f2(at(z32)[0])}–${f2(at(z32)[1])} (as registered ${f2(rg(z32)[0])}–${f2(rg(z32)[1])}). The offset moves the random-data rows by at most ${f0(100*mv('randn'))}% and the zeros rows by up to ${f0(100*mv('zeros'))}%: which card is cheapest on zeros is not settled by these runs.`;}
 }
 function runsN(){const nr=D.tensor.runs_per_card||{}, n=[...new Set(CK.cardsIn(nr).map(h=>nr[h]))]; return n.length===1?`${WORD[n[0]]||n[0]} runs on each card`:'every run';}
 if(hasLaunch)CK.seg('tmac-view',{label:'values',options:[['reg','as registered'],['launch','at each launch’s die temperature']],value:view,onChange:v=>{view=v;legendFor(v);f.redraw();}});
})();

/* ---------- 3.1 every instruction: a beeswarm per class (em-v3) ---------- */
(function(){
 const all=[]; CLASSES.forEach((c,ci)=>c[1].forEach(n=>{if(CB[`${n}/random/h2`]&&CB[`${n}/zeros/h2`]&&SA[`${n}/random/h2`])all.push({n,ci});}));
 if(!all.length)return;
 $('trapped').textContent='fdiv.s, fsqrt.s, fdiv.ps, fsqrt.ps, frsq.ps, fsin.ps, fdiv.pi, fdivu.pi, frem.pi, fremu.pi, fcvt.l.s, fcvt.s.l, csrr cycle';
 /* st.card: 'pooled' (the mean over every pass on every card) or a card id; it follows the page's card bus */
 const st={unit:'instr',card:'pooled',zeros:false,found:null};
 const nop=cb('nop/zeros/h2'), fen=cb('fence/zeros/h2');
 const div=a=>st.unit==='lane'&&LANES.has(a.n)?8:1;
 const val=(a,o)=>{const c=cbc(`${a.n}/${o}/h2`,st.card); return c?c.mean/div(a):null;};
 const barTxt=(a,o)=>{const c=cbc(`${a.n}/${o}/h2`,st.card), d=div(a); if(!c)return '—'; if(st.card==='pooled')return `${f1(c.mean/d)} pJ [${f1(c.lo/d)}–${f1(c.hi/d)}]`;
   return c.se!=null?`${f1(c.mean/d)} ± ${f2(c.se/d)} pJ`:`${f1(c.mean/d)} pJ`;};
 const tipHtml=a=>()=>{const k=`${a.n}/random/h2`, rs=CARDS.map(h=>[h,SUMM(h)[k]]).filter(x=>x[1]), r0=rs[0][1], per=st.unit==='lane'&&LANES.has(a.n)?' per lane':'';
   const iss=st.card==='pooled'?rateC(k,'ops_per_cycle_per_hart','pooled'):(SUMM(st.card)[k]||r0).ops_per_cycle_per_hart.mean;
   return `<b>${a.n}</b> — ${CLASSES[a.ci][0]}<br>random: ${barTxt(a,'random')}${per}<br>zeros: ${barTxt(a,'zeros')}${per}; random / zeros ${f2(val(a,'random')/val(a,'zeros'))}×<br>`+
    `issue ${f3(iss)} per hart per cycle<br>${rs.map(([h,r])=>`${cname(h)} ${f1(r.pj_per_op.mean)} ± ${f2(r.pj_per_op.se)}`).join(', ')} pJ`+
    (rs.length===2?`; ratio ${f3(rs[1][1].pj_per_op.mean/r0.pj_per_op.mean)}`:rs.length>2?'; '+rs.slice(1).map(([h,r])=>`${cshort(h)} / ${cshort(rs[0][0])} ${f3(r.pj_per_op.mean/r0.pj_per_op.mean)}`).join(', '):'');};
 const cardLabel=()=>st.card==='pooled'?`${ALLC} (the mean over every pass)`:cname(st.card);
 let lay=null, nodes=[], overlay=null, fr=null;
 function layout(W){
  const key=[W,st.unit,st.card].join('|'); if(lay&&lay.key===key)return lay;
  const L=10,Rr=14,T=30,B=34, lo=st.unit==='lane'?1:3, x=CK.log(lo,2000,L,W-Rr), r=3.5, sep=2*r+1;
  let y0=T; const rows=[];
  CLASSES.forEach((c,ci)=>{const pts=all.filter(a=>a.ci===ci&&val(a,'random')!=null).map(a=>({a,x:x(Math.max(lo,val(a,'random')))})).sort((p,q)=>p.x-q.x);   /* a card without the instruction draws no dot */
   if(!pts.length)return; const placed=[];
   pts.forEach(p=>{for(let k=0;k<200;k++){const o=(k%2?1:-1)*Math.ceil(k/2); if(placed.every(q=>(q.x-p.x)**2+(q.o-o)**2>=sep*sep)){p.o=o;break;}} if(p.o==null)p.o=0; placed.push(p);});
   const ext=Math.max(...placed.map(p=>Math.abs(p.o)));
   rows.push({ci,label:c[0],y:y0,cy:y0+17+ext+r+1,pts:placed}); y0+=17+2*(ext+r+1)+12;});
  lay={key,x,rows,H:y0+B,L,Rr,T,lo}; return lay;}
 /* the same instruction on zeros: a hollow ring in ink (the dots carry the card's colour) */
 const seg=(g,a,cy)=>{const vz=val(a,'zeros'); if(vz==null)return; const xr=lay.x(Math.max(lay.lo,val(a,'random'))),xz=lay.x(Math.max(lay.lo,vz));
  CK.el('line',{x1:xz,x2:xr,y1:cy,y2:cy,stroke:'var(--ink-2)','stroke-width':1.2},g); CK.el('circle',{cx:xz,cy,r:3.5,fill:'var(--surface)',stroke:'var(--ink-2)','stroke-width':1.8},g);};
 const showZero=(i)=>{if(!overlay)return; while(overlay.firstChild)overlay.removeChild(overlay.firstChild); if(i==null)return; const p=nodes[i]; seg(overlay,p.a,p.cy);};
 CK.seg('all-unit',{options:[['instr','per instruction'],['lane','per lane']],value:'instr',onChange:v=>{st.unit=v; fr.redraw(); cap();}});
 CK.cardSeg('all-card',{cards:CARDLIST,pooled:true,label:'card',onChange:v=>{st.card=v; fr.redraw(); cap();}});
 const zb=document.createElement('button'); zb.type='button'; zb.textContent='show zeros for all'; zb.setAttribute('aria-pressed','false');
 zb.addEventListener('click',()=>{st.zeros=!st.zeros; zb.setAttribute('aria-pressed',String(st.zeros)); fr.redraw();});
 const zs=$('all-zeros'); zs.className='controls'; zs.style.margin='0'; zs.appendChild(zb);
 $('all-names').innerHTML=all.map(a=>`<option value="${a.n}">`).join('');
 const ro=CK.readout('all-readout');
 fr=CK.frame('allinstr',{height:W=>layout(W).H,label:'Energy per instruction, every instruction, by class',draw:f=>{
  const Ly=layout(f.W), x=Ly.x, svg=f.svg, top=Ly.T, bot=f.H-34;
  const ticks=(f.W<600?[1,3,10,30,100,300,1000]:[1,2,5,10,20,50,100,200,500,1000,2000]).filter(t=>t>=Ly.lo), xf=v=>CK.fmt.num(v);
  const ax=CK.el('g',{'aria-hidden':'true'},svg), fl=st.unit==='instr'&&nop&&fen, flab=fl?`awake core ${f1(fen.mean)}–${f1(nop.mean)} pJ`:'', fx=fl?x(nop.mean)+4:0, fw=flab.length*6.2;
  ticks.forEach(t=>{CK.el('line',{x1:x(t),x2:x(t),y1:top-6,y2:bot,class:'grid-line'},ax); CK.txt(ax,x(t),bot+16,xf(t),'tick','middle');
   if(!fl||x(t)+12<fx||x(t)-12>fx+fw)CK.txt(ax,x(t),top-10,xf(t),'tick','middle');});
  Ly.rows.slice(1).forEach(rw=>CK.el('line',{x1:Ly.L,x2:f.W-Ly.Rr,y1:rw.y-4,y2:rw.y-4,stroke:'var(--grid)','stroke-dasharray':'2 3'},ax));
  CK.txt(ax,(Ly.L+f.W-Ly.Rr)/2,f.H-4,st.unit==='lane'?'pJ per instruction, or per lane for the vector and transcendental units (log)':'pJ per instruction, above idle (log)','lab','middle');
  if(fl){const x0=x(fen.mean),x1=x(nop.mean); CK.el('rect',{x:x0,y:top-4,width:Math.max(2,x1-x0),height:bot-top+4,fill:'var(--grid)',opacity:0.8},ax);
   CK.txt(ax,fx,top-10,flab,'tick','start');}
  const layer=CK.el('g',{},svg); overlay=CK.el('g',{'aria-hidden':'true'},svg); nodes=[];
  Ly.rows.forEach(rw=>{CK.txt(layer,Ly.L,rw.y+13,rw.label,'lab','start');
   rw.pts.forEach(p=>{const cy=rw.cy+p.o; if(st.zeros)seg(layer,p.a,cy);
    const gg=mark(f,layer,'circle',{cx:p.x,cy,r:3.5,fill:CK.card(st.card).color},7,tipHtml(p.a));
    gg.addEventListener('focus',()=>{showZero(nodes.findIndex(q=>q.g===gg)); ro.set(tipHtml(p.a)());});
    gg.addEventListener('pointerenter',()=>showZero(nodes.findIndex(q=>q.g===gg)));
    gg.addEventListener('pointerleave',()=>showZero(st.found));
    gg.addEventListener('blur',()=>showZero(st.found));
    nodes.push({g:gg,a:p.a,cy,x:p.x,row:rw.ci});});});
  /* the dearest are the two global atomics, whose order is not resolved: label the pair, not one of them */
  const mx=nodes.reduce((a,b)=>val(a.a,'random')>val(b.a,'random')?a:b), mrow=Ly.rows.find(rw=>rw.ci===mx.row);
  const gl=nodes.filter(n=>/^amoaddg\./.test(n.a.n)).map(n=>val(n.a,'random')), gv=gl.length?gl.reduce((a,b)=>a+b,0)/gl.length:val(mx.a,'random');
  const dtx=gl.length===2?`dearest: the global atomics, ~${nf(Math.round(gv/10)*10)} pJ`:`dearest: ${mx.a.n}, ${nf(val(mx.a,'random'))} pJ`;
  if(Ly.L+6.3*mrow.label.length+12<f.W-Ly.Rr-6.3*dtx.length)CK.txt(layer,f.W-Ly.Rr,mrow.y+13,dtx,'lab','end');   /* not where it would run into the row's label */
  CK.keynav(f,nodes.map(n=>n.g),{step:(k,K)=>{if(K!=='ArrowDown'&&K!=='ArrowUp')return null;
   const rs=[...new Set(nodes.map(n=>n.row))], ri=rs.indexOf(nodes[k].row)+(K==='ArrowDown'?1:-1); if(ri<0||ri>=rs.length)return k;
   let best=null; nodes.forEach((n,j)=>{if(n.row===rs[ri]&&(best==null||Math.abs(n.x-nodes[k].x)<Math.abs(nodes[best].x-nodes[k].x)))best=j;}); return best;}});
  if(st.found!=null){const j=nodes.findIndex(n=>n.a.n===st.foundName); st.found=j<0?null:j; showZero(st.found);}
 }});
 const inp=$('all-find');
 const find=()=>{const v=inp.value.trim().toLowerCase(), j=nodes.findIndex(n=>n.a.n.toLowerCase()===v);
  st.found=j<0?null:j; st.foundName=j<0?null:nodes[j].a.n; showZero(st.found); ro.set(j<0?(v?'No instruction by that name in the catalogue.':''):tipHtml(nodes[j].a)()+'<br><span class="small">Enter moves the focus to its dot.</span>'); return j;};
 inp.addEventListener('input',find);
 inp.addEventListener('keydown',ev=>{if(ev.key==='Enter'){const j=find(); if(j>=0){ev.preventDefault(); nodes[j].g.focus();}}});
 const relOf=S=>all.filter(a=>S[`${a.n}/random/h2`]).map(a=>S[`${a.n}/random/h2`].pj_per_op.se/S[`${a.n}/random/h2`].pj_per_op.mean).sort((a,b)=>a-b);
 const rel=relOf(SA), relN=CARDS.slice(1).map(h=>[h,relOf(SUMM(h))]).filter(x=>x[1].length), pct=(r,q)=>(100*r[Math.floor(r.length*q)]).toFixed(1);
 const half=all.map(a=>CB[`${a.n}/random/h2`]).map(c=>(c.hi-c.lo)/2/c.mean).sort((a,b)=>a-b);
 function cap(){const nd=st.card==='pooled'?all.length:all.filter(a=>val(a,'random')!=null).length; $('allcap').textContent=`${nd} instructions, one dot each at its random-data energy on ${cardLabel()}${st.unit==='lane'?', per lane for the eight-lane units':''}, one row per class. The hollow ring and the line to it are the same instruction on zeros: for the dot in focus, or for all of them with the toggle. `+
  (st.unit==='instr'?`The shaded band is the awake core, what a fence or a nop costs with both harts (${f1(fen.mean)}–${f1(nop.mean)} pJ). `:'')+
  `Pass-to-pass standard error is ${(100*rel[rel.length>>1]).toFixed(1)}% in the median and ${(100*rel[Math.floor(rel.length*0.9)]).toFixed(1)}% at the 90th percentile on ${CARDS[0]}${relN.length?` (${relN.map(([h,r])=>`${(100*r[r.length>>1]).toFixed(1)}% and ${pct(r,0.9)}% on ${cname(h)}`).join('; ')})`:''}; half the range over ${ALLC}' passes is ±${(100*half[half.length>>1]).toFixed(1)}% in the median and ±${(100*half[Math.floor(half.length*0.9)]).toFixed(1)}% at the 90th, about half of it the difference between the cards.`;}
 cap();
 const S=SA, gz=(n,o)=>S[`${n}/${o}/h2`], MORE=CARDS.slice(1), ncol=6+CARDS.length+MORE.length;
 $('alltab').innerHTML=`<thead><tr><th>Instruction</th><th class="num">zeros pJ, ${ALLC}</th><th class="num">random pJ, ${ALLC}</th><th class="num">per lane</th><th class="num">random / zeros</th><th class="num">issue per hart per cycle</th>`+
  CARDS.map(h=>`<th class="num">${cname(h)} ± se</th>`).join('')+(MORE.length?'':'<th class="num">card 2 ± se</th><th class="num">ratio</th>')+(MORE.length===1?'<th class="num">ratio</th>':MORE.map(h=>`<th class="num">${cshort(h)} / ${cshort(CARDS[0])}</th>`).join(''))+'</tr></thead><tbody>'+
  CLASSES.map(c=>`<tr><td colspan="${ncol+(MORE.length?0:2)}"><b>${c[0]}</b></td></tr>`+c[1].map(n=>{const r=gz(n,'random'),z=gz(n,'zeros'),cr=cb(`${n}/random/h2`),cz=cb(`${n}/zeros/h2`); if(!(r&&z))return '';
   const rN=MORE.map(h=>SUMM(h)[`${n}/random/h2`]);
   return `<tr><td><code>${n}</code></td><td class="num">${cz?bt(cz,f1):z.pj_per_op.mean.toFixed(1)}</td><td class="num">${cr?bt(cr,f1):'<b>'+r.pj_per_op.mean.toFixed(1)+'</b>'}</td><td class="num">${LANES.has(n)?((cr?cr.mean:r.pj_per_op.mean)/8).toFixed(1):'—'}</td><td class="num">${((cr?cr.mean:r.pj_per_op.mean)/(cz?cz.mean:z.pj_per_op.mean)).toFixed(2)}×</td><td class="num">${r.ops_per_cycle_per_hart.mean.toFixed(3)}</td><td class="num">${r.pj_per_op.mean.toFixed(1)} ± ${r.pj_per_op.se.toFixed(2)}</td>`+
    (MORE.length?rN.map(r2=>`<td class="num">${r2?r2.pj_per_op.mean.toFixed(1)+' ± '+r2.pj_per_op.se.toFixed(2):'—'}</td>`).join('')+rN.map(r2=>`<td class="num">${r2?(r2.pj_per_op.mean/r.pj_per_op.mean).toFixed(3):'—'}</td>`).join(''):'<td class="num">—</td><td class="num">—</td>')+'</tr>';}).join('')).join('')+'</tbody>';
 /* cheapest and dearest by the pooled mean over both cards, the page's convention */
 const pool=all.map(a=>({n:a.n,m:CB[`${a.n}/random/h2`].mean})).sort((a,b)=>a.m-b.m), cheapest=pool[0], dearest=pool[pool.length-1];
 const XC=D.catalogue.cross_cards||{}, xo=CK.cardsIn(XC);
 const span=(ns,o)=>{const v=ns.map(n=>CB[`${n}/${o}/h2`]).filter(Boolean).map(c=>c.mean); return [Math.min(...v),Math.max(...v),v.length];};
 const one=CLASSES[0][1], z1=span(one,'zeros'), r1=span(one,'random');
 const rat=(a,b)=>CB[`${a}/random/h2`]&&CB[`${b}/random/h2`]?CB[`${a}/random/h2`].mean/CB[`${b}/random/h2`].mean:null;
 const dv=rat('divu','mulw'), ag=['amoaddg.w','amoaddg.d'].flatMap(a=>['amoaddl.w','amoaddl.d'].map(l=>rat(a,l))).filter(v=>v);
 /* the two cheapest (fence, nop) and the two dearest (the global atomics) are each a pair whose order is not resolved */
 const two=pool.slice(0,2), top=pool.slice(-2), topm=(top[0].m+top[1].m)/2;
 $('alltext').innerHTML=`The cheapest are <code>${two[0].n}</code> and <code>${two[1].n}</code> (${f1(two[0].m)}–${f1(two[1].m)} pJ on random data) and the dearest the global atomics <code>${top[0].n}</code> and <code>${top[1].n}</code> (about ${nf(Math.round(topm/10)*10)} pJ), a span of about ${f0(Math.round(topm/two[0].m/10)*10)}× (pooled over ${ALLC}); within each pair the order is not resolved. `+
  (xo.length?`Across ${XC[xo[0]].n} configurations, in the median, ${andList(xo.map(h=>`${cname(h)} is ${f3(XC[h].median)}× ${CARDS[0]} (10th to 90th percentile ${f3(XC[h].p10)} to ${f3(XC[h].p90)})`))}, each at its own die temperature; the energy per operation rises with the die's temperature on each card, which is enough to account for those ratios (section 8). `:'')+
  `Instructions that share a unit and a latency cost about the same on zeros — the ${z1[2]} one-cycle integer ops span ${f1(z1[0])}–${f1(z1[1])} pJ — but data and latency spread every class: on random data the same ${r1[2]} span ${f1(r1[0])}–${f1(r1[1])} pJ, a 64-bit divide costs ${f0(dv)}× a <code>mulw</code>, and a global <code>amoaddg</code> ${f0(Math.min(...ag))}× a local <code>amoaddl</code>.`;
})();

/* ---------- 4. where bytes should live: energy per byte against bandwidth (em-v2) ---------- */
(function(){
 const rg=RR.rings_pj_per_byte||{}, rr=RR.relay_pj_per_byte||{};
 const FAM={read:['reads','var(--c1)'],write:['writes','var(--c2)'],msg:['core to core (rings of section 5)','var(--c7)'],relay:['the relay (a read and a write)','var(--c3)']};
 /* every point: e(o, h) its energy per byte on card h (h 'pooled' or left out: every pass on every card), null when h has
    none; gbs(o, h) its bandwidth on h (pooled: the mean over the cards), rcard the one card a bandwidth was timed on when
    only one was (the rings and the relay) */
 const RCARD=srcCard(D.comm.source), YCARD=srcCard(D.relay.source);
 const P=[], cat=(fam,k,sfx,sc,label,short)=>{if(!CB[`${k}/random${sfx}`])return; const kk=o=>`${k}/${CB[`${k}/${o}${sfx}`]?o:'random'}${sfx}`;
  P.push({fam,label,short,key:k,rcard:null,
   e:(o,h)=>cbc(kk(o),h,sc), op:o=>CB[`${k}/${o}${sfx}`]?o:'random',
   gbs:(o,h)=>{const b=rateC(kk(o),'bytes_per_s',h); if(b!=null)return b/1e9; const r=rateC(kk(o),'ops_per_s',h); return r!=null?r*32/1e9:null;}});};
 cat('read','flw.ps','/h2',1/32,'L1 hit, 32 B vector loads','L1 hits');
 cat('read','l1fill/stride32','',1,'own scratchpad, 32 B loads through the L1',null);
 cat('read','tload/scp','',1,'own scratchpad, tensor load','own scratchpad');
 [1,2,3,4,5,6,8].forEach(d=>cat('read',`wire/hop${d}`,'',1,`a scratchpad ${d} hop${d>1?'s':''} away, tensor load`,null));
 cat('read','dramrow/stride8K','',1,'L3, tensor load through the mesh','L3');
 cat('read','tload/dram','',1,'DRAM, tensor load','DRAM');
 cat('write','fsw.ps','/h2',1/32,'L1 hit, 32 B vector stores',null);
 cat('write','tstore/scp','',1,'own scratchpad, tensor store',null);
 cat('write','tstore/dram','',1,'DRAM, tensor store',null);
 cat('write','st_stream/dram','',1,'DRAM, stores through the L1','stores through the L1');
 D.comm.rows.filter(r=>!r.ring.endsWith('c4')&&rg[r.ring]).forEach(r=>{const m=MH[r.ring];
   P.push({fam:'msg',key:r.ring,label:`ring: ${r.ring}${m&&m.mean?` (${f1(m.mean)} mesh hops on average)`:''}, 1 KB messages`,short:null,e:(o,h)=>pcv(rg[r.ring],h),op:()=>'its own data',gbs:()=>r.gb_s,rcard:RCARD});});
 [['dram','through DRAM'],['hop','to the next shire'],['scp','in its own scratchpad']].forEach(([m,t])=>{if(rr[m])P.push({fam:'relay',key:'relay-'+m,label:`the relay, intermediate ${t}`,short:m==='scp'?null:'relay '+t.replace('the ',''),e:(o,h)=>pcv(rr[m],h),op:()=>'one constant per slab',gbs:()=>rp[m].bytes_per_s/1e9,rcard:YCARD});});
 const st={o:'random',X:10,on:Object.keys(FAM),card:'pooled'};
 const has=p=>p.e(st.o,st.card)!=null&&p.gbs(st.o,st.card)!=null;   /* a card without a value draws no point */
 const LABEL_ORDER=['DRAM','own scratchpad','L1 hits','relay through DRAM','relay to next shire','stores through the L1','L3'], NARROW=LABEL_ORDER.slice(0,5);
 CK.seg('map-data',{label:'data',options:[['random','random'],['zeros','zeros']],value:'random',onChange:v=>{st.o=v; fr.redraw(); read();}});
 CK.cardSeg('map-card',{cards:CARDLIST,pooled:true,label:'card',onChange:v=>{st.card=v; fr.redraw(); read();}});
 CK.range('map-watts',{label:'power over idle you can spend',stops:[1,2,3,5,7,10,15,20,30],value:10,fmt:v=>v+' W',onInput:v=>{st.X=v; fr.redraw(); read();}});
 CK.legend('map-legend',Object.keys(FAM).map(k=>({key:k,label:FAM[k][0],mark:'dot',color:FAM[k][1]})),{toggle:true,onChange:on=>{st.on=on; CK.showSeries(fr,on);}});
 const W_=(p,o)=>p.e(o).mean*p.gbs(o)/1000;
 const tipH=p=>()=>{const o=st.o, h=st.card, c=p.e(o,h), gb=p.gbs(o,h); if(!c)return p.label; const pc=h==='pooled'; if(!pc&&c.lo==null)return p.label;
   return `<b>${p.label}</b>, ${p.op(o)}${pc?'':`, on ${cname(h)}`}<br>${fs(c.mean)} pJ/B ${barOf(c,fs)} at ${nf(gb)} GB/s${p.rcard&&p.rcard!==h?` (${p.rcard}'s bandwidth)`:''}<br>${f1(c.mean*gb/1000)} W over idle<br>`+
    (pc?pcs(c,fs).replace(/<br>/g,' · '):c.sebar?'± its pass-to-pass standard error':c.nobar?'':c.n!=null?`the range over its ${WORD[c.n]||c.n} passes`:'');};
 const fr=CK.frame('bytemap',{height:W=>W<600?440:Math.round(Math.min(480,Math.max(360,W*0.6))),label:'Energy per byte against aggregate bandwidth, every path',draw:f=>{
  const L=44,Rr=14,T=24,B=40, x=CK.log(10,40000,L,f.W-Rr), y=CK.log(0.3,500,f.H-B,T), o=st.o;
  CK.axes(f,{x,y,L,R:Rr,T,B,xl:'aggregate bandwidth, GB/s (log)',yl:'pJ per byte, above idle (log)'});
  const clipId='mapclip'; const cp=CK.el('clipPath',{id:clipId},CK.el('defs',{},f.svg)); CK.el('rect',{x:L,y:T,width:f.W-Rr-L,height:f.H-B-T},cp);
  const dg=CK.el('g',{'clip-path':`url(#${clipId})`,'aria-hidden':'true'},f.svg);
  const boxes=[], dlab=[];
  const diag=(w,cls,sw,strong)=>{const a=[10,w*1000/10],b=[40000,w*1000/40000]; CK.el('line',{x1:x(a[0]),y1:y(a[1]),x2:x(b[0]),y2:y(b[1]),stroke:cls,'stroke-width':sw},dg);
   /* label just inside where the line leaves the plot at the bottom or the right */
   const gb=Math.min(40000,w*1000/0.3), pj=w*1000/gb, lx=Math.min(x(gb),f.W-Rr)-3, ly=Math.min(f.H-B-4,Math.max(T+10,y(pj)-4)), tw=(w+' W').length*6.4+4;
   dlab.push([lx,ly,w+' W',strong]); boxes.push([lx-tw,ly-11,lx,ly+3]);};
  [1,3,10,30].forEach(w=>{if(w!==st.X)diag(w,'var(--axis)',1,false);});
  diag(st.X,'var(--ink)',1.6,true);
  dlab.forEach(d=>CK.txt(f.svg,d[0],d[1],d[2],d[3]?'lab-strong':'tick','end').classList.add('halo'));
  const layer=CK.el('g',{},f.svg), groups={}, labs=[];
  const h=st.card, hops=P.filter(p=>/^wire\//.test(p.key)&&has(p)); if(hops.length){const pts=hops.map(p=>[p.gbs(o,h),p.e(o,h).mean]);
   CK.el('path',{d:CK.path(pts,x,y),fill:'none',stroke:'var(--c1)','stroke-width':1,opacity:0.6,'data-series':'read'},layer);}
  P.filter(has).forEach(p=>{const c=p.e(o,h), gb=p.gbs(o,h), cx=x(gb), cy=y(c.mean), col=FAM[p.fam][1];
   const gg=CK.el('g',{'data-series':p.fam},layer);
   CK.el('line',{x1:cx,x2:cx,y1:y(c.hi),y2:y(c.lo),stroke:col,'stroke-width':1.5},gg);
   const m=mark(f,gg,'circle',{cx,cy,r:4.5,fill:col,stroke:'var(--surface)','stroke-width':1.5},9,tipH(p));
   (groups[p.fam]=groups[p.fam]||[]).push([gb,m]); boxes.push([cx-4,cy-4,cx+4,cy+4]);
   if(p.short&&(!f.narrow||NARROW.includes(p.short)))labs.push({x:cx,y:cy,text:p.short,series:p.fam,rank:LABEL_ORDER.indexOf(p.short)});});
  const h1=hops[0]; if(h1&&!f.narrow)labs.push({x:x(h1.gbs(o,h)),y:y(h1.e(o,h).mean),text:'1–8 hops away',series:'read',rank:50});
  const rg1=P.find(p=>p.key==='xshire4'&&has(p)); if(rg1)labs.push({x:x(rg1.gbs()),y:y(rg1.e(o,h).mean),text:'rings between shires',series:'msg',rank:60});
  const rg0=P.find(p=>p.key==='pair'&&has(p)); if(rg0&&!f.narrow)labs.push({x:x(rg0.gbs()),y:y(rg0.e(o,h).mean),text:'pair',series:'msg',rank:70});
  placeLabels(layer,labs.sort((a,b)=>a.rank-b.rank),boxes,[L,T,f.W-Rr,f.H-B]);
  Object.keys(groups).forEach(k=>CK.keynav(f,groups[k].sort((a,b)=>a[0]-b[0]).map(z=>z[1])));
 }});
 CK.showSeries(fr,st.on);
 const KEYS=[['tload/dram','DRAM tensor loads'],['tload/scp','the own scratchpad'],['wire/hop6','a scratchpad 6 hops away'],['relay-hop','the relay to the next shire'],['flw.ps','L1 hits']];
 const bw=v=>v>=1000?f1(v/1000)+' TB/s':nf(v)+' GB/s';
 const ro=CK.readout('map-readout');
 function read(){const o=st.o, h=st.card;
  ro.set(`Within <b>${st.X} W</b> over idle, ${o==='zeros'?'on zeros':'on random data'}${h==='pooled'?'':`, on ${cname(h)}`}: `+KEYS.map(([k,l])=>{const p=P.find(q=>q.key===k); if(!p||!has(p))return ''; const gb=p.gbs(o,h), cap=st.X*1000/p.e(o,h).mean;
   return cap>=gb?`${l} all of its ${bw(gb)}`:`${l} ${bw(cap)} of its ${bw(gb)}`;}).filter(Boolean).join('; ')+'.');}
 read();
 const pd=P.find(p=>p.key==='tload/dram'), ps=P.find(p=>p.key==='tload/scp'), prd=P.find(p=>p.key==='relay-dram'), prh=P.find(p=>p.key==='relay-hop');
 const rings=P.filter(p=>p.fam==='msg').map(p=>W_(p,'random'));
 $('mapcap').innerHTML=(pd&&ps?`<b>DRAM (${f0(pd.e('random').mean)} pJ/B at ${f0(pd.gbs('random'))} GB/s, ${f1(W_(pd,'random'))} W) and the shire's own scratchpad (${f1(ps.e('random').mean)} pJ/B at ${nf(ps.gbs('random'))} GB/s, ${f1(W_(ps,'random'))} W) sit on the same 10 W diagonal, ${f0(ps.gbs('random')/pd.gbs('random'))}× apart in bandwidth</b> (random data). `:'')+
  (prd&&prh?`The relay through DRAM (${f1(prd.e().mean)} pJ/B at ${f0(prd.gbs())} GB/s) and to the next shire (${f1(prh.e().mean)} pJ/B at ${nf(prh.gbs())} GB/s) both draw about ${f0((W_(prd)+W_(prh))/2)} W while the kernel runs${rp.dram&&rp.hop?` (${f1(Math.min(rp.dram.over_idle_w,rp.hop.over_idle_w))}–${f1(Math.max(rp.dram.over_idle_w,rp.hop.over_idle_w))} W averaged over the burst, <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay">Hand it to the next shire</a> §2)`:''}, and the second moves ${f0(prh.gbs()/prd.gbs())}× the bytes. `:'')+
  (rings.length?`The rings between cores draw ${f1(Math.min(...rings))}–${f1(Math.max(...rings))} W. `:'')+
  `Diagonals: constant power over idle, pJ/B × GB/s; the slider picks one. Whiskers: the range over every pass on ${ALLC}; pick a card to see its own means, whiskers (the range over its passes, or ± its standard error for the rings and the relay) and bandwidths, the rings' and the relay's bandwidths being ${andList([...new Set([RCARD,YCARD].filter(Boolean))])}'s in every view. The L1 rows' bandwidth is their instruction rate times 32 B; the relay counts each byte it reads and each it writes. Reads and writes switch between zeros and random data; the rings and the relay carry their own data. The numbers are in the tables of sections 4.1, 4.3 and 5.`;
})();

/* ---------- 4.1 / 4.2 memory tables ---------- */
(function(){
 const paths=[['flw.ps/zeros/h2','flw.ps/random/h2',1/32,'L1 hit, flw.ps','read'],['fsw.ps/zeros/h2','fsw.ps/random/h2',1/32,'L1 hit, fsw.ps','write'],
   ['tload/scp/zeros','tload/scp/random',1,'own scratchpad, tensor load','read'],['tstore/scp/zeros','tstore/scp/random',1,'own scratchpad, tensor store','write'],
   ['tload/dram/zeros','tload/dram/random',1,'DRAM, tensor load','read'],['tstore/dram/zeros','tstore/dram/random',1,'DRAM, tensor store','write'],['st_stream/dram/zeros','st_stream/dram/random',1,'DRAM, stores through the L1','write']];
 if(!cb(paths[0][1])){return;}
 $('memcap').textContent='Tensor loads skip the L1 (the L2 and L3 cache them when the working set fits); tensor stores skip the L1 and the L2; the L1 rows are hits in a 256 B buffer, and their GB/s is the instruction rate times 32 B; the last row is a plain vector store to DRAM through the L1.';
 $('memtab').innerHTML='<thead><tr><th>Path</th><th class="num">zeros pJ/B</th><th class="num">random pJ/B</th><th class="num">random / zeros</th><th class="num">GB/s</th><th class="num" data-nosort>per card, random</th></tr></thead><tbody>'+
  paths.map(p=>{const z=cb(p[0],p[2]),r=cb(p[1],p[2]); if(!(z&&r))return ''; const s2=S2[p[1]], bps=!s2?0:s2.bytes_per_s.mean>0?s2.bytes_per_s.mean:p[2]<1?s2.ops_per_s.mean/p[2]:0;
   return `<tr><td>${p[3]} <span class="small">(${p[4]})</span></td><td class="num">${bt(z,fs)}</td><td class="num">${bt(r,fs)}</td><td class="num">${f2(r.mean/z.mean)}×</td><td class="num">${bps?nf(bps/1e9):'—'}</td><td class="num small">${pcs(r,fs)}</td></tr>`;}).join('')+'</tbody>';
 const dl=cb('tload/dram/random'),sl=cb('tload/scp/random'),ds=cb('tstore/dram/random'),ss=cb('st_stream/dram/random'),dz=cb('tload/dram/zeros');
 const oS=offRail('st_stream/dram/random'), oT=offRail('tstore/dram/random');
 /* the DRAM write against the read, per card; and the version-3 check's own test of it (V3-CAT, CAT-e: its 99% interval) */
 const wrh=CK.cardsIn(ds.per_card).filter(h=>dl.per_card[h]), wr=wrh.map(h=>100*(ds.per_card[h].mean/dl.per_card[h].mean-1));
 const WR=(V3.catalogue||{}).dram_write_read||{}, wrc=CK.cardsIn(WR), wr0=wrc.filter(h=>WR[h].lo<=0&&WR[h].hi>=0);
 $('memtext').innerHTML=
  `<b>DRAM is ${f0(dl.mean/sl.mean)}× the shire's own scratchpad per byte read.</b> A DRAM write by tensor store costs about what a read costs (${f0(ds.mean)} against ${f0(dl.mean)} pJ/B${wr.length?`; ${andList(wrh.map((h,i)=>`${f0(wr[i])}% more on ${cname(h)}`))}`:''})${wrc.length?`, and the version-3 check, a separate run of these rows, did not resolve the difference from zero on ${wr0.length===wrc.length?'any card':andList(wr0.map(cname))} (${semiList(wrc.map(h=>`${cname(h)} ${sg1(WR[h].diff)} pJ/B [${sg1(WR[h].lo)}, ${sg1(WR[h].hi)}]`))}, 99% intervals)`:''}; `+
  `<b>the same bytes written through the L1 cost ${f1(ss.mean/ds.mean)}× more</b> and arrive at a third of the bandwidth, consistent with each store allocating its line, so that the line is read from DRAM before it is written back and the byte pays for a read and a write. `+
  (oS&&oT?`Off-rail it costs ${f0(oS)} pJ against a tensor store's ${f0(oT)} (<a href="${HUB}#the-unmetered-remainder-attributed">Limits of observability, §4.2</a>), and a tensor load plus a tensor store come to ${f0(dl.mean+ds.mean)} of its ${f0(ss.mean)} pJ/B. `:'')+
  `<b>Even DRAM is data-dependent</b>: zeros ${f0(dz.mean)} [${f0(dz.lo)}–${f0(dz.hi)}], random ${f0(dl.mean)} [${f0(dl.lo)}–${f0(dl.hi)}] pJ/B; the scratchpad doubles. A scratchpad write is twice a scratchpad read.`;
 const lv=RR.levels_pj_per_byte, LB=RR.levels_by_contents_pj_per_byte||{};
 if(lv&&lv.dram){
  const LV=[['l1','L1 hits','256 B per hart, 2,048 harts'],['l2','L2','256 KB per shire (L2 is 512 KB)'],['l3','L3','768 KB per shire, 24 MB in all (L3 is 32 MB)'],['dram','DRAM','256 MB in all'],['scp-local','own scratchpad','2 MB of the shire’s own L2 scratchpad'],['scp-remote','remote scratchpad',`2 MB of the scratchpad 16 shire IDs away (${MH.xshire16?f1(MH.xshire16.mean):'about 2'} mesh hops on average)`]];
  /* the scratchpad levels are prefilled in the version-3 passes (zeros on odd passes, random data on even ones): one row per contents */
  const BYC=new Set(['scp-local','scp-remote']), CT=[['zeros','zeros'],['random','random data']];
  const l1c=cb('flw.ps/random/h2',1/32), gh=D.memory_reads.rows.map(r=>r.implied_ghz).filter(v=>v!=null);
  /* the level's L1 loop against the catalogue's L1 row, per card */
  const l1pc=l1c&&lv.l1?CK.cardsIn(lv.l1.per_card).filter(h=>l1c.per_card[h]).map(h=>[h,f0(100*(lv.l1.per_card[h].mean/l1c.per_card[h].mean-1)),f2(l1c.per_card[h].mean)]):[];
  /* The two L1 loops: memhier.c's (8 flw.ps per loop iteration; minion-cycles per load from its 18 September row, B per cycle being
     clock-independent in the minion's domain, and the 23 September reruns reproduce it) and the catalogue's (enercat.c's RUN
     macro, 64 per iteration; every card's issue rate). */
  const mh1=D.memory_reads.rows.find(r=>r.level==='l1'), cycMH=mh1&&mh1.implied_ghz?32/(mh1.gb_s/(mh1.implied_ghz*1024)):null,
   fl2=CARDS.map(h=>SUMM(h)['flw.ps/random/h2']).filter(Boolean), cycCat=fl2.length?1/(2*fl2.reduce((a,e)=>a+e.ops_per_cycle_per_hart.mean,0)/fl2.length):null,
   tbsCat=SA['flw.ps/random/h2']?SA['flw.ps/random/h2'].ops_per_s.mean*32/1e12:null;
  $('memold').innerHTML='<thead><tr><th>Level</th><th>Working set</th><th class="num">pJ/B</th><th class="num">per card</th></tr></thead><tbody>'+
   LV.map(r=>{if(!lv[r[0]])return ''; if(BYC.has(r[0])&&CT.every(([o])=>LB[o]&&LB[o][r[0]]))
     return CT.map(([o,ol])=>`<tr><td>${r[1]}, ${ol}</td><td class="small">${r[2]}, prefilled with ${ol}</td><td class="num">${bt(LB[o][r[0]],fs)}</td><td class="num small">${pcs(LB[o][r[0]],fs)}</td></tr>`).join('');
    return `<tr><td>${r[1]}</td><td class="small">${r[2]}</td><td class="num">${bt(lv[r[0]],fs)}</td><td class="num small">${pcs(lv[r[0]],fs)}</td></tr>`;}).join('')+'</tbody>';
  const PP=(RR.passes_per_card||{}).levels||{}, pph=CK.cardsIn(PP), npp=[...new Set(pph.map(h=>PP[h].length))];
  const RLo=(V3.rl||{}), SBC=RLo.scp_by_contents||{};
  const band=(h,o)=>SBC[h]&&SBC[h][o]?SBC[h][o].mean:null, inb=h=>band(h,'zeros')>=1.7&&band(h,'zeros')<=2.3&&band(h,'random')>=3.7&&band(h,'random')<=4.7;
  const sin=CK.cardsIn(SBC).filter(inb), sout=CK.cardsIn(SBC).filter(h=>!inb(h));
  const l2=lv.l2, l3=lv.l3, rspan=c=>c?`${fs(c.lo)}–${fs(c.hi)}`:'—';
  $('memoldnote').innerHTML=`L1: both harts of every minion re-reading a private 256 B buffer with 32 B vector loads, in the memory-hierarchy probe's own loop (contents not set). It issued a load every ${cycMH?f1(cycMH):'3'} minion-cycles against the catalogue's ${cycCat?f1(cycCat):'1.4'}, and reads ${l1pc.length?`${f0(Math.min(...l1pc.map(x=>+x[1])))}–${f0(Math.max(...l1pc.map(x=>+x[1])))}% above section 4.1's L1 row (${andList(l1pc.map(x=>x[2]))} pJ/B on random data on ${andList(l1pc.map(x=>cname(x[0])))})`:`${l1c&&lv.l1?f0(100*(lv.l1.mean/l1c.mean-1))+'%':'well'} above section 4.1's L1 row (${l1c?f2(l1c.mean):'—'} pJ/B on random data)`}, which is the figure to use. Other levels: hart 0 of every minion streaming 1 KB tensor loads (they skip the L1) over a working set sized to the level. The L2, L3 and DRAM buffers' contents are not set, so those rows do not match section 4.1's zeros and random columns (DRAM is within noise of the random row), and the L2 and L3 move a lot between passes (${rspan(l2)} and ${rspan(l3)} pJ/B). The version-3 passes fill the scratchpads with zeros or random data, and the own scratchpad follows the fill: ${sin.length?`inside the registered bands (1.7–2.3 and 3.7–4.7 pJ/B) on ${andList(sin.map(cname))}${sout.length?`, above them on ${andList(sout.map(h=>`${cname(h)} (${f2(band(h,'zeros'))} and ${f2(band(h,'random'))})`))}`:''}; `:''}no pair of cards differs on the L1 or the own scratchpad (99%). ${pph.length?`${(w=>w[0].toUpperCase()+w.slice(1))(String(npp.length===1?(WORD[npp[0]]||npp[0]):'Several'))} passes on each of ${WORD[pph.length]||pph.length} cards`:'Passes'} at 600 MHz (n = ${lv.dram.n}; 26 September), replacing 23 September's unfilled passes and the 18 September run (<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy">Memory hierarchy</a>), whose clock the governor moved (${gh.length?f2(Math.min(...gh))+'–'+f2(Math.max(...gh)):'0.6–0.7'} GHz).`;
 }
})();

/* ---------- 4.3 finer grain: wires, lines, rows, neighbourhoods ---------- */
(function(){
 const C=D.catalogue, S=SA;
 const Wf=C.cards[CARDS[0]].wire, Wf2=CARDS[1]&&C.cards[CARDS[1]].wire;
 /* every card after the first, drawn hollow in its registry shape (ring, diamond) and the operand's colour */
 const WO=CARDS.slice(1).map(h=>({h,w:C.cards[h].wire})).filter(o=>o.w);
 const hollow=(g,h,cx,cy,r,col)=>{const m=CK.card(h).mark, a={fill:'none',stroke:col,'stroke-width':1.5}, k=r*1.3;
  return CK.el(m==='diamond'?'polygon':m==='box'?'rect':'circle',Object.assign(m==='diamond'?{points:`${cx},${cy-k} ${cx+k},${cy} ${cx},${cy+k} ${cx-k},${cy}`}:m==='box'?{x:cx-r,y:cy-r,width:2*r,height:2*r}:{cx,cy,r},a),g);};
 if(Wf&&Wf.random&&Wf.zeros){
  const st={upto:8}, fitOf=(wf,upto)=>lfit(wf.points.filter(p=>p.hops>=1&&p.hops<=upto).map(p=>[p.hops,p.pj_per_byte]));
  const mxh=Math.max(...Wf.random.points.map(p=>p.hops)), shr=d=>(Wf.random.points.find(p=>p.hops===d)||{}).shires, full=Wf.random.points.filter(p=>p.shires===32).map(p=>p.hops);
  CK.seg('wire-fit',{label:'straight-line fit',options:[['8','over 1–'+mxh+' hops'],['6','over 1–6 hops']],value:'8',onChange:v=>{st.upto=+v; fw.redraw(); wread();}});
  const wireItems=[{key:'z',label:'zeros',mark:'dot',color:'var(--c3)'},{key:'r',label:'random data',mark:'dot',color:'var(--c2)'},...WO.map(o=>cardItem(o.h,cname(o.h)+' (hollow)','var(--ink-2)')),{key:'f',label:'fit, '+CARDS[0],mark:'dash',color:'var(--ink-2)'}]; CK.legend('wire-legend',wireItems); legendMarks('wire-legend',wireItems);
  const mxy=Math.max(...Wf.random.points.map(p=>(CB[`wire/hop${p.hops}/random`]||{hi:p.pj_per_byte}).hi))*1.08;
  const fw=CK.frame('wire',{height:W=>W<600?270:320,label:'Energy per byte against mesh distance',draw:f=>{
   const L=40,Rr=12,T=24,B=40, x=CK.lin(-0.4,mxh+0.5,L,f.W-Rr), y=CK.lin(0,mxy,f.H-B,T);
   CK.axes(f,{x,y,L,R:Rr,T,B,xt:[0,1,2,3,4,5,6,7,8].filter(v=>v<=mxh),xl:f.narrow?'mesh hops to the scratchpad read (0: its own)':'hops across the mesh to the scratchpad read (0: the shire’s own)',yl:'pJ per byte'});
   const dx=f.narrow?3:4, groups=[];
   [['zeros','var(--c3)'],['random','var(--c2)']].forEach(([o,col])=>{const wf=Wf[o], ft=fitOf(wf,st.upto);
    CK.el('line',{x1:x(0),x2:x(mxh),y1:y(ft.a),y2:y(ft.a+ft.b*mxh),stroke:col,'stroke-width':1.5,'stroke-dasharray':'5 4'},f.svg);
    const nodes=[];
    if(wf.local_pj_per_byte!=null){const l2=WO.map(w=>[w.h,w.w[o]&&w.w[o].local_pj_per_byte]).filter(z=>z[1]!=null);
     nodes.push(mark(f,f.svg,'circle',{cx:x(0)-dx/2,cy:y(wf.local_pj_per_byte),r:4,fill:col},8,`the shire's own scratchpad, ${o}: <b>${f2(wf.local_pj_per_byte)} pJ/B</b> on ${CARDS[0]}${l2.map(z=>`, ${f2(z[1])} on ${cname(z[0])}`).join('')}`));}
    wf.points.forEach(p=>{const c=CB[`wire/hop${p.hops}/${o}`], p3=WO.map((w,j)=>[w.h,w.w[o]&&w.w[o].points.find(q=>q.hops===p.hops),j]).filter(z=>z[1]);
     if(c)CK.el('line',{x1:x(p.hops),x2:x(p.hops),y1:y(c.hi),y2:y(c.lo),stroke:col,'stroke-width':1.5},f.svg);
     p3.forEach(([h,q,j])=>hollow(f.svg,h,x(p.hops)+dx*(1+j),y(q.pj_per_byte),3.5,col));
     nodes.push(mark(f,f.svg,'circle',{cx:x(p.hops)-dx/2,cy:y(p.pj_per_byte),r:4,fill:col},9,`${p.hops} hop${p.hops>1?'s':''}, ${o}: <b>${f2(p.pj_per_byte)} ± ${f2(p.se)} pJ/B</b> on ${CARDS[0]}${p3.map(([h,q])=>`, ${f2(q.pj_per_byte)} ± ${f2(q.se)} on ${cname(h)}`).join('')}${c?`<br>${ALLC}: ${f2(c.mean)} [${f2(c.lo)}–${f2(c.hi)}], n = ${c.n}`:''}<br>${p.shires} shires reading`));});
    groups.push(nodes);});
   groups.forEach(n=>CK.keynav(f,n));
  }});
  const ro=CK.readout('wire-readout');
  /* the fits per card; with more than two cards every card after the first is listed */
  function wread(){const u=st.upto, s=(wf,o)=>wf&&wf[o]?fitOf(wf[o],u):null; if(WO.length>1){const W_=[[CARDS[0],Wf]].concat(WO.map(w=>[w.h,w.w])).filter(z=>z[1].random&&z[1].zeros);
    ro.set(`Fit over 1–${u===8?mxh:6} hops: <b>random</b> ${andList(W_.map(([h,w])=>`${f2(s(w,'random').b)} (${cname(h)})`))} pJ/B per hop, intercept ${andList(W_.map(([h,w])=>f2(s(w,'random').a)))}; <b>zeros</b> ${andList(W_.map(([h,w])=>f2(s(w,'zeros').b)))} per hop.`); return;}
   ro.set(`Fit over 1–${u===8?mxh:6} hops: <b>random ${f2(s(Wf,'random').b)}</b> (${CARDS[0]})${Wf2?` and ${f2(s(Wf2,'random').b)} (${CARDS[1]})`:''} pJ/B per hop, intercept ${f2(s(Wf,'random').a)}${Wf2?` and ${f2(s(Wf2,'random').a)}`:''}; <b>zeros ${f2(s(Wf,'zeros').b)}</b>${Wf2?` and ${f2(s(Wf2,'zeros').b)}`:''} per hop.`);}
  wread();
  $('wirecap').textContent=`1 KB tensor loads from a scratchpad exactly d hops away, all 32 shires reading up to ${Math.max(...full)} hops (${shr(6)} at 6 hops, ${shr(8)} at 8, so the 8-hop point has half the traffic), at most two readers per target; d = 0 is the shire's own scratchpad. Filled: ${CARDS[0]}; hollow: ${andList(WO.map(o=>cname(o.h)))}; whiskers: the range over ${ALLC}' passes. Dashed: the straight-line fit over the hops chosen above.`;
  const dz=Wf.zeros.slope_pj_per_byte_per_hop, dr=Wf.random.slope_pj_per_byte_per_hop;
  /* the slopes per card: over 1–8 hops (analyze_catalogue's wire fit) and over 1–6 */
  const WA=[[CARDS[0],Wf]].concat(WO.map(o=>[o.h,o.w])).filter(z=>z[1]&&z[1].random&&z[1].zeros);
  const r8=WA.map(([h,w])=>w.random.slope_pj_per_byte_per_hop), r6=WA.map(([h,w])=>fitOf(w.random,6).b), z8=WA.map(([h,w])=>w.zeros.slope_pj_per_byte_per_hop), z6s=WA.map(([h,w])=>fitOf(w.zeros,6).b), zall=z8.concat(z6s);
  $('wiretext').innerHTML=`<b>One mesh hop costs about 2 pJ per byte on random data</b> (${andList(WA.map(([h],i)=>`${f2(r8[i])} on ${cname(h)}`))} fitted over 1–${mxh} hops; ${f2(Math.min(...r6))}–${f2(Math.max(...r6))} over 1–6, leaving out d = ${mxh}, which only ${shr(mxh)} shires reach and which sits level with d = 6) `+
   `<b>and ${f1(Math.min(...zall))}–${f1(Math.max(...zall))} on zeros</b> (${f2(Math.min(...z8))}–${f2(Math.max(...z8))} over 1–${mxh} hops, ${f2(Math.min(...z6s))}–${f2(Math.max(...z6s))} over 1–6). `+
   (()=>{/* EN-1: over 1-6 hops the step out of the shire is about one hop; only the 1-8 fit, which the half-traffic 8-hop point pulls down, makes it two */
    const st6=WA.map(([h,w])=>{const q=fitOf(w.random,6); return (q.a-(w.random.local_pj_per_byte||0))/q.b;}), st8=WA.map(([h,w])=>(w.random.intercept_pj_per_byte-(w.random.local_pj_per_byte||0))/w.random.slope_pj_per_byte_per_hop);
    return `<b>Leaving the shire costs about one more hop</b>: over 1–6 hops the intercept is ${andList(WA.map(([h,w])=>f2(fitOf(w.random,6).a)))} pJ/B on random data (${andList(WA.map(([h])=>cname(h)))}) against ${andList(WA.map(([h,w])=>f2(w.random.local_pj_per_byte||0)))} for the shire's own scratchpad, ${f1(Math.min(...st6))}–${f1(Math.max(...st6))} hops' worth; the 1–${mxh}-hop fit, which the half-traffic ${mxh}-hop point pulls down, puts it at ${f1(Math.min(...st8))}–${f1(Math.max(...st8))}. `;})()+
   /* Heat per millimetre's own figure (manual.json wire_ref, from its report.json): the third run, three cards, loaded mesh */
   (()=>{const WR=D.wire_ref||{}, lb=WR['loaded/board'], ln=WR['loaded/noc_rail'];
    return `For wires, use <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm">Heat per millimetre</a>`+(lb?`: ${f2(lb.pj_per_byte_hop)} pJ/B per hop on board power${ln?` (${f2(ln.pj_per_byte_hop)} on the mesh rail)`:''} for random data on a loaded mesh, split into bits that differ between flits, ones carried and a fixed part.`:', which splits a hop into bits that differ between flits, ones carried and a fixed part.');})();
 }
 /* ---- lines ---- */
 const fz=S['l1fill/stride32/zeros'],fr=S['l1fill/stride32/random'],gz=S['l1fill/stride64/zeros'],gr=S['l1fill/stride64/random'];
 if(fz&&fr&&gz&&gr){
  $('linetab').innerHTML='<thead><tr><th>32 B loads through the L1 from the shire’s scratchpad</th><th class="num">fills per load</th><th class="num">zeros pJ per load</th><th class="num">random pJ per load</th></tr></thead><tbody>'+
   [['32','0.5','l1fill/stride32'],['64','1','l1fill/stride64'],['128','1','l1fill/stride128']].map(r=>{const z=cb(r[2]+'/zeros',32),x=cb(r[2]+'/random',32);return z&&x?`<tr><td>stride ${r[0]} B</td><td class="num">${r[1]}</td><td class="num">${bt(z,f1)}</td><td class="num">${bt(x,f1)}</td></tr>`:'';}).join('')+
   '<tr><td colspan="4"><b>64 B tensor loads from the scratchpad, by stride</b></td></tr>'+
   ['64','128','256'].map(st=>{const z=cb(`scpline/stride${st}/zeros`,64),r=cb(`scpline/stride${st}/random`,64),rs=S[`scpline/stride${st}/random`]; return z&&r?`<tr><td>stride ${st} B (${st==='64'?'cycles the banks':st==='128'?'alternates two banks':'the same bank every time'})</td><td class="num">—</td><td class="num">${bt(z,f1)} per 64 B</td><td class="num">${bt(r,f1)} per 64 B, ${nf(rs.bytes_per_s.mean/1e9)} GB/s</td></tr>`:'';}).join('')+'</tbody>';
  const c32z=cb('l1fill/stride32/zeros',32),c64z=cb('l1fill/stride64/zeros',32),c32r=cb('l1fill/stride32/random',32),c64r=cb('l1fill/stride64/random',32);
  const fillz=2*(c64z.mean-c32z.mean), fillr=2*(c64r.mean-c32r.mean);
  const per=h=>2*((c64r.per_card[h]||{mean:0}).mean-(c32r.per_card[h]||{mean:0}).mean);
  const tlz=cb('tload/scp/zeros'), tlr=cb('tload/scp/random');
  /* the fill against a tensor load, per byte, per card and operand set: the pooled 75% hides 71-86% and an aifoundry2 interval that reaches 1 */
  const c32zr=[c32z,c32r], c64zr=[c64z,c64r], tlzr=[tlz,tlr];
  const frs=CARDLIST.flatMap(h=>[0,1].filter(i=>c64zr[i].per_card[h]&&c32zr[i].per_card[h]&&tlzr[i].per_card[h]).map(i=>2*(c64zr[i].per_card[h].mean-c32zr[i].per_card[h].mean)/64/tlzr[i].per_card[h].mean));
  /* the version-3 check's own test of the fill against a tensor load, random data (V3-CAT, CAT-f: the ratio and its ~99% interval) */
  const FV=(V3.catalogue||{}).fill_vs_tload||{}, fvh=CK.cardsIn(FV), fvy=fvh.filter(h=>FV[h].decision==='holds'), fvn=fvh.filter(h=>FV[h].decision!=='holds');
  const bwc=CARDLIST.map(h=>[SUMM(h)['scpline/stride64/random'],SUMM(h)['scpline/stride256/random']]).filter(z=>z[0]&&z[1]), bwSame=bwc.length&&bwc.every(z=>Math.abs(z[1].bytes_per_s.mean/z[0].bytes_per_s.mean-bwc[0][1].bytes_per_s.mean/bwc[0][0].bytes_per_s.mean)<0.02);
  const fr5=frs.length?[Math.round(20*Math.min(...frs))*5,Math.round(20*Math.max(...frs))*5]:[75,75];
  const bwOf=st=>S[`scpline/stride${st}/random`]?S[`scpline/stride${st}/random`].bytes_per_s.mean/1e9:null, bw64=bwOf(64), bw256=bwOf(256);
  $('linetext').innerHTML=`Twice the difference between the stride-64 and stride-32 rows is what filling one 64 B line from the scratchpad into the L1 costs: <b>${fillz.toFixed(0)} pJ on zeros, ${fillr.toFixed(0)} pJ on random data</b> (${CK.cardsIn(c64r.per_card).map(h=>cshort(h)+' '+per(h).toFixed(0)).join(', ')} on random data) — ${f1(fillz/64)} and ${f1(fillr/64)} pJ per byte of line, roughly ${fr5[0]}–${fr5[1]}% of the ${f1(tlz.mean)} and ${f1(tlr.mean)} pJ/B a tensor load pays for the same bytes from the same scratchpad on the ${WORD[CARDLIST.length]||CARDLIST.length} cards`+
   (fvh.length?` (the version-3 check, a separate run, resolved the fill below the tensor load on random data on ${andList(fvy.map(h=>`${cname(h)} (${f2(FV[h].ratio)} [${f2(FV[h].ci99[0])}, ${f2(FV[h].ci99[1])}])`))}${fvn.length?`, but not on ${andList(fvn.map(h=>`${cname(h)} (${f2(FV[h].ratio)} [${f2(FV[h].ci99[0])}, ${f2(FV[h].ci99[1])}])`))}, where it is not separable from equal`:''})`:'')+`. What random data adds over zeros is about ${(fillr-fillz).toFixed(0)} pJ for the fill's 512 bits, ${((fillr-fillz)*1000/512).toFixed(0)} fJ per bit on the path from the shire cache into the L1.`+
   (bw64&&bw256?` The 64 B tensor loads by stride show the banks: coming back to the same bank every time cuts the bandwidth by a third (${nf(bw256)} against ${nf(bw64)} GB/s${bwSame?`, on ${bwc.length===CARDLIST.length?'every card':andList(CARDLIST.filter(h=>SUMM(h)['scpline/stride256/random']).map(cname))}`:''}), but what it does to the energy per byte cannot be told apart from the other strides'.`:'');
 }
 /* ---- DRAM rows ---- */
 const rz2=n=>S[`dramrow2/${n}/zeros`], rr2=n=>S[`dramrow2/${n}/random`];
 if(rz2('seq')&&rz2('rowmiss')){
  const PAT=[['seq','sequential: next bank, 32 columns per row visit'],['rowhit','same bank and row, next column, every access'],['rowmiss','a new row on every visit to a bank']];
  $('rowtab').innerHTML='<thead><tr><th>1 KB tensor loads from DRAM, 32 harts with 64 MB each</th><th class="num">zeros pJ/B</th><th class="num">random pJ/B</th><th class="num">GB/s</th></tr></thead><tbody>'+
   PAT.map(r=>{const z=rz2(r[0]),x=rr2(r[0]),cz=cb(`dramrow2/${r[0]}/zeros`),cx=cb(`dramrow2/${r[0]}/random`);return z&&x?`<tr><td>${r[1]}</td><td class="num">${cz?bt(cz,f1):z.pj_per_byte.mean.toFixed(1)+' ± '+z.pj_per_byte.se.toFixed(1)}</td><td class="num">${cx?bt(cx,f1):x.pj_per_byte.mean.toFixed(1)+' ± '+x.pj_per_byte.se.toFixed(1)}</td><td class="num">${(x.bytes_per_s.mean/1e9).toFixed(1)}</td></tr>`:'';}).join('')+
   `</tbody><tfoot><tr><td colspan="4" class="small">${(()=>{const c=cb('dramrow2/seq/random'), nc=c?Object.keys(c.per_card).length:0; return nc>1?`Mean and range over three passes on each of ${WORD[nc]||nc} cards; GB/s: ${CARDS[0]}'s, the same on every card within 1%.`:`Mean and range over three passes on ${CARDS[0]}.`;})()}</td></tr></tfoot>`;
  /* how often each of the 32 harts comes back to its row: one 1 KB access per visit, at the aggregate rate / 32, 600 MHz */
  const gbs=PAT.flatMap(r=>['zeros','random'].map(o=>S[`dramrow2/${r[0]}/${o}`].bytes_per_s.mean)), cyc=gbs.map(v=>1024*32/v*600e6);
  const prem=o=>PAT.map(r=>100*(cb(`dramrow2/${r[0]}/${o}`).mean/cb(`tload/dram/${o}`).mean-1)), pr=prem('random'), pz=prem('zeros');
  const dlg=S['tload/dram/random'].bytes_per_s.mean/1e9, r100=v=>nf(Math.round(v/100)*100);
  const l3=S['dramrow/stride8K/random'], l3z=S['dramrow/stride8K/zeros'], l3b=SB['dramrow/stride8K/random'], l3bz=SB['dramrow/stride8K/zeros'];
  /* 3.87 µs and 2,325 cycles: the refresh interval the memory-anatomy page reads from the controller (PLAN2 D21) */
  /* the version-3 check's test of the rows (V3-CAT, CAT-c): one-way ANOVA over the three patterns, and rows − tensor loads per card */
  const DR=(V3.catalogue||{}).dram_rows||{}, drh=CK.cardsIn(DR), anovaOK=drh.length&&drh.every(h=>['zeros','random'].every(o=>DR[h][o].anova_p>0.01));
  const exR=o=>drh.filter(h=>DR[h][o].rows_minus_tload.lo>0), exN=o=>drh.filter(h=>!(DR[h][o].rows_minus_tload.lo>0));
  $('rowtext').innerHTML=`<b>The row pattern does not change the energy per byte</b>: row hits, row misses and the streaming case agree within their pass-to-pass error on both operand sets${drh.length?`, on ${anovaOK?`every card (the version-3 check: no pattern differs at 99% on ${andList(drh.map(cname))})`:'some cards'}`:''}. `+
   `On aifoundry2 the controller runs an open-page policy: a row stays open until a refresh (every 3.87 µs) or an access to another row of its bank closes it (<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy#how-long-a-row-stays-open">Anatomy of a memory access</a>). `+
   `Each hart here comes back to its row only every ${r100(Math.min(...cyc))}–${r100(Math.max(...cyc))} cycles or so (32 harts at ${f0(Math.min(...gbs)/1e9)}–${f0(Math.max(...gbs)/1e9)} GB/s), with 31 other streams in between, and a refresh falls every 2,325 cycles. `+
   `So either every pattern paid an activation, or an activation is small next to the transfer (one of about 30 pJ/B on zeros, or 50 on random data, would have shown); for a programmer it makes no difference. `+
   `These 32-hart loads cost ${f0(Math.min(...pr))}–${f0(Math.max(...pr))}% more per byte than section 4.1's tensor loads at ${f0(dlg)} GB/s (${f0(Math.min(...pz))}–${f0(Math.max(...pz))}% more on zeros)`+
   (drh.length?`; the version-3 check resolved the premium from zero on zeros on ${exR('zeros').length===drh.length?'every card':andList(exR('zeros').map(cname))} and on random data on ${andList(exR('random').map(cname))}${exN('random').length?`, but not on ${andList(exN('random').map(h=>`${cname(h)} (${sg1(DR[h].random.rows_minus_tload.diff)} pJ/B [${sg1(DR[h].random.rows_minus_tload.lo)}, ${sg1(DR[h].random.rows_minus_tload.hi)}])`))}`:''}`:'')+
   `: use them to compare patterns, and section 4.1 to price DRAM.`+
   (l3&&l3z?(()=>{const L3=CARDS.map(h=>[h,SUMM(h)['dramrow/stride8K/zeros'],SUMM(h)['dramrow/stride8K/random']]).filter(z=>z[1]&&z[2]);
     return ` An earlier version of this experiment with all 1,024 minions and only 32 KB touched per hart fitted in the L3 and measured that instead: <b>${L3.map(([h,z,r],i)=>`${z.pj_per_byte.mean.toFixed(1)}${i?'':' pJ/B on zeros'} and ${r.pj_per_byte.mean.toFixed(1)}${i?'':' on random data'} on ${cname(h)}`).join(', ')}</b>, at ${nf(l3.bytes_per_s.mean/1e9)} GB/s on ${L3.length>2?'every card':L3.length===2?'both':CARDS[0]}, the L3 read by tensor loads through the mesh.`;})():'');
 }
 const nb=[0,1,2,3].map(k=>S[`neigh/${k}/random`]); if(nb.every(v=>v)){
  $('neightab').innerHTML='<thead><tr><th>Neighbourhood reading the shire’s own scratchpad (random data)</th><th class="num">pJ/B, '+ALLC+'</th><th class="num" data-nosort>per card</th><th class="num">GB/s</th></tr></thead><tbody>'+
   nb.map((v,k)=>{const c=cb(`neigh/${k}/random`);return `<tr><td>${k}: minions ${8*k}–${8*k+7}</td><td class="num">${c?bt(c,f2):v.pj_per_byte.mean.toFixed(2)}</td><td class="num small">${c?pcs(c,f2):v.pj_per_byte.se.toFixed(2)}</td><td class="num">${nf(v.bytes_per_s.mean/1e9)}</td></tr>`;}).join('')+'</tbody>';
 }
})();

/* ---------- 4.5 where the current flows, by meter ---------- */
(function(){
 const S=SA;
 const groups=[['scalar integer',['add','sub','and','or','xor','sll','srl','sra','slt','sltu','addi','andi','ori','xori','slli','srli'].map(n=>`${n}/random/h2`)],
  ['scalar multiply',['mul','mulh','mulhu','mulhsu'].map(n=>`${n}/random/h2`)],['scalar float',['fadd.s','fsub.s','fmul.s','fmadd.s','fmsub.s'].map(n=>`${n}/random/h2`)],
  ['vector float',['fadd.ps','fsub.ps','fmul.ps','fmadd.ps','fmsub.ps'].map(n=>`${n}/random/h2`)],['vector integer',['fadd.pi','fsub.pi','fmul.pi','fand.pi','fxor.pi'].map(n=>`${n}/random/h2`)],
  ['transcendental',['fexp.ps','flog.ps','frcp.ps'].map(n=>`${n}/random/h2`)],['L1 hits',['lw','ld','sw','sd','flw.ps','fsw.ps'].map(n=>`${n}/random/h2`)],
  ['L1-bypass to the L2',['flwl.ps','fswl.ps'].map(n=>`${n}/random/h2`)],['atomics, local L2',['amoaddl.w/random/h2','amoaddl.d/random/h2']],['atomics, home L3',['amoaddg.w/random/h2','amoaddg.d/random/h2']],
  ['own scratchpad, tensor load',['tload/scp/random']],['own scratchpad, tensor store',['tstore/scp/random']],['scratchpad 1 hop away',['wire/hop1/random']],['scratchpad 3 hops away',['wire/hop3/random']],['scratchpad 6 hops away',['wire/hop6/random']],
  ['L3, tensor load',['dramrow/stride8K/random']],['DRAM, tensor load',['tload/dram/random']],['DRAM, tensor store',['tstore/dram/random']],['DRAM, stores through the L1',['st_stream/dram/random']]];
 const PARTS=[['minions','var(--c1)'],['SRAM','var(--c3)'],['mesh','var(--c2)'],['no sensor (regulators, PHYs)','var(--ref)']];
 const rows=[]; groups.forEach(gp=>{const rs=gp[1].map(k=>S[k]).filter(Boolean); if(!rs.length)return;
  const av=fn=>rs.reduce((a,r)=>a+fn(r),0)/rs.length, o=av(r=>r.over_idle_w.mean), m=av(r=>r.rails_over_w.minion_w.mean), sr=av(r=>r.rails_over_w.sram_w.mean), n=av(r=>r.rails_over_w.noc_w.mean);
  rows.push({label:gp[0],o,parts:[m,sr,n,o-m-sr-n]});});
 if(!rows.length)return;
 CK.legend('rails-legend',PARTS.map((p,i)=>({key:'p'+i,label:p[0],mark:'box',color:p[1]})));
 CK.frame('railsplit',{height:W=>(W<480?rows.length*42:rows.length*26)+30,label:'Each class of operation split across the metered rails',draw:f=>{
  const stack=f.W<480, L=stack?0:Math.min(220,Math.round(0.34*f.W)), Rr=8, pitch=stack?42:26, bh=stack?18:20, T=4;
  const x=CK.lin(0,1,L,f.W-Rr), nodes=[];
  rows.forEach((r,i)=>{const y0=T+i*pitch, by=stack?y0+18:y0+2; let acc=0;
   CK.txt(f.svg,stack?0:L-8,stack?y0+13:y0+16,r.label,'lab',stack?'start':'end');
   const pos=r.parts.reduce((a,v)=>a+Math.max(0,v),0);
   r.parts.forEach((v,j)=>{const fr=Math.max(0,v)/pos, w=Math.max(0,x(acc+fr)-x(acc)-(j<3?2:0));
    if(w>0.5)nodes.push(mark(f,f.svg,'rect',{x:x(acc),y:by,width:w,height:bh,fill:PARTS[j][1],rx:1},0,`<b>${r.label}</b>: ${f2(r.o)} W over idle<br>${PARTS[j][0]}: ${f2(v)} W (${Math.round(100*v/r.o)}%)`)); acc+=fr;});});
  const yb=T+rows.length*pitch+8; [0,0.25,0.5,0.75,1].forEach(t=>{CK.el('line',{x1:x(t),x2:x(t),y1:yb-6,y2:yb-2,class:'ck-axis'},f.svg); CK.txt(f.svg,x(t),yb+10,Math.round(100*t)+'%','tick',t===0?'start':t===1?'end':'middle');});
  CK.keynav(f,nodes);
 }});
 const RF=D.catalogue.rail_filter, taus=RF?Object.values(RF).map(v=>v.tau_s):[];
 $('railscap').textContent=`Random data, ${CARDS[0]}, mean of three passes. The split of each burst's power over idle across the three rails the PMIC meters, read from the end of the burst and corrected for the lag of the PMIC's own running average (a time constant of ${RF?andList(CK.cardsIn(RF).filter(h=>RF[h]).map(h=>`${f2(RF[h].tau_s)} s on ${cname(h)}`)):'about a second'}); the remainder has no sensor.`;
 const wire6=rows.find(r=>r.label==='scratchpad 6 hops away'), si=rows.find(r=>r.label==='scalar integer'), dr=rows.find(r=>r.label==='DRAM, tensor load');
 const U=D.unmetered, dd=U&&U.ddr_droop, dl=cb('tload/dram/random'), uh=U?CK.cardsIn(U).filter(h=>U[h]&&U[h].coef):[], mn=uh.map(h=>100*U[h].coef.minion), dp=uh.map(h=>U[h].coef.dram_pj_per_byte);
 if(wire6&&si) $('railstext').innerHTML=`<p><b>An instruction’s energy is the core’s</b>: ${Math.round(100*si.parts[0]/si.o)}% of a scalar integer burst is on the minion rail, almost nothing on the SRAM or the mesh, and the rest is consistent with what the regulators lose delivering it. <b>A byte fetched across the mesh is mostly wire</b>: six hops away, ${Math.round(100*wire6.parts[2]/wire6.o)}% of the energy is on the mesh rail and ${Math.round(100*wire6.parts[1]/wire6.o)}% on the SRAM that holds it, with the minions that asked for it at most about a sixth (${Math.round(100*wire6.parts[0]/wire6.o)}% measured, not resolved from zero).`+
  (dr?` <b>A DRAM byte is mostly off-chip</b>: ${Math.round(100*dr.parts[3]/dr.o)}% of its energy is on no metered rail.`+(U&&U.aifoundry2&&dl?` Fitted over this whole catalogue in <a href="${HUB}#the-unmetered-remainder-attributed">Limits of observability, §4.2–4.3</a>, ${f0(Math.min(...dp))}${Math.round(Math.min(...dp))!==Math.round(Math.max(...dp))?'–'+f0(Math.max(...dp)):''} of its ${f0(dl.mean)} pJ/B sit in the DDR PHY, the I/O rail and the DRAM chips (the fitted coefficient, ${andList(uh.map((h,i)=>`${f0(dp[i])} on ${cname(h)}`))}), and the rest of the unmetered share is consistent with the regulators' delivery loss (${mn.length>1?`${andList(uh.map((h,i)=>`${f0(mn[i])}%`))} of the minion rail's watts on ${andList(uh.map(cname))}`:`${f0(mn[0])}% of the minion rail's watts`}, as far as the rails' meters can be trusted) plus the fit's residual${dd?`; the same page reads DRAM power from the DDR rail's voltage droop, 1 mV for about ${f1(1/dd.mv_per_dram_offrail_w)} W`:''}.`:''):'')+'</p>';
})();

/* ---------- 5. comm ---------- */
(function(){
 const rg=RR.rings_pj_per_byte||{}, rr=RR.relay_pj_per_byte||{};
 const val=(r)=>rg[r.ring]?bt(rg[r.ring],f2):`<b>${f2(r.pj_per_byte)}</b> ± ${f2(r.pj_spread)}`;
 const hopk=k=>{const m=MH[k]; return !m?'—':m.mean?`${f1(m.mean)} <span class="small">(${m.min}–${m.max})</span>`:'0';};
 const name=k=>{const x=k.match(/^xshire(\d+)(-c4)?$/); if(x)return `Shires ${x[1]} ID${x[1]==='1'?'':'s'} apart${x[2]?', 128 B':''}`;
   return {pair:'Pair',neigh:'Neighbourhood',shire:'Shire','shire-c4':'Shire, 128 B'}[k]||k;};
 const esc=s=>String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;');
 /* in-shire rings first, then the 1 KB rings between shires by mean mesh distance, then the 128 B rows */
 const small=k=>k.endsWith('c4'), dist=k=>(MH[k]||{mean:0}).mean;
 const rows=[...D.comm.rows].sort((a,b)=>(small(a.ring)-small(b.ring))||(dist(a.ring)-dist(b.ring)));
 $('comm').innerHTML='<thead><tr><th>Ring, 1 KB messages unless said</th><th class="what" data-nosort>What moves</th><th class="num">Mesh hops, mean (range)</th><th class="num">pJ/B</th><th class="num" data-nosort>per card</th><th class="num">GB/s aggregate</th></tr></thead><tbody>'+
  rows.map(r=>`<tr><td title="${esc(r.what)}">${name(r.ring)} <span class="small">(${r.ring})</span></td><td class="small what">${r.what}</td><td class="num">${hopk(r.ring)}</td><td class="num">${val(r)}</td><td class="num small">${rg[r.ring]?pcs(rg[r.ring],f2):'a2, 2 runs'}</td><td class="num">${nf(r.gb_s)}</td></tr>`).join('')+
  '</tbody><tbody><tr><td colspan="6"><b>Handing a slab to the next shire</b> <span class="small">(the relay: a stage reads a slab, adds 1 and writes it where the next stage reads it)</span></td></tr>'+
  [['hop','in the next shire’s scratchpad','write where the next shire reads, read there; the next shire by ID',MH.xshire1?hopk('xshire1'):'—'],['dram','through DRAM','write to DRAM, read back','—'],['scp','kept in this shire’s scratchpad','write and read in place','0']].map(m=>
   `<tr><td title="${esc(m[2])}">${m[1]}</td><td class="small what">${m[2]}</td><td class="num">${m[3]}</td><td class="num">${rr[m[0]]?bt(rr[m[0]],f1):'<b>'+f1(rp[m[0]].pj_per_byte)+'</b>'}</td><td class="num small">${rr[m[0]]?pcs(rr[m[0]],f1):'a2 only'}</td><td class="num">${nf(rp[m[0]].bytes_per_s/1e9)}</td></tr>`).join('')+
  '</tbody>';
 $('commnote').innerHTML=(rg.shire?(()=>{
    /* the 18 September runs were on aifoundry2, so they are set against aifoundry2's own new passes */
    const d=D.comm.rows.filter(r=>rg[r.ring]&&rg[r.ring].per_card.aifoundry2&&r.pj_per_byte_local).map(r=>100*(r.pj_per_byte_local/rg[r.ring].per_card.aifoundry2.mean-1)).sort((a,b)=>a-b);
    const pm=v=>(v<0?'−':'+')+f0(Math.abs(v));
    const PP=RR.passes_per_card||{}, rp_=PP.rings||{}, yp=PP.relay||{}, nPass=o=>{const n=[...new Set(CK.cardsIn(o).map(h=>o[h].length))]; return n.length===1?`${WORD[n[0]]||n[0]} passes on each of ${WORD[CK.cardsIn(o).length]||CK.cardsIn(o).length} cards`:andList(CK.cardsIn(o).map(h=>`${WORD[o[h].length]||o[h].length} on ${cname(h)}`))+' passes';};
    /* the s <-> s+16 ring: its bursts starved the sampler in every version-3 pass; it keeps the 23 September passes (reruns.fallback_23sep) */
    const x16=(RR.dropped||[]).filter(x=>x.burst==='xshire16'&&x.sampler_median_ms!=null), v3x=x16.filter(x=>/claims-v3/.test(x.pass)), fb=(RR.fallback_23sep||{}).xshire16;
    const cardsOf=xs=>[...new Set(xs.map(x=>(String(x.pass).match(/raw\/([^/]+)\//)||[])[1]).filter(Boolean))];
    const ms=xs=>xs.length?`${f0(Math.min(...xs.map(x=>x.sampler_median_ms)))}–${f0(Math.max(...xs.map(x=>x.sampler_median_ms)))} ms`:'over 60 ms';
    return `<p class="small">Rings: re-measured in the version-3 check (26 September) with the manual's own sampler, ${nPass(rp_)} (n = ${rg.shire.n}); they replace the three passes on each of two cards of 23 September. The 18 September pair of runs on aifoundry2, sampled without the die temperature and so without a leakage correction, is not pooled; against aifoundry2's own new passes the values <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication">On-chip communication</a> publishes from it read ${pm(d[0])}% to ${pm(d[d.length-1])}% (median ${pm(d[d.length>>1])}%). `+
      (v3x.length?`The s ↔ s+16 ring starves the service processor's own management path — the sampler's latency rises from 22 ms to ${ms(v3x)} and the board reading takes a new value about twice a second instead of six times — in every version-3 pass on ${andList(CK.cardsIn(cardsOf(v3x)).map(cname))}, so those bursts were dropped${fb?` and that row keeps ${andList(fb.cards.map(cname))}'s three passes of 23 September, when its sampler stayed at 22 ms`:''}. `:'')+
      `Relay: ${nPass(yp)} (n = ${rr.dram?rr.dram.n:'—'}), 26 September; they replace the 22 September session (<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay">Hand it to the next shire</a>) and the 23 September passes. GB/s: the 22 September session's, on aifoundry2. `+
      `Mesh hops: the Manhattan distance between shire s and shire s + k (or s − 1 for the relay), averaged over all 32 compute shires.</p>`;})():'');
 const mesh=D.comm.rows.filter(r=>r.ring.startsWith('xshire')&&!r.ring.includes('c4'));
 const xs=mesh.map(r=>rg[r.ring]?rg[r.ring].mean:r.pj_per_byte);
 const fit=MH.xshire1?lfit(mesh.map(r=>[MH[r.ring].mean,rg[r.ring]?rg[r.ring].mean:r.pj_per_byte])):null, hx=mesh.map(r=>(MH[r.ring]||{}).mean||0);
 const nb=rg.neigh?rg.neigh.mean:D.comm.rows.find(r=>r.ring==='neigh').pj_per_byte, sh=rg.shire?rg.shire.mean:D.comm.rows.find(r=>r.ring==='shire').pj_per_byte;
 const pr=rg.pair?rg.pair.mean:D.comm.rows.find(r=>r.ring==='pair').pj_per_byte;
 const hop=rr.hop?rr.hop.mean:rp.hop.pj_per_byte, dram=rr.dram?rr.dram.mean:rp.dram.pj_per_byte;
 const hw=['dram','hop','scp'].filter(k=>rr[k]).map(k=>100*(rr[k].hi-rr[k].lo)/2/rr[k].mean), ow=['dram','hop','scp'].map(k=>rp[k].over_idle_w);
 /* the line through the rings between shires, per card, on the rings every card measured (the pooled line mixes cards,
    and the s <-> s+16 ring has aifoundry3's 23 September passes only) */
 const rcards=CK.cardsIn(Object.assign({},...mesh.filter(r=>rg[r.ring]).map(r=>rg[r.ring].per_card)));
 const both=mesh.filter(r=>rg[r.ring]&&rcards.every(h=>rg[r.ring].per_card[h])&&MH[r.ring]);
 const pcFit=MH.xshire1&&both.length>=3?rcards.map(h=>[h,lfit(both.map(r=>[MH[r.ring].mean,rg[r.ring].per_card[h].mean]))]):null, hb=both.map(r=>MH[r.ring].mean);
 const rpc=CK.cardsIn((rr.dram||{}).per_card||{}).filter(h=>rr.hop&&rr.hop.per_card[h]);
 /* the version-3 check on the rings (V3-RL): the mesh slope pooled over the cards (RL-a), the step out of the shire (RL-b), the
    128 B rows against the 1 KB ones (RL-c), the relay's DRAM round trip against the hand-off (RL-d) */
 const RL=V3.rl||{}, MS=RL.mesh_slope||{}, ES=RL.exit_step||{}, SMm=RL.small_messages||{}, RQ=RL.relay_ratio||{};
 const esY=CK.cardsIn(ES).filter(h=>ES[h].ci99[0]>0), esN=CK.cardsIn(ES).filter(h=>!(ES[h].ci99[0]>0));
 const smAll=Object.keys(SMm).length&&Object.values(SMm).every(o=>CK.cardsIn(o).every(h=>o[h].ci99[0]>0)), smCards=Object.keys(SMm).length?CK.cardsIn(Object.values(SMm)[0]):[];
 /* bandwidth: the in-shire 1 KB rings (pair, neighbourhood, shire) against the rings between shires, the same busy cores (On-chip communication) */
 const inS=D.comm.rows.filter(r=>['pair','neigh','shire'].includes(r.ring)&&r.gb_s).map(r=>r.gb_s), xS=mesh.filter(r=>r.gb_s).map(r=>r.gb_s),
  gbr=inS.length&&xS.length?[Math.min(...inS)/Math.max(...xS),Math.max(...inS)/Math.min(...xS)]:null;
 const ci1=x=>`${f1(x.mean)} [${mf2(x.ci99[0]).replace(/(\.\d)\d$/,'$1')}, ${f1(x.ci99[1])}]`;
 $('commtext').innerHTML=`Between the two minions of a pair a byte costs under a picojoule (${f2(pr)} pJ); around a neighbourhood or a shire about ${f1((nb+sh)/2)} pJ; across the mesh ${f0(Math.min(...xs))}–${f0(Math.max(...xs))} pJ. `+
  (pcFit?`A straight line through the 1 KB rings between shires against their mean distances (the ${WORD[both.length]||both.length} that ${rcards.length>2?'every card':'both cards'} measured, ${f1(Math.min(...hb))}–${f1(Math.max(...hb))} hops) gives ${semiList(pcFit.map(([h,q],i)=>`${f1(q.a)}${i?'':' pJ to leave the shire'} plus ${f1(q.b)}${i?'':' pJ per mesh hop'} on ${cname(h)}`))}${MS.pooled!=null?`; the version-3 check finds no card's per-hop cost different from another's, ${f2(MS.pooled)} pJ/B per hop pooled`:''}. `+
   `<b>For messages, leaving the shire is the biggest step</b>, mostly because the same busy cores move ${gbr?`${f0(gbr[0])}–${f0(gbr[1])}`:'7–34'}× fewer bytes across the mesh than around a shire (<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication">On-chip communication</a>); for tensor loads it costs about one hop (section 4.3).`+
   (esY.length?` The step out of the shire beyond one hop is ${andList(esY.map(h=>`${ci1(ES[h])} pJ/B on ${cname(h)}`))}${esN.length?`, not resolved on ${andList(esN.map(h=>`${cname(h)} (${ci1(ES[h])})`))}`:''} (99% intervals over six passes). `:' '):'')+
  (smAll?`<b>Small messages cost more per byte</b>: the 128 B rows are dearer than the 1 KB ones on ${smCards.length>2?'every card':andList(smCards.map(cname))}, by ${andList(Object.entries(SMm).map(([k,o])=>`${f1(Math.min(...CK.cardsIn(o).map(h=>o[h].mean)))}–${f1(Math.max(...CK.cardsIn(o).map(h=>o[h].mean)))} pJ/B ${k.startsWith('shire')?'around a shire':'between neighbouring shire IDs'}`))} (resolved from zero at 99% on each); `:`Small messages cost more per byte in the 128 B rows; `)+
  `the per-message overhead is 40–224 cycles of the sending and receiving harts (<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication">On-chip communication</a>, one session on aifoundry2). `+
  (rpc.length>1?(()=>{const hi=rpc.reduce((a,h)=>rr.dram.per_card[h].mean>rr.dram.per_card[a].mean?h:a), rest=rpc.filter(h=>h!==hi), prem=rest.map(h=>100*(rr.dram.per_card[hi].mean/rr.dram.per_card[h].mean-1)), sePct=Math.max(...rpc.map(h=>100*rr.dram.per_card[h].se/rr.dram.per_card[h].mean));
    return `<b>Handing a slab to the next shire through its scratchpad is ${andList(rpc.map(h=>f1(rr.dram.per_card[h].mean/rr.hop.per_card[h].mean)+'×'))} cheaper than the DRAM round trip</b> on ${andList(rpc.map(cname))}${RQ.pooled!=null?` (the same on every card at 99%, ${f1(RQ.pooled)}× pooled)`:''}; the hand-off itself costs ${andList(rpc.map(h=>f1(rr.hop.per_card[h].mean)))} pJ/B in that order. `+
     `The three relay bars are ±${f0(Math.min(...hw))}–${f0(Math.max(...hw))}%, most of it ${cname(hi)} reading ${f0(Math.min(...prem))}–${f0(Math.max(...prem))}% above the others through DRAM (a difference the version-3 check resolves); within a card the passes agree to ${f0(Math.ceil(sePct))}% (standard error).`;})():
   `Handing a slab to the next shire through its scratchpad is ${f0(dram/hop)}× cheaper than the DRAM round trip. The three relay bars are ±${f0(Math.min(...hw))}–${f0(Math.max(...hw))}% because each is a ${f0(Math.min(...ow))}–${f0(Math.max(...ow))} W signal over a board idle that drifts; the DRAM relay's power also rides on a path with no rail sensor.`);
 /* the rings chart: pJ/B against mean mesh hops, one dot per ring per card, each card's own line (the same fit as the
    text above) and, dashed in the same colour, section 4.3's tensor-load wire fit over 1-6 hops, for comparison */
 const ringCards=CK.cardsIn(mesh.reduce((s,r)=>rg[r.ring]?s.concat(Object.keys(rg[r.ring].per_card)):s,[]));
 const wireFit=h=>{const w=D.catalogue.cards[h]&&D.catalogue.cards[h].wire&&D.catalogue.cards[h].wire.random;
  if(!w)return null; const pts=w.points.filter(p=>p.hops>=1&&p.hops<=6).map(p=>[p.hops,p.pj_per_byte]); return pts.length>=2?lfit(pts):null;};
 if(ringCards.length&&pcFit){
  const ringItems=ringCards.map(h=>cardItem(h,cname(h)+', rings (solid) and wire (dashed)'));
  CK.legend('rings-legend',ringItems); legendMarks('rings-legend',ringItems);
  const mxx=Math.max(...hb,6)+0.4, mxy=Math.max(...mesh.flatMap(r=>ringCards.map(h=>rg[r.ring]&&rg[r.ring].per_card[h]?rg[r.ring].per_card[h].mean+(rg[r.ring].per_card[h].se||0):0)))*1.08;
  CK.frame('rings',{height:W=>W<600?260:300,label:'Energy per byte for the rings between shires against mean mesh distance',draw:f=>{
   const L=40,Rr=12,T=24,B=38, x=CK.lin(0,mxx,L,f.W-Rr), y=CK.lin(0,mxy,f.H-B,T);
   CK.axes(f,{x,y,L,R:Rr,T,B,xl:'mean mesh hops',yl:'pJ per byte'});
   ringCards.forEach(h=>{const wf=wireFit(h);
    if(wf)CK.el('line',{x1:x(0),x2:x(mxx),y1:y(wf.a),y2:y(wf.a+wf.b*mxx),stroke:CK.card(h).color,'stroke-width':1.3,'stroke-dasharray':'5 4'},f.svg);
    const ft=(pcFit.find(p=>p[0]===h)||[])[1]; if(ft)CK.el('line',{x1:x(0),x2:x(mxx),y1:y(ft.a),y2:y(ft.a+ft.b*mxx),stroke:CK.card(h).color,'stroke-width':1.8},f.svg);
   });
   ringCards.forEach(h=>{
    const nodes=mesh.filter(r=>MH[r.ring]&&rg[r.ring]&&rg[r.ring].per_card[h]).map(r=>{
     const c=rg[r.ring].per_card[h], hh=MH[r.ring].mean;
     if(c.se)ebar(f.svg,x(hh),y(c.mean+c.se),y(c.mean-c.se),CK.card(h).color);
     return cmark(f,f.svg,h,x(hh),y(c.mean),4,8,`${name(r.ring)}, ${cname(h)}: <b>${f1(c.mean)}</b> ± ${f2(c.se||0)} pJ/B at ${f1(hh)} mean hops (n = ${c.n})`);
    });
    CK.keynav(f,nodes);
   });
  }});
  $('ringscap').textContent=`Solid: each card's own line through the ${WORD[both.length]||both.length} rings ${rcards.length>2?'every card':'both cards'} measured, the same fit as the text above. Bars: each card's pass-to-pass standard error. Dashed: section 4.3's tensor-load wire fit over 1–6 hops, in the same card's colour, for comparison: for messages leaving the shire is the biggest step, for tensor loads it costs about one hop (section 4.3), so the lines need not agree past it.`;
 }
})();

/* ---------- 6. sync ---------- */
(function(){
 const hn=RR.hotline_nj_per_op||{};
 /* the chip barrier's waiting energy: 1,024 minions stalled for its length at the pooled stalled power (section 2) */
 const stallW=HOT?HOT.mean:at.contended.over_idle_w, bar=stallW*D.sync.barrier_cycles_chip/0.6e9*1e6;
 const conm=hn.contended?hn.contended.mean:at.contended.nj_per_op, sprm=hn.spread?hn.spread.mean:at.spread.nj_per_op;
 /* the latencies of the version-3 check on three cards (manual.json sync.v3, V3-LAT: every kept pass per card) and the
    remote atomic's round trip per card (the hot line's passes) */
 const SV=D.sync.v3, RA=D.sync.remote_atomic_latency_by_card;
 const latAll=o=>CK.cardsIn(o).flatMap(h=>o[h]), latMean=o=>{const a=latAll(o); return a.reduce((x,y)=>x+y,0)/a.length;};
 const latRng=(o,g)=>{const a=latAll(o), lo=g(Math.min(...a)), hi=g(Math.max(...a)); return lo===hi?lo:`${lo}–${hi}`;};
 const latPc=(o,g)=>CK.cardsIn(o).map(h=>{const lo=g(Math.min(...o[h])), hi=g(Math.max(...o[h])); return `${cshort(h)} ${lo===hi?lo:lo+'–'+hi}`;}).join('<br>');
 const latN=(o,k=1)=>{const hs=CK.cardsIn(o), n=hs.map(h=>o[h].length/k), each=hs.length===3?'the three cards':andList(hs.map(cname)); return (n.every(x=>x===n[0])?`${WORD[n[0]]||n[0]} passes on each of `:'every pass on ')+each;};  /* k values a pass (the shire barrier: two variants) */
 $('sync').innerHTML='<thead><tr><th>Event</th><th class="num">Energy</th><th class="num" data-nosort>per card</th><th class="num">Time</th><th data-nosort>Note</th></tr></thead><tbody>'+
  `<tr><td>Global atomic, one line, 1,024 requesters</td><td class="num">${hn.contended?bt(hn.contended,f1)+' nJ':'<b>'+f1(at.contended.nj_per_op)+' nJ</b>'}</td><td class="num small">${hn.contended?pcs(hn.contended,f1):'a2 only'}</td><td class="num">${f0(at.contended.cycles_per_op)} cycles each at the bank</td><td class="small">the bank serialises and every requester waits its turn; the host shire's own loads stop</td></tr>`+
  `<tr><td>Global atomic, 32 lines, one per shire</td><td class="num">${hn.spread?bt(hn.spread,f2)+' nJ':f1(at.spread.nj_per_op)+' nJ'}</td><td class="num small">${hn.spread?pcs(hn.spread,f2):'a2 only'}</td><td class="num">${f2(at.spread.cycles_per_op)} cycles each, aggregate</td><td class="small">the same instruction, ${f0(conm/sprm)}× cheaper</td></tr>`+
  `<tr><td>Uncontended remote atomic round trip</td><td class="num">—</td><td class="num small">${RA?latPc(Object.fromEntries(Object.entries(RA).map(([h,v])=>[h,[v]])),v=>v.toFixed(1)):''}</td><td class="num">${f0(D.sync.remote_atomic_latency_cycles)} cycles</td><td class="small">${RA?`the same on ${CK.cardsIn(RA).length===CARDLIST.length?ALLC:andList(CK.cardsIn(RA).map(cname))} (<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line">One hot line stops a shire</a>, 26 September)`:'the same on both cards'}</td></tr>`+
  `<tr><td>Chip-wide barrier, ${nf(D.sync.barrier_participants||1024)} minions</td><td class="num" data-sort="${1000*bar}">≈ ${f0(bar)} µJ of waiting</td><td class="num small">${SV?latPc(SV.chip_barrier_all,nf):''}</td><td class="num">${SV?latRng(SV.chip_barrier_all,nf):nf(D.sync.barrier_cycles_chip)} cycles</td><td class="small">derived: 1,024 minions stalled at ${f1(stallW/1024*1e3)} mW (section 2) for its length, ${SV?`${nf(D.sync.barrier_cycles_chip)} cycles, the mean of ${latN(SV.chip_barrier_all)} (the version-3 check, 26 September); with one minion per shire ${latRng(SV.chip_barrier_one_per_shire,nf)} cycles; one run on aifoundry2 on 18 September gave ${nf(D.sync.barrier_cycles_chip_18sep)}`:'the length is one run on aifoundry2 (18 September)'}</td></tr>`+
  `<tr><td>FLB (fast local barrier) + credit barrier, one shire</td><td class="num">—</td><td class="num small">${SV?latPc(SV.shire_barrier,f1):''}</td><td class="num">${SV?f0(latMean(SV.shire_barrier)):237} cycles</td><td class="small"><a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication">On-chip communication</a>${SV?`, ${latN(SV.shire_barrier,2)} (the version-3 check, 26 September; 237 on aifoundry2 on 18 September)`:', aifoundry2, 18 September'}</td></tr>`+
  `<tr><td>TensorReduce (the hardware reduction tree) + broadcast, 32 minions</td><td class="num">—</td><td class="num small">${SV?latPc(SV.allreduce32,f1):''}</td><td class="num">${SV?f0(latMean(SV.allreduce32)):432} cycles</td><td class="small"><a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication">On-chip communication</a>${SV?`, ${latN(SV.allreduce32)} (the version-3 check, 26 September; 432 on aifoundry2 on 18 September)`:', aifoundry2, 18 September'}</td></tr>`+
  '</tbody>';
 $('syncnote').innerHTML=(hn.contended?`Hot line: 22 September and ${WORD[(hn.contended.per_card.aifoundry2||{n:1}).n-1]} warm passes on aifoundry2, ${WORD[(hn.contended.per_card.aifoundry3||{n:0}).n]} passes on aifoundry3 (n = ${hn.contended.n}). The first session alone (aifoundry2, 22 September, one run) gave ${f1(at.contended.nj_per_op)} and ${f2(at.spread.nj_per_op)} nJ. The contended row’s bar is wide mostly because of that session: the whole chip stalled drew ${f1(at.contended.over_idle_w)} W over idle in it, against ${HOT&&HOT.n>1?f2((HOT.n*HOT.mean-at.contended.over_idle_w)/(HOT.n-1)):f1(conm*at.contended.ops_per_s*1e-9)} W in the mean of the passes since, and the per-operation figure divides that small number by a rate the bank fixes at one per 10 cycles.`:'');
})();

/* ---------- 7.1 build a workload's energy (em-v1) ---------- */
(function(){
 const rg=RR.rings_pj_per_byte||{}, rr=RR.relay_pj_per_byte||{};
 /* ENT: every event the calculator can price, on card h ('pooled' or a card id from the page's card bus).
    e(o,h) is {mean,lo,hi} per event: pooled, the mean over every pass on every card and their range; on a card, its own
    mean and the range over its passes (± its standard error for the tensor unit and the rings); null when h has no value.
    rate(o,h) is what the card reached per second running it alone: pooled, the mean over the cards; null when h did not
    run it. rcard: the one card a row's rate was timed on, when only one was (the tensor unit, the rings), named in the
    readout. unit MAC | instr | byte; issue rows share the harts' issue slots. */
 const TCARD=srcCard(D.tensor.source&&D.tensor.source.rows), RCARD=srcCard(D.comm.source);
 const ENT={}, GROUPS=[], put=(grp,id,o)=>{ENT[id]=Object.assign({id,rcard:null},o); let gp=GROUPS.find(g=>g[0]===grp); if(!gp)GROUPS.push(gp=[grp,[]]); gp[1].push(id);};
 const tcfg=(ty,o)=>`${ty}_${o==='zeros'?'zeros':'randn'}`;
 ['fp32','fp16','int8'].forEach(ty=>{if(!TB[tcfg(ty,'random')])return; put('Tensor unit, per multiply-add','t:'+ty,{label:`TensorFMA ${ty}, all 1,024 minions`,short:`TensorFMA ${ty}`,unit:'MAC',issue:true,
   e:(o,h)=>pcv(TB[tcfg(ty,o)],h), rate:o=>D.tensor.rows.find(r=>r.config===tcfg(ty,o)).per_s, rcard:TCARD});});
 const catE=(grp,k,sfx,label,short,issue,unit)=>{if(!CB[`${k}/random${sfx}`])return; const ok=o=>`${k}/${CB[`${k}/${o}${sfx}`]?o:'random'}${sfx}`;
  put(grp,'c:'+k+sfx,{label,short:short||label,unit,issue,e:(o,h)=>cbc(ok(o),h),rate:(o,h)=>rateC(ok(o),unit==='byte'?'bytes_per_s':'ops_per_s',h),only:CB[`${k}/zeros${sfx}`]?null:'random'});};
 CLASSES.forEach(c=>c[1].forEach(n=>catE(c[0]+' (both harts, per instruction)',n,'/h2',n,n,true,'instr')));
 [['tload/scp','own scratchpad, tensor load'],['tstore/scp','own scratchpad, tensor store'],['l1fill/stride32','own scratchpad, 32 B loads through the L1'],['tload/dram','DRAM, tensor load'],['tstore/dram','DRAM, tensor store'],['st_stream/dram','DRAM, stores through the L1'],['dramrow/stride8K','L3, tensor load through the mesh']]
  .forEach(([k,l])=>catE('Bytes through the memory hierarchy (per byte)',k,'',l,l,false,'byte'));
 [1,2,3,4,5,6,8].forEach(d=>catE('Bytes from a scratchpad d hops away (tensor loads, per byte)',`wire/hop${d}`,'',`a scratchpad ${d} hop${d>1?'s':''} away`,null,false,'byte'));
 if(wireAt(HH,'random'))put('Bytes from a scratchpad d hops away (tensor loads, per byte)','w:hh',{label:`a scratchpad ${f1(HH)} hops away (interpolated; the relay's next shire)`,short:`a scratchpad ${f1(HH)} hops away`,unit:'byte',issue:false,e:(o,h)=>wireAt(HH,o,h),
   rate:(o,h)=>{const lo=Math.floor(HH),hi=Math.ceil(HH),a=rateC(`wire/hop${lo}/${o}`,'bytes_per_s',h),b=rateC(`wire/hop${hi}/${o}`,'bytes_per_s',h); return a==null||b==null?null:a+(b-a)*(hi>lo?(HH-lo)/(hi-lo):0);}});
 D.comm.rows.filter(r=>!r.ring.endsWith('c4')&&rg[r.ring]).forEach(r=>put('Between cores: rings, 1 KB messages (per byte)','r:'+r.ring,{label:`ring ${r.ring}`,short:`ring ${r.ring}`,unit:'byte',issue:false,e:(o,h)=>pcv(rg[r.ring],h),rate:()=>r.gb_s*1e9,only:'own',rcard:RCARD}));
 const tRow=(ty,o)=>D.tensor.rows.find(r=>r.config===tcfg(ty,o));
 const relayP=(m,rd,wr,label)=>({label,rows:[[rd,rp[m].bytes_per_s/2],[wr,rp[m].bytes_per_s/2]],relay:m});
 const PRE=[['fp32','fp32 matmul',{rows:[['t:fp32',1]],tensor:'fp32'}],['fp16','fp16 matmul',{rows:[['t:fp16',1]],tensor:'fp16'}],['int8','int8 matmul',{rows:[['t:int8',1]],tensor:'int8'}],
  ['dram','stream from DRAM (tensor loads)',{rows:[['c:tload/dram',1]]}],
  ['rhop','relay: next shire',relayP('hop','w:hh','c:tstore/scp')],['rscp','relay: own scratchpad',relayP('scp','c:l1fill/stride32','c:tstore/scp')],['rdram','relay: through DRAM',relayP('dram','c:tload/dram','c:tstore/dram')]]
  .filter(p=>p[2].rows.every(r=>ENT[r[0]]));
 /* st.card follows the page's card bus; st.view 'one' draws the chosen card's bar, 'cmp' one bar per card */
 const st={T:80,o:'random',dur:7,rows:[{id:'',p:0},{id:'',p:0},{id:'',p:0}],preset:'fp32',capped:false,card:'pooled',view:'one'};
 const COL=['var(--c1)','var(--c2)','var(--c3)'];
 /* a preset gives each row a fraction of its measured rate (a number ≤ 1) or an absolute rate per second (a number > 1),
    the fraction taken of the pooled rate so that a preset does not depend on the card */
 function load(id){const p=PRE.find(q=>q[0]===id)[2]; st.preset=id;
  st.rows=[0,1,2].map(i=>{const r=p.rows[i]; if(!r)return {id:'',p:0}; const e=ENT[r[0]], v=r[1]>1?r[1]/e.rate(st.o,'pooled'):r[1]; return {id:r[0],p:Math.min(1,v)};});
  sync(); upd();}
 const pbox=$('calc-presets'), pbtn={};
 PRE.forEach(([id,label])=>{const b=document.createElement('button'); b.type='button'; b.textContent=label; b.setAttribute('aria-pressed','false'); b.addEventListener('click',()=>load(id)); pbox.appendChild(b); pbtn[id]=b;});
 const tr=CK.range('calc-temp',{label:'die temperature',min:45,max:95,step:1,value:80,fmt:v=>v+' °C',onInput:v=>{st.T=v; upd();}});
 const ds=CK.seg('calc-data',{label:'data',options:[['random','random'],['zeros','zeros']],value:'random',onChange:v=>{st.o=v; sync(); upd();}});
 CK.cardSeg('calc-card',{cards:CARDLIST,pooled:true,label:'priced on',onChange:v=>{st.card=v; sync(); upd();}});
 CK.seg('calc-view',{label:'show',options:[['one','one bar'],['cmp','compare cards']],value:'one',onChange:v=>{st.view=v; upd();}});
 const dur=$('calc-dur'); dur.addEventListener('input',()=>{const v=+dur.value; if(v>0){st.dur=v; upd();}});
 /* the three event rows: a select, a rate slider, and the absolute rate */
 const rowsBox=$('calc-rows'), UI=[];
 const opts='<option value="">(none)</option>'+GROUPS.map(([gname,ids])=>`<optgroup label="${gname}">`+ids.map(id=>`<option value="${id}">${ENT[id].label}</option>`).join('')+'</optgroup>').join('');
 const unitTxt={MAC:'MAC/s',instr:'instructions/s',byte:'B/s'};
 const rateTxt=(e,v)=>!(v>0)?'0 '+unitTxt[e.unit]:e.unit==='byte'?(v>=1e12?f2(v/1e12)+' TB/s':nf(v/1e9)+' GB/s'):sci(v)+' '+unitTxt[e.unit];
 [0,1,2].forEach(i=>{const d=document.createElement('div'); d.className='ck-controls calc-row';
  d.innerHTML=`<span class="ck-range"><label for="calc-e${i}">row ${i+1}</label><select id="calc-e${i}" aria-label="row ${i+1}: what the workload does">${opts}</select></span>`+
   `<span class="ck-range"><label for="calc-p${i}">rate, % of what the card reached</label><input type="range" id="calc-p${i}" min="0" max="100" step="1" aria-label="row ${i+1} rate, percent of what the card reached"><output for="calc-p${i}" id="calc-o${i}"></output></span>`;
  rowsBox.appendChild(d); const sel=d.querySelector('select'), rng=d.querySelector('input'), out=d.querySelector('output');
  sel.addEventListener('change',()=>{const e=sel.value?ENT[sel.value]:null, room=Math.max(0,Math.min(1,1-issueSum(i))); st.capped=!!(e&&e.issue&&room<1); st.rows[i]={id:sel.value,p:e?(e.issue?room:1):0}; st.preset=null; sync(); upd();});
  rng.addEventListener('input',()=>{const r=st.rows[i]; if(!r.id)return; let v=+rng.value/100; st.capped=false;
   if(ENT[r.id].issue){const room=1-issueSum(i); if(v>room+1e-9){v=Math.max(0,room); st.capped=true;}} r.p=v; st.preset=null; sync(st.capped?undefined:i); upd();});   /* a capped slider snaps back to the cap */
  UI.push({sel,rng,out});});
 const issueSum=skip=>st.rows.reduce((s,r,k)=>s+(k!==skip&&r.id&&ENT[r.id].issue?r.p:0),0);
 function sync(skipRange){st.rows.forEach((r,i)=>{const u=UI[i], e=r.id?ENT[r.id]:null; u.sel.value=r.id; u.rng.disabled=!e;
   if(skipRange!==i)u.rng.value=Math.round(100*r.p);
   const rt=e?e.rate(st.o,st.card):null, s=e?`${f0(100*r.p)}% · ${rt!=null?rateTxt(e,r.p*rt):'not run on '+cname(st.card)}`:'—'; u.out.textContent=s; u.rng.setAttribute('aria-valuetext',s);});
  for(const id in pbtn)pbtn[id].setAttribute('aria-pressed',String(id===st.preset));}
 /* the idle law priced for card h: its own when the data has one (rest.per_card[h] with P_fix_w, A_leak_80_w, T_L_c),
    otherwise the law fitted on LAWCARD in section 1, the only one fitted so far */
 const lawOf=h=>{const own=h&&h!=='pooled'&&R.per_card&&R.per_card[h];
  return own&&own.P_fix_w!=null&&own.A_leak_80_w!=null&&own.T_L_c?{P_fix_w:own.P_fix_w,A_leak_80_w:own.A_leak_80_w,T_L_c:own.T_L_c,card:h}:{P_fix_w:R.P_fix_w,A_leak_80_w:R.A_leak_80_w,T_L_c:R.T_L_c,card:LAWCARD};};
 /* price the current state on card h; a row card h has no value or rate for is left out (miss), never priced at zero */
 function price(o,T,h){const L=lawOf(h), fix=L.P_fix_w, leak=L.A_leak_80_w*Math.exp((T-80)/L.T_L_c), rows=[], miss=[];
  st.rows.forEach((r,i)=>{if(!r.id||r.p<=0)return; const e=ENT[r.id], c=e.e(o,h), rt=e.rate(o,h); if(!c||rt==null){miss.push(e); return;} const rate=r.p*rt;
   rows.push({i,e,rate,w:c.mean*rate*1e-12,lo:c.lo*rate*1e-12,hi:c.hi*rate*1e-12,c,op:e.only==='own'?'its own data':e.only&&o!=='random'?'random only':o});});
  const dyn=rows.reduce((s,r)=>s+r.w,0), lo=rows.reduce((s,r)=>s+r.lo,0), hi=rows.reduce((s,r)=>s+r.hi,0);
  return {fix,leak,rows,dyn,lo,hi,tot:fix+leak+dyn,miss,law:L,h};}
 /* the measurement the preset reproduces on card h: the ablation's board power at the card's own launch temperature (for
    the pooled bar, LAWCARD's unless strict), or the relay's measured energy per byte times its rate, over idle (comparable at
    any temperature, like every priced row; per card from the reruns) */
 function measured(h,strict){const p=st.preset&&PRE.find(q=>q[0]===st.preset); if(!p)return null; const q=p[2];
  if(q.tensor){const PR=D.tensor.per_card_rows||{}, cfg=tcfg(q.tensor,st.o), hh=h==='pooled'?(strict?null:LAWCARD):h, r=hh&&PR[hh]&&PR[hh][cfg]; if(!r)return null;
   const T=Math.round(r.launch_c); return {tot:r.idle_w+r.over_idle_w,T,label:`measured ${f1(r.idle_w+r.over_idle_w)} W`,src:`the version-3 ablation on ${cname(hh)}, launched at ${T} °C, the mean of its ${WORD[r.runs]||r.runs} runs, among those the price is built from`};}
  if(q.relay&&rr[q.relay]){const m0=rr[q.relay], pooled=h==='pooled', m=pooled?m0:CK.pick(m0,h); if(!m)return null; const bps=rp[q.relay].bytes_per_s, w=m.mean*bps*1e-12;
   return {over:w,label:`measured ${f1(w)} W over idle`,src:pooled?`the relay, ${f1(m0.mean)} pJ/B [${f1(m0.lo)}–${f1(m0.hi)}] × ${nf(bps/1e9)} GB/s, ${ALLC} (n = ${m0.n})`:`the relay on ${cname(h)}, ${f1(m.mean)} ± ${f1(m.se||0)} pJ/B × ${nf(bps/1e9)} GB/s (n = ${m.n})`,relay:q.relay};}
  return null;}
 /* what a price rests on, in words: whose means and rates, whose idle law, and which rows the card has no value for */
 const sgn=v=>(v<0?'−':'+')+f2(Math.abs(v)), LR=D.catalogue.idle_law_residual||{};
 function basis(pz){const h=pz.h, L=pz.law, x1=pz.rows.filter(r=>r.e.rcard&&r.e.rcard!==h), one=[...new Set(x1.map(r=>r.e.rcard))];
  let s=h==='pooled'?`Priced on ${ALLC}, pooled: each row's mean over every pass on them, at the mean of the rates they reached`
   :`Priced on ${cname(h)}: each row's own mean there (whisker: the range over its passes, or ± its standard error) at the rate it reached there`;
  if(x1.length)s+=`; ${andList(x1.map(r=>r.e.short))} at ${andList(one)}'s rate, the only card ${x1.length>1?'they were':'it was'} timed on`;
  s+=L.card===h?`; idle: ${cname(h)}'s own law${h!==LAWCARD&&R.per_card&&R.per_card[h]?` (section 1's form refitted to its idle in the version-3 cycles, ${R.per_card[h].T[0]}–${R.per_card[h].T[1]} °C)`:''}`:`; idle: ${L.card}'s law (section 1)${h==='pooled'?'':', the only one fitted'}`;
  if(h!=='pooled'&&L.card!==h&&LR[h]&&LR[h].die_c)s+=` (${cname(h)} sat ${sgn(LR[h].mean)} W from it at ${f0(LR[h].die_c[0])}–${f0(LR[h].die_c[1])} °C in the catalogue's idle stretches)`;
  s+='.'; if(pz.miss.length)s+=` Not measured on ${cname(h)}, so left out: ${andList(pz.miss.map(e=>e.short))}.`;
  return s;}
 const bars=()=>st.view==='cmp'?['pooled'].concat(CARDLIST):[st.card];
 const spread=q=>q.rows.length&&!q.rows.every(r=>r.c.nobar);   /* a whisker only when some row carries a spread */
 const barName=h=>h==='pooled'?`${ALLC}, pooled`:cname(h);
 const ro=CK.readout('calc-readout');
 const fc=CK.frame('calc',{height:W=>st.view==='cmp'?104+(bars().length-1)*44:(W<600?128:118),label:"Board power priced from the tables, for the chosen card or one bar per card",draw:f=>{
  const cmp=st.view==='cmp', hs=bars(), PZ=hs.map(h=>price(st.o,st.T,h)), MS=hs.map(h=>measured(h,cmp));
  const mx=Math.max(80,...PZ.map(pz=>Math.ceil((pz.fix+pz.leak+pz.hi+1)/20)*20));
  /* one bar: the original layout; compare: a name line above each bar */
  const L=8,Rr=16,T=cmp?24:34,bh=cmp?20:34,pitch=44, x=CK.lin(0,mx,L,f.W-Rr), top=i=>cmp?T+i*pitch+18:T, bot=top(hs.length-1)+bh;
  const ax=CK.el('g',{'aria-hidden':'true'},f.svg);
  x.ticks(f.narrow?4:8).forEach(t=>{CK.el('line',{x1:x(t),x2:x(t),y1:(cmp?T:top(0))-6,y2:bot+6,class:'grid-line'},ax); CK.txt(ax,x(t),bot+22,CK.fmt.num(t),'tick','middle');});
  CK.txt(ax,f.W-Rr,f.H-4,'board power, W','lab','end');
  const nodes=[];
  hs.forEach((h,i)=>{const pz=PZ[i], M=MS[i], y0=top(i), who=cmp?`<b>${barName(h)}</b> · `:'';
   if(cmp)CK.txt(f.svg,L,y0-6,`${barName(h)}: ${f1(pz.tot)} W${pz.miss.length?` (no ${andList(pz.miss.map(e=>e.short))})`:''}`,h===st.card?'lab-strong':'lab','start');
   const segs=[['fixed',pz.fix,'var(--ref)',`${who}<b>fixed</b>: ${f1(pz.fix)} W, the idle law's constant at its best fit (section 1${pz.law.card!==h?`, ${pz.law.card}'s law`:''})`],
     ['leakage',pz.leak,'var(--c4)',`${who}<b>leakage at ${st.T} °C</b>: ${f1(pz.leak)} W (section 1${pz.law.card!==h?`, ${pz.law.card}'s law`:''})`]]
    .concat(pz.rows.map(r=>[r.e.short,r.w,COL[r.i],`${who}<b>${r.e.label}</b>, ${r.op}<br>${fs(r.c.mean)} ${r.e.unit==='byte'?'pJ/B':r.e.unit==='MAC'?'pJ per MAC':'pJ per instruction'} ${barOf(r.c,fs)} × ${rateTxt(r.e,r.rate)}${r.e.rcard&&r.e.rcard!==h?` (${r.e.rcard}'s rate)`:''} = <b>${f1(r.w)} W</b>${r.c.nobar?'':` [${f1(r.lo)}–${f1(r.hi)}]`}`]));
   let acc=0;
   segs.forEach(s=>{const w=Math.max(0,x(acc+s[1])-x(acc)-2); if(w>0.3)nodes.push(mark(f,f.svg,'rect',{x:x(acc),y:y0,width:w,height:bh,fill:s[2],rx:2},0,s[3])); acc+=s[1];});
   if(spread(pz)){const a=x(pz.fix+pz.leak+pz.lo), b=x(pz.fix+pz.leak+pz.hi), cy=y0+bh/2;
    CK.el('line',{x1:a,x2:b,y1:cy,y2:cy,stroke:'var(--ink)','stroke-width':1.5},f.svg); [a,b].forEach(v=>CK.el('line',{x1:v,x2:v,y1:cy-6,y2:cy+6,stroke:'var(--ink)','stroke-width':1.5},f.svg));}
   if(M){const v=M.tot!=null?M.tot:pz.fix+pz.leak+M.over, live=M.T==null||Math.abs(st.T-M.T)<=2, xm=x(v), ext=cmp?4:8;
    CK.el('line',{x1:xm,x2:xm,y1:y0-ext,y2:y0+bh+ext,stroke:live?'var(--ink)':'var(--muted)','stroke-width':2,'stroke-dasharray':live?null:'3 3'},f.svg);
    const lab=live?M.label:`measured at ${M.T} °C`, right=xm>f.W*0.6, ly=cmp?y0-6:y0-12;
    if(!cmp){const t=CK.txt(f.svg,xm+4,ly,lab,live?'lab-strong':'tick',right&&xm>f.W-150?'end':'start'); if(right&&xm>f.W-150)t.setAttribute('x',xm-4);}
    else if(!f.narrow)CK.txt(f.svg,f.W-Rr,ly,lab,live?'lab-strong':'tick','end');}});
  CK.keynav(f,nodes);
 }});
 function upd(){fc.redraw(); const cmp=st.view==='cmp', h=st.card, pz=price(st.o,st.T,h), M=measured(h,false), J=pz.tot*st.dur, first=pz.rows[0];
  const used=st.rows.map((r,i)=>r.id&&r.p>0?{key:'r'+i,label:ENT[r.id].short,mark:'box',color:COL[i]}:null).filter(Boolean);
  CK.legend('calc-legend',cmp?[{key:'f',label:'fixed',mark:'box',color:'var(--ref)'},{key:'l',label:`leakage at ${st.T} °C`,mark:'box',color:'var(--c4)'}].concat(used)
    .concat(bars().some(b=>measured(b,true))?[{key:'m',label:'measurement',mark:'line',color:'var(--ink)'}]:[])
   :[{key:'f',label:`fixed ${f1(pz.fix)} W`,mark:'box',color:'var(--ref)'},{key:'l',label:`leakage at ${st.T} °C ${f1(pz.leak)} W`,mark:'box',color:'var(--c4)'}]
   .concat(pz.rows.map(r=>({key:'r'+r.i,label:`${r.e.short} ${f1(r.w)} W`,mark:'box',color:COL[r.i]}))).concat(M?[{key:'m',label:'measurement',mark:'line',color:'var(--ink)'}]:[]));
  if(cmp){const PZ=bars().map(b=>price(st.o,st.T,b));
   let s=`At ${st.T} °C, ${st.o==='zeros'?'on zeros':'on random data'}: `+PZ.map(q=>{const m=measured(q.h,true); return `${barName(q.h)} <b>${f1(q.tot)} W</b>${spread(q)?` [${f1(q.fix+q.leak+q.lo)}–${f1(q.fix+q.leak+q.hi)}]`:''}, ${nf(q.tot*st.dur)} J over ${CK.fmt.num(st.dur)} s`+
    (m?m.tot!=null&&Math.abs(st.T-m.T)>2?` (measured at ${m.T} °C)`:` (${m.label})`:'');}).join('; ')+'.';
   const x1=[...new Set(PZ.flatMap(q=>q.rows.filter(r=>r.e.rcard).map(r=>r.e.short)))], rc=[...new Set(PZ.flatMap(q=>q.rows.filter(r=>r.e.rcard).map(r=>r.e.rcard)))];
   s+=`<br><span class="small">Each bar is priced on its own card: that card's means and the rates it reached (the pooled bar: every pass on ${ALLC}, the mean rate)`+
    (x1.length?`; ${andList(x1)} at ${andList(rc)}'s rate on every bar, the only card ${x1.length>1?'they were':'it was'} timed on`:'')+
    `; idle: ${PZ.every(q=>q.law.card===PZ[0].law.card)?`${PZ[0].law.card}'s law on every bar, the only one fitted`:`each card's own law, and ${LAWCARD}'s for the pooled bar`}.`+
    PZ.filter(q=>q.miss.length).map(q=>` Not measured on ${cname(q.h)}, so left out of its bar: ${andList(q.miss.map(e=>e.short))}.`).join('')+
    (bars().some(b=>measured(b,true))?` The measurement is drawn on the ${PZ.filter(q=>measured(q.h,true)).length>1?'bars':'bar'} it was made on.`:'')+'</span>';
   if(st.capped)s+=' <span class="small">Instruction rows share the harts’ issue slots, so together they stop at 100%.</span>';
   ro.set(s); return;}
  /* per useful operation: every row in the first row's unit counts (a relay's read row and write row are its bytes moved) */
  const same=first?pz.rows.filter(r=>r.e.unit===first.e.unit):[], k=first&&first.e.unit==='MAC'?2:1, ops=same.reduce((a,r)=>a+k*r.rate,0), dw=same.reduce((a,r)=>a+r.w,0);
  const per=first&&ops>0?[pz.tot/ops*1e12,{MAC:first.e.id==='t:int8'?'pJ per int8 op':'pJ per FLOP',byte:'pJ per byte',instr:'pJ per instruction'}[first.e.unit],dw/ops*1e12]:null;   /* two ops per multiply-add */
  let s=`<b>${f1(pz.tot)} W</b>${spread(pz)?` [${f1(pz.fix+pz.leak+pz.lo)}–${f1(pz.fix+pz.leak+pz.hi)}]`:''} at ${st.T} °C: idle ${f1(pz.fix+pz.leak)} W (${f1(pz.fix)} fixed + ${f1(pz.leak)} leakage at the law's best fit)`+pz.rows.map(r=>` + ${f1(r.w)} W ${r.e.short}`).join('')+
   `. Over ${CK.fmt.num(st.dur)} s: <b>${nf(J)} J</b>, ${f0(100*(pz.fix+pz.leak)/pz.tot)}% of it static.`;
  if(per)s+=` That is ${CK.fmt.num(per[0])} ${per[1]} with the card's idle, ${CK.fmt.num(per[2])} of it the ${per[1].replace('pJ per ','')}s themselves.`;
  if(M){if(M.tot!=null)s+=Math.abs(st.T-M.T)<=2?` The measurement: ${f1(M.tot)} W (${M.src}).`:` The measurement (${f1(M.tot)} W) was at ${M.T} °C; move the temperature there to compare.`;
   else{const pzz=price('zeros',st.T,h), pzr=price('random',st.T,h), inb=M.over<pzz.dyn?'below the bracket':M.over>pzr.dyn?'above the bracket':'inside the bracket';
    s+=` Priced ${f1(pzz.dyn)} W on zeros … ${f1(pzr.dyn)} W on random data over idle; measured ${f1(M.over)} W (${M.src}): ${inb}.`;}}
  if(st.capped)s+=' <span class="small">Instruction rows share the harts’ issue slots, so together they stop at 100%.</span>';
  s+=`<br><span class="small">${basis(pz)}</span>`;
  ro.set(s);}
 sync(); load('fp32');
 /* text beneath: the default preset against its measurement, and the static share at 80 °C */
 const t=tRow('fp32','random'), tz=tRow('fp32','zeros'), tb=TB.fp32_randn;
 /* the largest dynamic power measured: every card's catalogue entries and tensor rows (tensor.per_card_rows) */
 const PR=D.tensor.per_card_rows||{};
 const dynList=[...CARDS.flatMap(h=>Object.entries(D.catalogue.cards[h].summary).map(([k,e])=>[e.over_idle_w.mean,k,h])),...CK.cardsIn(PR).flatMap(h=>Object.entries(PR[h]).map(([k,r])=>[r.over_idle_w,k,h]))];
 const mxe=dynList.reduce((a,b)=>b[0]>a[0]?b:a), mxd=mxe[0], sw=tb.mean*t.per_s*1e-12;
 /* what cooling from 80 to 60 C saves, over the fits in R.profile (each its own T_L), and on each card by its own law */
 const sv=R.profile?R.profile.fits.map(q=>q.A_leak_80_w*(1-Math.exp(-20/q.T_L_c))):null, cool=sv?[Math.min(...sv),Math.max(...sv)]:null;
 const PCL=R.per_card||{}, lawH=(h,T)=>{const L=PCL[h]; return L.P_fix_w+L.A_leak_80_w*Math.exp((T-80)/L.T_L_c);}, pch=CK.cardsIn(PCL).filter(h=>PCL[h].T[0]<=60&&PCL[h].T[1]>=80);
 /* cut on 27 September (TODO cut list): the law residuals and the fixed/leakage split, with the bound on the idle total
    the fits share, are stated once, in section 1 */
 $('compcap').innerHTML=`How it is priced: the idle law of section 1 at the chosen die temperature, plus each row's energy per event from sections 3–5 (the mean over ${ALLC}; the whisker spans the rows' ranges) times its rate, a fraction of what the card reached running that row alone. `+
  `With a card chosen, each row takes that card's own mean and rate, and the idle is that card's own law (${LAWCARD}'s of section 1; for ${andList(CK.cardsIn(PCL).map(cname))} the same form refitted to their version-3 idle cycles, to ${andList(CK.cardsIn(PCL).map(h=>`${f2(PCL[h].rms_w)} W rms`))}); a row timed on one card keeps that card's rate, and the line beneath the bar names the basis. "Compare cards" draws one bar per card. Instruction rows share the harts' issue slots, so together they stop at 100%; byte streams are assumed to add, which only the relay's reads and writes have tested (section 7.2). Per-instruction costs include the awake core (section 2), so two instruction rows count it twice. `+
  `The default is the dense fp32 matmul on random data: ${f1(P80)} W of idle at 80 °C and ${f1(sw)} W of multiply-adds (section 3.2's ${f2(tb.mean)} pJ per MAC at ${sci(t.per_s)} MAC/s), ${f1(P80+sw)} W, against ${f1(t.idle_w+t.over_idle_w)} W measured on ${LAWCARD} — the mean of four of the runs the ${f2(tb.mean)} pJ is built from, so this checks the arithmetic rather than the price; the flip model of section 3.2, fitted on aifoundry2, prices the same tile at ${f1((D.cards.patterns||[]).find(p=>p.values==='randn').model)} W instead of ${f1(sw)}.`;
 const st80=[LAWCARD].concat(CK.cardsIn(PCL)).map(h=>[h,h===LAWCARD?P80:lawH(h,80)]);
 $('comptext').innerHTML=`<b>At 80 °C the static power exceeds the dynamic power of every kernel measured here, on every card</b>: ${andList(st80.map(([h,v])=>`${f1(v)} W on ${cname(h)}`))} at rest, against at most ${f1(mxd)} W over idle (${mxe[1].startsWith('fp32_randn')?'the dense random matmul':mxe[1]}, on ${cname(mxe[2])}). The same matmul on zeros draws ${f1(tz.over_idle_w)} W over idle instead of ${f1(t.over_idle_w)} on ${LAWCARD}, and its measured loaded cost per flop there falls from ${f1(1e12*(t.idle_w+t.over_idle_w)/(2*t.per_s))} to ${f1(1e12*(tz.idle_w+tz.over_idle_w)/(2*tz.per_s))} pJ, almost all of it static. Cooling the die from 80 to 60 °C saves about ${f0(P80-lawAt(60))} W of ${LAWCARD}'s idle power${cool?` (${f1(cool[0])}–${f1(cool[1])} W over the e-foldings that fit)`:''}${pch.length?` and, by their own laws, ${andList(pch.map(h=>`${f1(lawH(h,80)-lawH(h,60))} W on ${cname(h)}`))}, whose version-3 idle cycles span those temperatures`:''}; under load it presumably saves as much. <b>On every card the data decides the dynamic energy and the temperature decides the rest.</b>`;
})();

/* ---------- 7.2 the relay, priced from section 4 ---------- */
(function(){
 /* The relay reads with 32 B vector loads through the L1 and writes with tensor stores; its "next shire" is shire
    s - 1 by ID. Each byte is read once and written once, so each bracket is the mean of a read row and a write row,
    zeros ... random (its data is one constant per slab). */
 const rr2=RR.relay_pj_per_byte||{};
 const zr=k=>{const z=cb(k+'/zeros'),r=cb(k+'/random'); return z&&r?[z.mean,r.mean]:null;};
 const mid=(a,b)=>[(a[0]+b[0])/2,(a[1]+b[1])/2];
 const wl=wireAt(HH,'zeros'), wh=wireAt(HH,'random'), wire=wl&&wh?[wl.mean,wh.mean]:null;
 const ts=zr('tstore/scp'), pd=mid(zr('tload/dram'),zr('tstore/dram')), l1f=zr('l1fill/stride32'), ps=l1f&&ts?mid(l1f,ts):null, ph=wire&&ts?mid(wire,ts):null;
 /* within 10% below a bracket is its low edge. The own scratchpad: the version-3 check (results/rl.json, item RL-f,
    claim energy-manual-153) put the relay's cost minus each card's own catalogue low edge at these values, pJ/B with
    99% intervals: at the edge on every card, not below it */
 const edge=(v,b)=>v<b[0]&&v>=0.9*b[0];
 const RLF=[['aifoundry2',-0.32,-0.79,0.16],['aifoundry3',-0.19,-0.50,0.13],['aifoundry1-c1',-0.18,-0.41,0.04]],sg2=v=>(v<0?'−':'+')+f2(Math.abs(v));
 const edgeTxt=x=>x[0]==='the own scratchpad'?`sits at the low edge of its bracket on every card, not below it (the version-3 check measured the relay's own-scratchpad cost minus each card's own catalogue low edge at ${andList(RLF.map(([h,m,lo,hi],i)=>`${sg2(m)}${i?'':' pJ/B'} [${sg2(lo)}, ${sg2(hi)}] on ${cname(h)}`))}, 99% intervals that include zero)`:`sits at the low edge of its bracket`;
 const inb=(v,b)=>edge(v,b)?'at its low edge':v<b[0]?'below':v>b[1]?'above':'inside';
 const M=k=>rr2[k]?rr2[k].mean:rp[k].pj_per_byte;
 $('relaycheck').innerHTML='<thead><tr><th>Where the relay keeps its intermediate</th><th class="num">priced pJ/B, zeros … random</th><th class="num">measured</th></tr></thead><tbody>'+
  `<tr><td>intermediate in DRAM</td><td class="num">${f0(pd[0])} … ${f0(pd[1])}</td><td class="num">${rr2.dram?bt(rr2.dram,f1):'<b>'+f1(rp.dram.pj_per_byte)+'</b>'} <span class="small">(${inb(M('dram'),pd)})</span></td></tr>`+
  (ps?`<tr><td>in the shire's own scratchpad</td><td class="num">${f1(ps[0])} … ${f1(ps[1])}</td><td class="num">${rr2.scp?bt(rr2.scp,f2):'<b>'+f2(rp.scp.pj_per_byte)+'</b>'} <span class="small">(${inb(M('scp'),ps)})</span></td></tr>`:'')+
  (ph?`<tr><td>in the next shire's scratchpad</td><td class="num">${f1(ph[0])} … ${f1(ph[1])}</td><td class="num">${rr2.hop?bt(rr2.hop,f2):'<b>'+f2(rp.hop.pj_per_byte)+'</b>'} <span class="small">(${inb(M('hop'),ph)})</span></td></tr>`:'')+'</tbody>';
 const V=[['DRAM',M('dram'),pd],['the next shire',M('hop'),ph],['the own scratchpad',M('scp'),ps]].filter(x=>x[2]);
 const inside=V.filter(x=>x[1]>=x[2][0]&&x[1]<=x[2][1]).map(x=>x[0]), out=V.filter(x=>!(x[1]>=x[2][0]&&x[1]<=x[2][1]));
 /* DRAM priced with the constant-operand rows instead, per card: closer to the relay's data than the zeros ... random bracket */
 const cst=CARDLIST.map(h=>{const a=cb('tload/dram/const'),b=cb('tstore/dram/const'),m=rr2.dram&&rr2.dram.per_card[h];
   return a&&b&&a.per_card[h]&&b.per_card[h]&&m?{h,p:(a.per_card[h].mean+b.per_card[h].mean)/2,m:m.mean}:null;}).filter(Boolean);
 $('relaytext').innerHTML=`No row of section 4 was derived from the relay, but the rows that price it were chosen after it was measured, so this is a consistency check with wide brackets, not a prediction. Each byte is read once and written once, so each bracket is the mean of a read row and a write row of section 4, from zeros to random data (the relay's data is one constant per slab). The relay reads with 32 B loads through the L1 and writes with tensor stores. It is priced with the 32 B L1 row of section 4.3 for its own scratchpad, the wire read of section 4.3 at ${f1(HH)} hops for the next shire, and, for DRAM, section 4.1's tensor-load row, the nearest the catalogue has. `+
  (inside.length?`${inside.join(' and ').replace(/^./,c=>c.toUpperCase())} fall${inside.length>1?'':'s'} inside ${inside.length>1?'their brackets':'its bracket'}`:'')+
  out.map(x=>`${inside.length?' and ':''}${x[0]} ${edge(x[1],x[2])?edgeTxt(x):`reads ${f0(100*Math.abs(1-x[1]/(x[1]<x[2][0]?x[2][0]:x[2][1])))}% ${x[1]<x[2][0]?'below':'above'}`}`).join('')+
  `; the adds and barriers the relay also runs are in no table.`+
  (cst.length>1?` The brackets are wide: priced instead with the constant-operand rows, DRAM comes to ${andList(cst.map((c,i)=>`${f1(c.p)}${i?'':' pJ/B'} on ${cname(c.h)} against ${f1(c.m)} measured (${sg1(100*(c.m/c.p-1)).replace(/\.\d$/,'')}%)`))}.`:'')+
  ` Section 7.1 prices the three relays with the same rows.`;
 /* the bracket chart: for each place the relay keeps its intermediate, the priced zeros ... random range, the measured
    mean, and each card's own measured mean, on a log x axis (3-150 pJ/B spans DRAM down to the own scratchpad) */
 const ROWS=[['dram','DRAM',pd],['scp','the own scratchpad',ps],['hop','the next shire',ph]].filter(x=>x[2]);
 if(ROWS.length){
  const relCards=CK.cardsIn(ROWS.reduce((s,r)=>rr2[r[0]]?s.concat(Object.keys(rr2[r[0]].per_card)):s,[]));
  const relItems=[{key:'priced',label:'priced, zeros … random',mark:'line',color:'var(--muted)'},{key:'measured',label:'measured mean',mark:'diamond',color:'var(--ink)'}].concat(CK.cardLegend(relCards));
  CK.legend('relay-legend',relItems); legendMarks('relay-legend',relItems);
  CK.frame('relaychart',{height:W=>W<600?250:220,label:'Priced range against measured energy for the relay’s three places to keep its intermediate',draw:f=>{
   const L=f.narrow?96:150,Rr=14,T=18,B=40,pitch=(f.H-T-B)/ROWS.length, x=CK.log(3,150,L,f.W-Rr), nodes=[];
   ROWS.forEach((r,i)=>{const[key,label,b]=r, y0=T+pitch*(i+0.5), m=M(key), st={stroke:'var(--muted)','stroke-width':1.5};
    CK.txt(f.svg,L-8,y0+4,f.narrow?label.replace(/^the /,''):label,'lab','end');
    CK.el('line',Object.assign({x1:x(b[0]),x2:x(b[1]),y1:y0,y2:y0},st),f.svg);
    CK.el('line',Object.assign({x1:x(b[0]),x2:x(b[0]),y1:y0-4,y2:y0+4},st),f.svg);
    CK.el('line',Object.assign({x1:x(b[1]),x2:x(b[1]),y1:y0-4,y2:y0+4},st),f.svg);
    const meas=mark(f,f.svg,'polygon',{points:`${x(m)},${y0-5} ${x(m)+5},${y0} ${x(m)},${y0+5} ${x(m)-5},${y0}`,fill:'var(--ink)'},9,
     `${label}: priced ${f1(b[0])}–${f1(b[1])} pJ/B (zeros … random), measured <b>${f1(m)}</b> pJ/B (${inb(m,b)})`);
    nodes.push(meas);
    const pc=(rr2[key]&&rr2[key].per_card)||{};
    CK.cardsIn(pc).forEach((h,j)=>nodes.push(cmark(f,f.svg,h,x(pc[h].mean),y0+10+7*j,3.5,7,`${label}, ${cname(h)}: <b>${f1(pc[h].mean)}</b> ± ${f2(pc[h].se||0)} pJ/B (n = ${pc[h].n})`)));
   });
   [3,10,30,100,150].forEach(t=>{CK.el('line',{x1:x(t),x2:x(t),y1:T-4,y2:f.H-B,class:'grid-line'},f.svg); CK.txt(f.svg,x(t),f.H-B+16,CK.fmt.num(t),'tick','middle');});
   CK.txt(f.svg,(L+f.W-Rr)/2,f.H-4,'pJ per byte (log)','lab','middle');
   CK.keynav(f,nodes);
  }});
  $('relaychartcap').textContent=`Bracket: the priced range of the table above, zeros to random data. Black diamond: the measured mean. Below it: each card's own mean, in the card's colour and mark.`;
 }
})();

/* ---------- 8. three cards: the ratio against the value (em-l2) ---------- */
(function(){
 /* every other card against the reference card (CARDS[0], aifoundry2), entry by entry; one series per card in its registry
    colour and mark */
 const REF=CARDS[0], SR=SUMM(REF), OC=CARDS.slice(1).filter(h=>Object.keys(SUMM(h)).length); if(!OC.length)return;
 const pts=[]; OC.forEach(h=>{const Sh=SUMM(h); for(const k in SR){const r2=SR[k],r3=Sh[k]; if(!r3)continue; const byte=r2.bytes_per_s.mean>0, fld=byte?'pj_per_byte':'pj_per_op';
  if(r2[fld].mean>0&&r3[fld].mean>0)pts.push({h,k,byte,v2:r2[fld].mean,v3:r3[fld].mean,s2:r2[fld].se,s3:r3[fld].se,r:r3[fld].mean/r2[fld].mean});}});
 const SEC={relay_pj_per_byte:['relay (section 5)','pJ/B'],hotline_nj_per_op:['hot line (section 6)','nJ'],rings_pj_per_byte:['ring (section 5)','pJ/B'],levels_pj_per_byte:['level (section 4.2)','pJ/B']};
 const rer=[]; Object.keys(SEC).forEach(sec=>{const o=RR[sec]||{}; for(const k in o){const v=o[k]; if(!v||!v.per_card[REF])continue;
  OC.forEach(h=>{if(v.per_card[h])rer.push({h,k,sec,v2:v.per_card[REF].mean,v3:v.per_card[h].mean,r:v.per_card[h].mean/v.per_card[REF].mean});});}});
 const XC=D.catalogue.cross_cards||{}, lo=0.7, hi=Math.max(1.3,Math.ceil(10*Math.max(...pts.map(p=>p.r),...rer.map(p=>p.r)))/10);
 CK.legend('cards-legend',OC.map(h=>cardItem(h,`${cname(h)}: median ${XC[h]?f3(XC[h].median):'—'} (dashed: 10–90%)`)).concat([{key:'eq',label:'equal to aifoundry2',mark:'line',color:'var(--axis)'}]));
 legendMarks('cards-legend',OC.map(h=>cardItem(h,'')));
 const tipP=p=>`<b>${p.k}</b> (${p.byte?'per byte':'per instruction'})<br>${cname(REF)} ${fs(p.v2)} ± ${fs(p.s2)}, ${cname(p.h)} ${fs(p.v3)} ± ${fs(p.s3)} ${p.byte?'pJ/B':'pJ'}<br>ratio <b>${f3(p.r)}</b>`;
 const tipR=p=>`<b>${SEC[p.sec][0]}: ${p.k}</b><br>${cname(REF)} ${fs(p.v2)}, ${cname(p.h)} ${fs(p.v3)} ${SEC[p.sec][1]}<br>ratio <b>${f3(p.r)}</b>`;
 CK.frame('cards',{height:W=>W<600?320:360,label:`Every catalogue entry: ${andList(OC.map(cname))} as a fraction of ${REF}`,draw:f=>{
  const SW=f.narrow?58:84, L=40,Rr=10,T=24,B=40, xR=f.W-Rr-SW-10, x=CK.log(1,2000,L,xR), y=CK.lin(lo,hi,f.H-B,T);
  CK.axes(f,{x,y,L,R:Rr+SW+10,T,B,yt:[0.7,0.8,0.9,1,1.1,1.2,1.3,1.4,1.5,1.6].filter(v=>v<=hi+1e-9),yfmt:v=>f1(v),xl:`${REF}, pJ per instruction or per byte (log)`,yl:`card / ${REF}`});
  CK.el('line',{x1:L,x2:f.W-Rr,y1:y(1),y2:y(1),stroke:'var(--axis)','stroke-width':1},f.svg);
  OC.forEach(h=>{const c=CK.card(h).color, q=XC[h]; if(!q)return;
   CK.el('line',{x1:L,x2:xR,y1:y(q.median),y2:y(q.median),stroke:c,'stroke-width':1.8},f.svg);
   [q.p10,q.p90].forEach(v=>CK.el('line',{x1:L,x2:xR,y1:y(v),y2:y(v),stroke:c,'stroke-width':1,'stroke-dasharray':'4 3'},f.svg));});
  const cl=v=>Math.max(lo,Math.min(hi,v));
  OC.forEach(h=>{const nodes=pts.filter(p=>p.h===h).sort((a,b)=>a.v2-b.v2).map(p=>cmark(f,f.svg,h,x(Math.max(1,p.v2)),y(cl(p.r)),2.6,6,tipP(p))); CK.keynav(f,nodes);});
  /* the reruns: their x (pJ/B, nJ) is not comparable, so they get a strip of their own on the same ratio axis */
  const x0=f.W-Rr-SW, cx=x0+SW/2, placed=[];
  CK.el('line',{x1:x0,x2:x0,y1:T,y2:f.H-B,stroke:'var(--axis)'},f.svg);
  CK.txt(f.svg,cx,f.H-B+16,'reruns','tick','middle');
  const rn=rer.slice().sort((a,b)=>a.r-b.r).map(p=>{const cy=y(cl(p.r)); let o=0; for(let k=0;k<40;k++){o=(k%2?1:-1)*Math.ceil(k/2)*7; if(placed.every(q=>(q.o-o)**2+(q.cy-cy)**2>=49))break;} placed.push({o,cy});
   return cmark(f,f.svg,p.h,cx+Math.max(-SW/2+5,Math.min(SW/2-5,o)),cy,3,6,tipR(p));});
  CK.keynav(f,rn);
 }});
 const med=v=>{v=v.slice().sort((a,b)=>a-b); return v.length%2?v[v.length>>1]:(v[v.length/2-1]+v[v.length/2])/2;};
 const DB=D.catalogue.die_c_busy_median, CAT3=V3.catalogue||{}, GAP=CAT3.gap_vs_a2||{}, TP=CAT3.temperature||{}, CB_=CAT3.cool_a3_warm_a2, OUTL=D.catalogue.scale_outliers||{}, C23=CAT3.committed_23sep, CL=VI.clocks||{}, X5=V3.x5||{}, PR=D.tensor.per_card_rows||{};
 const rng=h=>{const r=pts.filter(p=>p.h===h).map(p=>p.r); return [Math.min(...r),Math.max(...r)];};
 const kind=(h,b)=>med(pts.filter(p=>p.h===h&&p.byte===b).map(p=>p.r));
 const tIn=CK.cardsIn(TP).filter(h=>TP[h].decision==='temperature'), tNo=CK.cardsIn(TP).filter(h=>TP[h].decision!=='temperature');
 const bci=b=>`${sgw(b.beta)}% per °C [${sgw(b.lo)}, ${sgw(b.hi)}]`;
 const xr=CK.cardsIn(X5).filter(h=>X5[h]&&X5[h].fp32_randn&&X5[h].fp32_randn.ci[0]>0);
 $('cardscap').innerHTML=`${XC[OC[0]]?XC[OC[0]].n:pts.length/OC.length} entries, each the mean of three passes on each card (26 September)${DB?`, the bursts at a median die temperature of ${andList(CARDS.filter(h=>DB[h]!=null).map(h=>`${f0(DB[h])} °C on ${cname(h)}`))}`:''}. `+
  semiList(OC.map(h=>`${cname(h)} / ${REF}: median ${f3(XC[h].median)}, 10th–90th percentile ${f3(XC[h].p10)}–${f3(XC[h].p90)}, range ${f2(rng(h)[0])}–${f2(rng(h)[1])}; per instruction ${f3(kind(h,false))} and per byte ${f3(kind(h,true))} in the median`))+
  `. Solid lines: each card's median; dashed: its 10th and 90th percentiles; the line at 1 is equality. `+
  (OC.every(h=>OUTL[h])?`Against each card's common scale, once the ${OUTL[OC[0]].entries} comparisons are allowed for, ${andList(OC.map(h=>OUTL[h].outliers.length?`${WORD[OUTL[h].outliers.length]||OUTL[h].outliers.length} entr${OUTL[h].outliers.length>1?'ies':'y'} on ${cname(h)} (${andList(OUTL[h].outliers.map(o=>`<code>${o.cfg}</code> ${f2(o.vs_scale)}×`))})`:`no entry on ${cname(h)}`))} differ beyond the noise of three passes (99%, Bonferroni). `:'')+
  (Object.keys(GAP).length?`Taken pass by pass over the whole catalogue, the version-3 check puts ${andList(CK.cardsIn(GAP).filter(h=>GAP[h]).map(h=>`${cname(h)} at ${f3(GAP[h].ratio)} [${f3(GAP[h].lo)}, ${f3(GAP[h].hi)}]`))} of ${REF} (99% intervals)${C23?`; the 23 September catalogue, which this one replaces, gave ${f3(C23.median)} for aifoundry3`:''}. `:'')+
  (rer.length?`The ${rer.length} rerun entries of sections 4.2, 5 and 6 (right, their energies in their own units) do not share the catalogue's scale: ${andList(OC.map(h=>{const r=rer.filter(p=>p.h===h).map(p=>p.r); return r.length?`${cname(h)} ${f3(med(r))} in the median (${f2(Math.min(...r))}–${f2(Math.max(...r))})`:null;}).filter(Boolean))}${OC.some(h=>rer.some(p=>p.h===h&&p.sec==='hotline_nj_per_op'))?'':'; the hot line has aifoundry2 and aifoundry3 only (23 September)'}. `:'')+
  `<b>What sets the scale.</b> `+(tIn.length?`The energy per operation rises with die temperature on ${andList(tIn.map(h=>`${cname(h)}, ${bci(TP[h].beta_pct_per_c)}`))}${tNo.length?`, and not resolved on ${andList(tNo.map(h=>`${cname(h)}, ${bci(TP[h].beta_pct_per_c)}`))}`:''} (a 30-entry panel run hot and cool on each card, 6–14 °C apart; 99% intervals): enough to account for aifoundry3's gap, its die ${DB&&DB.aifoundry3!=null?f0(DB[REF]-DB.aifoundry3)+' °C':'some 15 °C'} cooler here, so that aifoundry3 itself differs from ${REF} is not established. `:'')+
  (TP.aifoundry2&&TP.aifoundry2.hot_c!=null?`The hot passes held aifoundry2's die at ${f0(TP.aifoundry2.hot_c)} °C in the mean; the hottest (26 September) read 90–103 °C, above the 90 °C at which this work's long runs stop, with 106 °C on the hottest sensor, all at 600 MHz: nothing on the card limits the die's temperature (<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature#a-load-step-seen-through-every-sensor">Power and temperature, §2</a>). `:'')+
  (CB_?`With aifoundry3 cool and aifoundry2 warm, as here, the panel gives ${f3(CB_.ratio)} [${f3(CB_.lo)}, ${f3(CB_.hi)}]. `:'')+
  (xr.length?`Switching power itself follows the die: the random-data fp32 matmul drew ${andList(xr.map(h=>`${sg1(X5[h].fp32_randn.hot_minus_cool_w)} W [${sg1(X5[h].fp32_randn.ci[0])}, ${sg1(X5[h].fp32_randn.ci[1])}] more on ${cname(h)} launched at ${f0(X5[h].launch_c.hi)} than at ${f0(X5[h].launch_c.lo)} °C`))}. `:'')+
  (()=>{const RM=D.catalogue.rail_mv||{}, rh=CK.cardsIn(RM); if(rh.length<2||!RM[REF])return '';
    const v2=(h,k)=>100*((RM[h][k]/RM[REF][k])**2-1), dir=v=>`${f0(Math.abs(v))}% ${v>0?'more':'less'}`;
    return `The minion rail runs at ${andList(rh.map(h=>`${f0(RM[h].minion)}`))} mV and the SRAM rail at ${andList(rh.map(h=>`${f0(RM[h].sram)}`))} mV on ${andList(rh.map(cname))} (the catalogue's median readings). By V² alone that would make ${semiList(rh.filter(h=>h!==REF).map(h=>`${cname(h)}'s instructions cost ${dir(v2(h,'minion'))} and its SRAM accesses ${dir(v2(h,'sram'))}`))}: the voltage does not explain aifoundry3's scale, and is in line with aifoundry1 card 1's cheaper instructions and dearer bytes (${f3(kindMed('aifoundry1-c1',false))} and ${f3(kindMed('aifoundry1-c1',true))} in the median), which its cooler die would not explain. `;})()+
  (CK.cardsIn(PR).length>1&&PR[REF]&&PR[REF].fp32_randn?`The tensor unit's random-data fp32 switching power, launched at each card's own temperature (section 3.2), is ${andList(CK.cardsIn(PR).filter(h=>h!==REF&&PR[h].fp32_randn).map(h=>`${f3(PR[h].fp32_randn.over_idle_w/PR[REF].fp32_randn.over_idle_w)} on ${cname(h)}`))} of ${REF}'s`+
   (CK.cardsIn(LO).length>1&&atL(REF,'fp32_randn')!=null?` as registered, and ${andList(CK.cardsIn(LO).filter(h=>h!==REF&&atL(h,'fp32_randn')!=null).map(h=>rng2(atL(h,'fp32_randn')/atL(REF,'fp32_randn'),atLs(h,'fp32_randn')!=null&&atLs(REF,'fp32_randn')!=null?atLs(h,'fp32_randn')/atLs(REF,'fp32_randn'):null,f3)))} at the die temperature of each launch (the launch-temperature offset of note C2, section 3.2, over its two readings of the launch temperature)`:'')+
   `. These are ratios of one configuration's switching power; the flip model's single scale for aifoundry3, a different quantity fitted to the model over the Horace patterns, was ${f3(D.cards&&D.cards.scale||0.924)} in the 22 September transfer.`:'');
})();

/* ---------- E48: gathers, scatters and packed atomics (3.1's last table, 4.3's patterns, 4.4, 6's rows) ----------
   D.gs is build_energy_manual.py gs_block(): every configuration pooled over every pass of every card (pj_per_element,
   elements_per_s, cpi_minion, pj_per_line, line_bytes_per_s: {mean, lo, hi, n, per_card}), cat_pj_per_element over the
   catalogue's cards only (aifoundry2 and aifoundry3: E48's rule for rows set beside the catalogue), and the rows every
   page draws (levels, l1_rows, updates, patterns, from tools/ettelem/gs_levels.py). "Random" is random lines within
   4 KB tiles (D.gs.random), never uniform addresses. */
const GS=D.gs||null;
const gsK=GS?GS.configs:{};
const gsCfg=(op,table,o)=>{o=o||{}; return `gs/${o.s||'E'}/${op}/${table}/${o.p||'rand'}/${o.d||'random'}/h${o.h||2}/m${o.m||'ff'}/n${o.n||'1024'}`;};
const gsGet=(op,table,o)=>gsK[gsCfg(op,table,o)]||null;
const gsCards=GS?CK.cardsIn(GS.cards):[];
const gsN=GS?WORD[gsCards.length]||gsCards.length:'';
/* a rate per second: "452 G/s", "27.4 G/s", "1.19 G/s", "422 M/s" (u: the unit after G or M) */
const gsRate=(v,u)=>{u=u==null?'/s':u; if(v==null)return '—'; const g=v/1e9; return g>=100?`${nf(g)} G${u}`:g>=10?`${f1(g)} G${u}`:g>=1?`${f2(g)} G${u}`:`${nf(v/1e6)} M${u}`;};
/* an energy in pJ: pJ below 1,000 (one decimal from 10), nJ above */
const gsE=v=>v==null?'—':v>=1000?`${f1(v/1000)} nJ`:`${v>=10?f1(v):f2(v)} pJ`;
const gsBar=c=>{if(!c)return '—'; const nj=c.mean>=1000, s=nj?1000:1, g=nj?(c.mean>=10000?f1:f2):(c.mean>=10?f1:f2);
 return `<b>${g(c.mean/s)}</b> <span class="small">[${g(c.lo/s)}–${g(c.hi/s)}]</span> ${nj?'nJ':'pJ'}`;};
const gsPer=(c,k)=>{if(!c)return '—'; k=k||1; const nj=c.mean*k>=1000, s=nj?1000:1, g=v=>nj?f2(v):v>=10?f1(v):f2(v);
 return CK.cardsIn(c.per_card).map(h=>`${cshort(h)} ${g(c.per_card[h].mean*k/s)} ± ${more(c.per_card[h].se*k/s,g)}`).join('<br>')+(nj?' nJ':'');};
/* the energy manual's contiguous path for a level, per 4 B (sections 4.1, 4.2) */
const gsStream=l=>{if(!l.stream)return null; const [k,key]=l.stream;
 if(k==='cat'){const c=CB[key]; return c?c.mean*(key.indexOf('flw.ps')===0?4/32:4):null;}
 if(k==='lv'){const c=(RR.levels_pj_per_byte||{})[key]; return c?c.mean*4:null;}
 const c=((RR.levels_by_contents_pj_per_byte||{}).random||{})[key]; return c?c.mean*4:null;};

/* 3.1: from the L1, per instruction and per element; the bold figure pools the catalogue's cards (aifoundry2, aifoundry3) */
(function(){
 if(!GS||!$('gsl1tab'))return;
 const cat=CK.cardsIn(GS.catalogue_cards), rest=gsCards.filter(h=>!cat.includes(h));
 const pb=(c,k)=>{if(!c)return '—'; const g=c.mean*k>=10?f1:f2; return `<b>${g(c.mean*k)}</b> <span class="small">[${g(c.lo*k)}–${g(c.hi*k)}]</span>`;};
 const rows=GS.l1_rows.map(r=>{const e=gsK[r.cfg], z=r.zeros?gsK[r.zeros]:null; if(!e||!e.cat_pj_per_element)return '';
  const k=e.per_instr, rc=e.cat_pj_per_element, zc=z&&z.cat_pj_per_element, iss=1/(2*e.cpi_minion.mean), at=r.zeros?'element':'update';
  const zeroOnly=!r.zeros;
  return `<tr><td><code>${r.op}</code> <span class="small">${r.label}</span></td><td class="num">${zeroOnly?pb(rc,k)+`<br><span class="small">${f1(rc.mean)} per ${at}</span>`:zc?pb(zc,k)+`<br><span class="small">${f1(zc.mean)} per element</span>`:'—'}</td>`+
   `<td class="num">${zeroOnly?'—':pb(rc,k)+`<br><span class="small">${f1(rc.mean)} per element</span>`}</td><td class="num">${zc?f2(rc.mean/zc.mean)+'×':'—'}</td>`+
   `<td class="num">${iss<0.01?iss.toPrecision(2):f3(iss)}</td><td class="num small">${gsPer(e.pj_per_element,k)}${zeroOnly?' (zeros)':''}</td></tr>`;}).join('');
 $('gsl1tab').innerHTML=`<thead><tr><th>Instruction</th><th class="num">zeros pJ per instruction, ${andList(cat.map(cname))}</th><th class="num">random pJ per instruction, ${andList(cat.map(cname))}</th><th class="num">random / zeros, ${andList(cat.map(cname))}</th><th class="num">issue per hart per cycle</th><th class="num" data-nosort>per card, per instruction ± se</th></tr></thead><tbody>${rows}</tbody>`;
 const g1=gsGet('fgw.ps','dram-512B'), b1=gsGet('fg32w.ps','dram-512B'), s1=gsGet('fscw.ps','dram-512B'), fl=gsGet('flw','dram-512B');
 const nops=new Set(Object.values(gsK).map(c=>c.op).filter(o=>!['flw','fsw','amoaddl.w','amoaddg.w','upd'].includes(o))).size;
 if(!(g1&&b1&&s1&&fl))return;
 $('gsl1text').innerHTML=`<b>Gathers and scatters</b> (E48, ${nops} more instructions measured on the same ${gsN} cards after the catalogue, 26 September). Pooled over the ${gsN} cards, from the L1 a word gather <code>fgw.ps</code> costs `+
  `${f1(g1.pj_per_element.mean*8)} pJ an instruction, ${f1(g1.pj_per_element.mean)} per element, about what a scalar <code>flw</code> on the same addresses costs (${f1(fl.pj_per_element.mean)} pJ), `+
  `and issues its eight elements in ${f1(g1.cpi_minion.mean)} minion-cycles; a scatter <code>fscw.ps</code> ${f1(s1.pj_per_element.mean)} pJ an element; the 32 B-block form <code>fg32w.ps</code>, one access per instruction, ${f1(b1.pj_per_element.mean)} pJ an element at ${f1(b1.elements_per_s.mean/g1.elements_per_s.mean)}× the rate. `+
  `The table's bold figures pool ${andList(cat.map(cname))}'s passes, as E48's rules, fixed before its data, pool rows set beside this catalogue${g1.cat_pj_per_element?` (the word gather: ${f1(g1.cat_pj_per_element.mean)} pJ an element there, ${f1(g1.pj_per_element.mean)} over all ${gsN} cards)`:''}; ${andList(rest.map(cname))} is in the per-card column. `+
  `The same instructions from the L2, the scratchpads and DRAM are in <a href="#irregular-access-gathers-and-scatters-by-level">section 4.4</a>, and the packed atomics on shared tables in <a href="#synchronisation">section 6</a>.`;
})();

/* 4.3: the pattern sweep split into a cost per line and per instruction; masks, element sizes, conflicts, scaling */
(function(){
 if(!GS||!$('gspattab'))return;
 const pts=[], rows=GS.patterns.map(([p,lab])=>{const a1=gsGet('fgw.ps','dram-512B',{p}), a2=gsGet('fgw.ps','dram-4K',{p});
  const r1=gsGet('fgw.ps','dram-512B',{p,h:1,n:'M1',s:'R'}), r2=gsGet('fgw.ps','dram-4K',{p,h:1,n:'M1',s:'R'}); if(!(a1&&a2))return '';
  const pji=a2.pj_per_element.mean*a2.per_instr; pts.push([a2.lines_per_instr,pji]);
  const cy=(r,a)=>`${r?f1(r.cpi_minion.mean):'—'} / ${f1(a.cpi_minion.mean)}`;
  return `<tr><td>${lab} <span class="small">(<code>${p}</code>)</span></td><td class="num">${cy(r1,a1)}</td><td class="num">${f1(a1.pj_per_element.mean)}</td><td class="num">${f1(a2.lines_per_instr)}</td><td class="num">${cy(r2,a2)}</td><td class="num">${f1(a2.pj_per_element.mean)}</td><td class="num">${f0(pji)}</td><td class="num">${f0(a2.pj_per_line.mean)}</td></tr>`;}).join('');
 $('gspattab').innerHTML='<thead><tr><th>Pattern</th><th class="num">L1: cycles an instruction, 1 minion / 1,024</th><th class="num">L1: pJ per element</th><th class="num">L2: lines an instruction</th><th class="num">L2: cycles an instruction, 1 minion / 1,024</th><th class="num">L2: pJ per element</th><th class="num">L2: pJ an instruction</th><th class="num">L2: pJ per line</th></tr></thead><tbody>'+rows+'</tbody>';
 if(pts.length<3)return;
 const ft=lfit(pts), z32=CB['l1fill/stride32/random'], z64=CB['l1fill/stride64/random'], fill=z32&&z64?2*32*(z64.mean-z32.mean):null;
 const sp=CARDS.map(h=>SUMM(h)['spin/zeros/h2']).filter(Boolean).map(r=>r.over_idle_w.mean), pw=sp.length?sp.reduce((a,b)=>a+b,0)/sp.length/1024:null;
 const r8=gsGet('fgw.ps','dram-4K'), cyl=r8?r8.cpi_minion.mean/r8.lines_per_instr:null, awk=pw&&cyl?pw/0.6e9*cyl*1e12:null;
 const m=['ff','0f','01'].map(k=>[k,gsGet('fgw.ps','dram-512B',{m:k}),gsGet('fgw.ps','dram-4K',{m:k})]), ln={ff:8,'0f':4,'01':1};
 const es=['fgw.ps','fgh.ps','fgb.ps'].map(o=>[o,gsGet(o,'dram-512B'),gsGet(o,'dram-4K')]);
 const bw=gsGet('fgw.ps','dram-512B',{p:'bcast'}), bs=gsGet('fscw.ps','dram-512B',{p:'bcast'}), g1=gsGet('fgw.ps','dram-512B'), s1=gsGet('fscw.ps','dram-512B');
 const wins=[...new Set(Object.values(GS.checks).flatMap(c=>Object.values(c.winners_by_op||{}).flatMap(o=>Object.keys(o))))];
 $('gspattext').innerHTML=`<b>Gathers: a line's cost and an element's</b> (E48, the table below). From the L1 the pattern of a gather's eight addresses does not matter: every pattern issues in about ${f1(g1.cpi_minion.mean)} minion-cycles an instruction. `+
  `<b>From the L2 the time and the energy follow the lines, not the elements</b>: fitted over the seven patterns, an instruction costs <b>${f0(ft.a)} pJ plus ${f0(ft.b)} pJ per line it fetches</b> (random data). An instruction whose lanes fall on one or two lines takes about one L2 latency, consecutive, permuted, strided or all on one word alike, because a minion's two miss handlers fetch two lines at once; eight lines take four rounds, and the whole chip runs each minion at about the rate one minion reaches alone. `+
  (fill&&awk?`The ${f0(ft.b)} pJ per line is about a line's fill into the L1 (${f0(fill)} pJ on random data, the line-fill table above) plus the awake minion for the ${f1(cyl)} cycles each line takes (${f1(pw*1e3)} mW with both harts, section 2: ${f0(awk)} pJ), ${f0(fill+awk)} pJ together. `:'')+
  (m.every(x=>x[1]&&x[2])?`<b>A masked lane still takes its issue slot</b> in the L1 (${m.map(x=>f1(x[1].cpi_minion.mean)).join(' / ')} cycles an instruction with 8 / 4 / 1 lanes active, ${m.map(x=>f0(x[1].pj_per_element.mean*ln[x[0]])).join(' / ')} pJ), while from the L2 the time follows the active lanes' lines (${m.map(x=>f1(x[2].cpi_minion.mean)).join(' / ')} cycles). `:'')+
  (es.every(x=>x[1]&&x[2])?`<b>Bytes and halfwords cost what words cost</b> per element (${es.map(x=>`<code>${x[0]}</code> ${f1(x[1].pj_per_element.mean)} and ${f0(x[2].pj_per_element.mean)} pJ`).join(', ')} from the L1 and the L2), so per useful byte a byte gather is four times a word gather. `:'')+
  (bw&&bs?`<b>Eight lanes on one word</b> cost ${f1(bw.pj_per_element.mean)} pJ per gathered element from the L1 against ${f1(g1.pj_per_element.mean)} for random words (${f1(bs.pj_per_element.mean)} against ${f1(s1.pj_per_element.mean)} scattered), and when all eight lanes scatter to one word, lane ${wins.join(', ')}'s value remains, every time on every card.`:'');
 const sc=[['the L1','dram-512B'],['the L2','dram-4K'],['the own scratchpad','scp-16K'],['a scratchpad 2 hops away','rscp-16K']].map(([lab,t])=>{const o=gsGet('fgw.ps',t,{n:'M1',s:'R'}), sh=gsGet('fgw.ps',t,{n:'S32',s:'R'}), fu=gsGet('fgw.ps',t);
  return o&&fu?`${lab} ${f1(o.elements_per_s.mean*1024/1e9)} G/s from one minion's rate (both harts)${sh?`, ${f1(sh.elements_per_s.mean*32/1e9)} from one full shire's`:''}, ${f1(fu.elements_per_s.mean/1e9)} measured`:null;}).filter(Boolean);
 $('gspatnote').innerHTML=`Word gathers <code>fgw.ps</code> on random data, from a 512 B table per hart (the L1) and a 4 KB one (the L2), with one minion's hart 0 alone (one pass per card of the rate block, three on each card) and with both harts of all 1,024 minions; energy at 1,024 minions only (one minion's is under the meter's reach). Every figure pools the ${gsN} cards. `+
  (sc.length?`Times 1,024 minions (or 32 shires), one minion's rate predicts the chip's: ${sc.join('; ')}. From DRAM the one-minion and spread runs are no test: their 256 KB tables per hart fit in the L2 and L3.`:'');
})();

/* 4.4: irregular access by level: a dot plot per level, energy per element or rate, gathers, scatters and the scalar load */
(function(){
 if(!GS||!$('gslevels'))return;
 const LV=GS.levels.filter(l=>Object.keys(l.cols).some(c=>gsK[l.cols[c]]));
 const SER=[['gather','gather fgw.ps'],['gather_lg','gather past the L1 (fgwl.ps, fgwg.ps)'],['scatter','scatter fscw.ps'],['scatter_lg','scatter past the L1 (fscwl.ps, fscwg.ps)'],['load','scalar flw, same addresses']];
 const st={metric:'pj',card:'pooled'};
 const v=(e,card)=>{const c=e&&(st.metric==='pj'?e.pj_per_element:e.elements_per_s); if(!c)return null; if(card==null||card==='pooled')return {mean:c.mean,lo:c.lo,hi:c.hi,n:c.n,cards:c.cards};
  const p=CK.pick(c,card); return p?{mean:p.mean,lo:p.se!=null?p.mean-p.se:p.mean,hi:p.se!=null?p.mean+p.se:p.mean,se:p.se,n:p.n,cards:1}:null;};
 const fmt=x=>st.metric==='pj'?gsE(x):gsRate(x);
 const ro=CK.readout('gs-readout');
 const tip=(l,s,e)=>()=>{const x=v(e,st.card), pj=e.pj_per_element, r=e.elements_per_s, sp=gsStream(l);
  return `<b>${l.label}</b>, ${s[1]}: <code>${e.op}</code><br>${pj?`${gsE(pj.mean)} per element [${gsE(pj.lo)}–${gsE(pj.hi)}] over ${pj.n} passes`:'energy not kept'}, ${gsRate(r.mean,' elements/s')}`+
   (pj&&pj.cards<gsCards.length?`<br>energy on ${andList(CK.cardsIn(pj.per_card).map(cname))} only: the clock rule dropped the other cards' bursts`:'')+
   (pj?`<br>${CK.cardsIn(pj.per_card).map(h=>`${cshort(h)} ${gsE(pj.per_card[h].mean)} ± ${gsE(pj.per_card[h].se)}`).join(' · ')}`:'')+
   (sp&&st.metric==='pj'?`<br>streamed from the same level: ${gsE(sp)} per 4 B`:'')+`<br>table: ${l.table}`;};
 CK.seg('gs-metric',{label:'Show',options:[['pj','pJ per element'],['rate','elements per second']],value:'pj',onChange:k=>{st.metric=k; fr.redraw(); cap();}});
 CK.cardSeg('gs-card',{cards:gsCards,pooled:true,label:'card',onChange:k=>{st.card=k; fr.redraw(); cap();}});
 const lg=CK.legend('gs-legend',SER.map(([k,lab],i)=>({key:k,label:lab,color:CK.color(i),mark:'dot'})).concat([{key:'stream',label:'the level read contiguously, per 4 B',color:'var(--ref)',mark:'line'}]),{toggle:true,onChange:on=>CK.showSeries(fr,on)});
 const NAR=W=>W<600, rowH=W=>NAR(W)?56:40;
 const fr=CK.frame('gslevels',{height:W=>30+LV.length*rowH(W)+40,label:'A random 4-byte element by memory level: energy per element or elements per second, for gathers, scatters and scalar loads',draw:f=>{
  const W=f.W, nar=NAR(W), L=nar?10:150, Rr=16, T=30, rh=rowH(W), bot=T+LV.length*rh;
  const lo=st.metric==='pj'?2:2e8, hi=st.metric==='pj'?5e4:2e12, x=CK.log(lo,hi,L,W-Rr);
  const ax=CK.el('g',{'aria-hidden':'true'},f.svg), tk=x.ticks(nar?4:7);
  tk.forEach(t=>{CK.el('line',{x1:x(t),x2:x(t),y1:T-4,y2:bot,class:'grid-line'},ax); CK.txt(ax,x(t),bot+16,st.metric==='pj'?gsE(t).replace('.0 ',' '):t<1e9?`${nf(t/1e6)} M/s`:`${nf(t/1e9)} G/s`,'tick','middle');});
  CK.txt(ax,(L+W-Rr)/2,f.H-6,st.metric==='pj'?'energy per element above idle, random data (log)':'elements per second over the chip, 1,024 minions (log)','lab','middle');
  const layer=CK.el('g',{},f.svg), nodes=[];
  LV.forEach((l,i)=>{const y0=T+i*rh, cy=nar?y0+30:y0+rh/2;
   if(i)CK.el('line',{x1:0,x2:W,y1:y0,y2:y0,stroke:'var(--grid)','stroke-dasharray':'2 3'},ax);
   CK.txt(layer,nar?L:4,nar?y0+13:cy+4,l.label,'lab','start');
   const sp=gsStream(l); if(sp&&st.metric==='pj'){const g=CK.el('g',{'data-series':'stream'},layer); CK.el('line',{x1:x(sp),x2:x(sp),y1:cy-12,y2:cy+12,stroke:'var(--ref)','stroke-width':2.5},g);
    CK.tip(f,g,`<b>${l.label}</b>: the level read contiguously, ${gsE(sp)} per 4 B (sections 4.1 and 4.2)`); nodes.push(g);}
   SER.forEach(([k,lab],si)=>{const e=gsK[l.cols[k]]; const c=v(e,st.card); if(!c)return; const oy=cy+(si-2)*(nar?4.5:5);
    const g=CK.el('g',{'data-series':k},layer), col=CK.color(si);
    if(c.hi>c.lo)CK.el('line',{x1:x(Math.max(lo,c.lo)),x2:x(Math.min(hi,c.hi)),y1:oy,y2:oy,stroke:col,'stroke-width':1.5},g);
    CK.el('circle',{cx:x(c.mean),cy:oy,r:8,class:'ck-hit'},g);
    const dot=CK.el('circle',{cx:x(c.mean),cy:oy,r:4},g); dot.style.fill=col; if(c.cards<gsCards.length&&st.card==='pooled'){dot.style.fill='var(--surface)'; dot.style.stroke=col; dot.style.strokeWidth='2';}
    CK.tip(f,g,tip(l,[k,lab],e)); g.addEventListener('focus',()=>ro.set(tip(l,[k,lab],e)())); nodes.push(g);});
  });
  CK.keynav(f,nodes);
 }});
 CK.showSeries(fr,lg.on);
 const cap=()=>{$('gscap').innerHTML=`Both harts of all 1,024 minions issue the instruction back to back, each hart on a table of its own sized to the level (the table's size per hart is in each tooltip), eight random words on eight lines of a 4 KB tile per instruction (random lines within 4 KB tiles, the tiles in a scrambled order: not uniform addresses). `+
  `${st.card==='pooled'?`Dots are the mean over every pass on ${ALLC}, bars the range of those passes`:`Dots are ${cname(st.card)}'s mean, bars ± its pass-to-pass standard error`}; a hollow dot rests on fewer cards (the 64 KB table: the clock rule dropped aifoundry2's and aifoundry1 card 1's bursts). `+
  `In the energy view the grey tick is the same level read contiguously, per 4 B: the L1 row of section 4.1, the levels of 4.2, DRAM's tensor load. Energy is card power above idle over the chip's element rate, E48, three passes on each of ${gsN} cards (26 September).`;};
 cap();
 /* the table: every level and column, with each card */
 const cols=GS.columns;
 /* compact cells: the pooled mean, the range of the passes and the rate; each card's mean in the second table */
 const rngs=c=>{const nj=c.mean>=1000, g=v=>nj?f1(v/1000):f0(v); return `[${g(c.lo)}–${g(c.hi)}]`;};
 $('gstab').innerHTML=`<thead><tr><th>Level</th>${cols.map(c=>`<th class="num">${c[1].replace(/ \(.*\)$/,'').replace(/, same offsets/,'').replace(/`([^`]+)`/g,'<code>$1</code>')}</th>`).join('')}<th class="num">streamed, per 4 B</th></tr></thead><tbody>`+
  LV.map(l=>`<tr><td>${l.label}<br><span class="small">${l.table}</span></td>`+cols.map(([k])=>{const e=gsK[l.cols[k]]; if(!e||!e.pj_per_element)return '<td class="num">—</td>';
   const part=k.endsWith('_lg')?`<code>${e.op}</code><br>`:'';
   const few=e.pj_per_element.cards<gsCards.length?`<br><span class="small">${andList(CK.cardsIn(e.pj_per_element.per_card).map(cname))} only</span>`:'';
   return `<td class="num" data-sort="${e.pj_per_element.mean}">${part}<b>${gsE(e.pj_per_element.mean)}</b><br><span class="small">${rngs(e.pj_per_element)}</span><br>${gsRate(e.elements_per_s.mean)}${few}</td>`;}).join('')+
   `<td class="num">${gsStream(l)!=null?gsE(gsStream(l)):'—'}</td></tr>`).join('')+'</tbody>';
 $('gstabcards').innerHTML=`<thead><tr><th>Level</th><th class="num">gather <code>fgw.ps</code>, per card ± se</th><th class="num">scatter <code>fscw.ps</code>, per card ± se</th></tr></thead><tbody>`+
  LV.map(l=>{const g=gsK[l.cols.gather], c=gsK[l.cols.scatter]; if(!(g&&g.pj_per_element)&&!(c&&c.pj_per_element))return '';
   return `<tr><td>${l.label}</td><td class="num small">${g&&g.pj_per_element?gsPer(g.pj_per_element):'—'}</td><td class="num small">${c&&c.pj_per_element?gsPer(c.pj_per_element):'—'}</td></tr>`;}).join('')+'</tbody>';
 /* the text */
 const I=GS.items, get=(k,c)=>{const l=GS.levels.find(x=>x.key===k); return l&&l.cols[c]?gsK[l.cols[c]]:null;}, lvl=k=>GS.levels.find(x=>x.key===k);
 const g1=get('l1','gather'),g2=get('l2','gather'),gs=get('scp','gather'),gd=get('dram','gather'),s1=get('l1','scatter'),s2=get('l2','scatter'),sd=get('dram','scatter');
 const ld1=get('l1','load'),ld2=get('l2','load'),b1=get('l1','block'),gl2=get('l2','gather_lg'),gg3=get('l3','gather_lg'),gr=get('rscp','gather');
 const pj=e=>e.pj_per_element.mean, rt=e=>e.elements_per_s.mean;
 const z2=gsGet('fgw.ps','dram-4K',{d:'zeros'}), zd=gsGet('fgw.ps','dram-256K',{d:'zeros'}), zs2=gsGet('fscw.ps','dram-4K',{d:'zeros'});
 const MH=I['GS-MH']||{}, UC=I['GS-UC']||{}, L1I=I['GS-L1']||{}, DR=I['GS-DRAM']||{}, CR=(I['GS-CARD']||{}).ratios||{};
 const out=o=>{const oc=CK.cardsIn(o.outcomes||{}).map(h=>o.outcomes[h]); return oc.length&&oc.every(x=>x===oc[0])?`${oc[0]} on every card`:andList(CK.cardsIn(o.outcomes||{}).map(h=>`${cname(h)} ${o.outcomes[h]}`));};
 const h21=Math.max(...CK.cardsIn(MH.per_card||{}).map(h=>Math.max(...MH.per_card[h].h2_over_h1_l2))), uc=CK.cardsIn(UC.per_card||{}).map(h=>(UC.per_card[h].h2_over_h1[0]+UC.per_card[h].h2_over_h1[1])/2);
 const ucm=uc.reduce((a,b)=>a+b,0)/uc.length;
 if(!(g1&&g2&&gs&&gd&&s1&&s2&&sd&&ld1&&ld2&&b1&&gl2&&gg3&&gr))return;
 $('gslead').innerHTML=`The vector unit's indexed loads and stores take eight addresses per instruction from a vector of byte offsets. <b>From the L1 a gather is as cheap as a scalar load</b> (${f1(pj(g1))} pJ an element, ${gsRate(rt(g1),' elements/s')} over the chip). `+
  `<b>Past the L1 every element fetches its own line</b>: a random word costs ${f0(pj(g2))} pJ from the L2 (${f0(pj(g2)/gsStream(lvl('l2')))}× the same 4 B read contiguously) and ${f1(pj(gd)/1000)} nJ from DRAM (${f0(pj(gd)/gsStream(lvl('dram')))}×), at ${gsRate(rt(g2))} and ${gsRate(rt(gd))}. `+
  `Three passes on each of ${gsN} cards in ${gsN} machines (E48, 26 September), every tested item decided card by card.`;
 const drop=gsCards.map(h=>[h,(GS.dropped[h]||[])]).filter(x=>x[1].length), dcf=[...new Set(drop.flatMap(x=>x[1].map(d=>d.cfg)))];
 $('gstext').innerHTML='<ul>'+
  `<li><b>From the L1, a gather costs what a scalar load costs.</b> ${gsRate(rt(g1),' elements/s')} at ${f1(pj(g1))} pJ each against ${gsRate(rt(ld1))} at ${f1(pj(ld1))} pJ for scalar <code>flw</code> on the same 64 offsets; an instruction's eight elements take ${f2(g1.cpi_minion.mean)} minion-cycles on every card (the design's model: 8, one address a cycle; registered 7–12: ${out(L1I)}). The 32 B-block form <code>fg32w.ps</code>, one access per instruction with the lanes permuted inside the block, runs ${f1(rt(b1)/rt(g1))}× as fast at ${f2(pj(b1)/pj(g1))}× the energy.</li>`+
  `<li><b>Past the L1 the line is the unit.</b> A minion's two miss handlers fetch two lines at a time: ${gsRate(rt(g2))} from the L2 and ${gsRate(rt(gs))} from the own scratchpad, ${f2(rt(g2)/MH.bound_elements_per_s)}× the two-miss-handler bound (${gsRate(MH.bound_elements_per_s)}), with one hart or two (the second adds ${f2(100*(h21-1))}% or less: ${out(MH)}), and no faster than eight scalar loads on the same addresses (${gsRate(rt(ld2))}). From DRAM ${gsRate(rt(gd))}: the lines arrive at ${f1(gd.line_bytes_per_s.mean/1e9)} GB/s, DRAM's streaming bandwidth (57–95 GB/s registered: ${out(DR)}), at ${f0(gd.pj_per_line.mean/64)} pJ per line byte against a tensor load's ${f0(CB['tload/dram/random'].mean)} pJ/B. A scratchpad two mesh hops away: ${gsRate(rt(gr))} at ${f0(pj(gr))} pJ.</li>`+
  `<li><b>Skipping the L1 does not help.</b> <code>fgwl.ps</code> reads the L2 at ${gsRate(rt(gl2))}, ${f2(rt(gl2)/rt(g2))}× the path through the L1, at ${f0(pj(gl2))} pJ; one minion's second hart adds only ${f0(100*(ucm-1))}% to it, where the strict per-thread order of L1-bypassing operations predicted 1.6–2.4× (${out(UC)}): the two harts share one limit. <code>fgwg.ps</code> reaches the line's home L3 slice at ${gsRate(rt(gg3))} for ${f2(pj(gg3)/1000)} nJ.</li>`+
  `<li><b>A scatter costs about twice a gather.</b> Into the L2 ${f0(pj(s2))} pJ (${f1(pj(s2)/pj(g2))}× the gather) at ${gsRate(rt(s2))}: each element allocates its line and writes it back; into DRAM ${gsRate(rt(sd))} at ${f1(pj(sd)/1000)} nJ (${f1(pj(sd)/pj(gd))}×).</li>`+
  (z2&&zd&&zs2?`<li><b>Random data costs more than zeros</b>: a gather ${f2(pj(g2)/pj(z2))}× from the L2 (${f0(pj(z2))} pJ on zeros) and ${f2(pj(gd)/pj(zd))}× from DRAM (${f1(pj(zd)/1000)} nJ), a scatter ${f2(pj(s2)/pj(zs2))}× into the L2.</li>`:'')+
  `<li><b>The ${gsN} cards agree.</b> Every rate is the same to ${f2(100*Math.max(...Object.values(CR).map(r=>Math.max(Math.abs(r.elements_per_s.p10-1),Math.abs(r.elements_per_s.p90-1)))))}% (10–90% over the configurations); energy per element is ${andList(Object.keys(CR).sort((a,b)=>CK.cardsIn([a.split('/')[0],b.split('/')[0]])[0]===a.split('/')[0]?-1:1).map(k=>`${f3(CR[k].pj_per_element.median)}× aifoundry2's on ${cname(k.split('/')[0])}`))} in the median, each card at its own die temperature. All ${GS.checks[gsCards[0]].expected} verify launches passed on every card (every gathered element, scattered word and shared counter checked), the detector of erratum 1.3's skipped elements; when every lane scatters to one word, lane 7's value remains.</li>`+
  dcf.map(cf=>{const e=gsK[cf]||{}, who=drop.filter(x=>x[1].some(d=>d.cfg===cf)).map(x=>x[0]), kept=gsCards.filter(h=>!who.includes(h));
   return `<li><b>A gap.</b> The <code>${e.op}</code> gather from ${e.ws/1024} KB per hart lost every energy burst on ${andList(who.map(cname))}: one launch in each burst ran at an implied 0.594 GHz (cycles over wall time), just under the pre-registered 0.595–0.605 GHz band, while the telemetry read 600 MHz. The rule was not relaxed, so its energy is ${andList(kept.map(cname))}'s alone (the hollow dot).</li>`;}).join('')+
  '</ul>'+`<p class="small">Scatter-add and the packed atomics are in <a href="#synchronisation">section 6</a>; the per-line and per-element split, masks, element sizes and lane conflicts in <a href="#finer-grain-wires-lines-rows-and-the-leakage-of-the-arrays">4.3</a>. The measurement: <a href="https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/tools/claims-v3/gs"><code>tools/claims-v3/gs/</code></a> (E48).</p>`;
})();

/* 6: the packed atomics, the scalar ones on the same tables, and scatter-add */
(function(){
 if(!GS||!$('sync'))return;
 const R=[['famoaddl.pi','shire-256K','rand','Packed atomic add <code>famoaddl.pi</code>, random words of a 256 KB table per shire','at the shire’s L2; eight updates an instruction, one after another'],
  ['amoaddl.w','shire-256K','rand','Scalar atomic add <code>amoaddl.w</code>, the same tables','as fast as the packed form, and cheaper'],
  ['famoaddg.pi','chip-8M','rand','Packed atomic add <code>famoaddg.pi</code>, random words of one 8 MB table for the chip','at the line’s home L3 slice'],
  ['amoaddg.w','chip-8M','rand','Scalar atomic add <code>amoaddg.w</code>, the same table','the spread global atomic above, each hart on random words of the table'],
  ['famoaddl.pi','dram-512B','bcast','<code>famoaddl.pi</code>, all eight lanes on the hart’s own word','every update counted'],
  ['famoaddg.pi','dram-512B','bcast','<code>famoaddg.pi</code>, all eight lanes on the hart’s own word','']];
 const body=$('sync').tBodies[0]; if(!body)return;
 R.forEach(([op,t,p,lab,note])=>{const e=gsGet(op,t,{p,d:'zeros'}); if(!e||!e.pj_per_element)return; const c=e.pj_per_element, cyc=e.cpi_minion.mean/e.per_instr;
  const tr=document.createElement('tr');
  tr.innerHTML=`<td>${lab}</td><td class="num">${bt({mean:c.mean/1000,lo:c.lo/1000,hi:c.hi/1000},f2)} nJ</td><td class="num small">${CK.cardsIn(c.per_card).map(h=>`${cshort(h)} ${f2(c.per_card[h].mean/1000)} ± ${more(c.per_card[h].se/1000,f2)}`).join('<br>')}</td>`+
   `<td class="num" data-sort="${cyc}">${gsRate(e.elements_per_s.mean,' updates/s')}, ${f0(cyc)} cycles an update per minion</td><td class="small">E48, ${gsN} cards${note?'; '+note:''}</td>`;
  body.appendChild(tr);});
 const e=(op,t,d)=>gsGet(op,t,{d:d||'zeros'}), fl=e('famoaddl.pi','shire-256K'), al=e('amoaddl.w','shire-256K'), fg=e('famoaddg.pi','chip-8M'), ag=e('amoaddg.w','chip-8M');
 const up=[['the L1','dram-512B'],['the L2','dram-4K'],['the own scratchpad','scp-16K'],['DRAM','dram-256K']].map(([l,t])=>[l,e('upd',t,'random')]);
 if(!(fl&&al&&fg&&ag)||up.some(u=>!u[1]))return;
 const r=x=>x.elements_per_s.mean, p=x=>x.pj_per_element.mean/1000;
 const u10=up.filter(u=>r(u[1])>1e10).map(u=>u[0]), a10=[['famoaddl.pi',fl],['amoaddl.w',al],['famoaddg.pi',fg],['amoaddg.w',ag]].filter(x=>r(x[1])>1e10).map(x=>`<code>${x[0]}</code>`);
 $('gssynctext').innerHTML=`<b>The packed atomics and scatter-add</b> (E48, three passes on each of ${gsN} cards, 26 September; the table's last six rows). A packed atomic applies its eight lanes one after another: <code>famoaddl.pi</code> adds into a shire's table at ${gsRate(r(fl),' updates/s')}, the rate of scalar <code>amoaddl.w</code> on the same tables (${gsRate(r(al))}), for ${f2(p(fl)/p(al))}× its energy per update; at the home L3, <code>famoaddg.pi</code> runs ${gsRate(r(fg))} against ${gsRate(r(ag))}, for ${f2(p(fg)/p(ag))}×. `+
  `Every update counts: the verify launches checked every counter of the shared tables, and none was lost. On a table private to each hart, the vector unit's own gather, <code>fadd.ps</code> and scatter runs at ${up.map(([l,u])=>`${gsRate(r(u))} at ${p(u)<0.1?f3(p(u)):p(u)>=10?f1(p(u)):f2(p(u))} nJ in ${l}`).join('; ')}. `+
  `Past 10 G updates a second, the rate <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-influence-functions">Influence functions on the ET-SoC-1</a> asked of a scatter-add: gather-add-scatter in ${andList(u10)}, and ${andList(a10)} on a shire's table; nothing that updates the home L3 or DRAM.`;
})();

/* ---------- 6: every way to add into a table, rate against energy per update (pages-v5) ----------
   D.gs.updates (E48: the vector unit's gather, fadd.ps and scatter on a private table per hart, and the atomic adds on
   tables the harts share), each at its rate over the chip (elements_per_s) and its energy per update (pj_per_element),
   pooled or one card's; and the hot line's two runs (sync.atomics: the rate of the 22 September session, which the
   bank fixes; the energy pooled over the reruns, reruns.hotline_nj_per_op). ASK is the scatter-add rate Influence
   functions on the ET-SoC-1 asked of the chip, the threshold section 6's text uses. */
(function(){
 if(!GS||!$('updmap')||!GS.updates)return;
 const ASK=1e10;
 const WHERE={'dram-512B':'L1','dram-4K':'L2','scp-16K':'own scratchpad','dram-256K':'DRAM','shire-256K':'L2','chip-8M':'L3'};
 const SHORT={'dram-512B':'L1','dram-4K':'L2','scp-16K':'scratchpad','dram-256K':'DRAM'};
 const code=t=>String(t).replace(/`([^`]+)`/g,'<code>$1</code>');
 /* label placement per point: [anchor, dx, dy] for the long (wide) and short (narrow) labels */
 const P=[];
 GS.updates.forEach(u=>{const e=gsK[u.cfg]; if(!e||!e.pj_per_element||!e.elements_per_s)return; if(u.cfg.indexOf('/bcast/')>=0)return;
  const t=e.table, priv=u.op==='upd', w=WHERE[t]||t;
  const lng=priv?`gather, add, scatter: ${w==='own scratchpad'?'own scratchpad':w==='DRAM'?'DRAM':'the '+w}`:`${u.op}, ${t.startsWith('shire')?'shire tables':'chip table'}`;
  const sht=priv?(t==='dram-4K'?'L2, scratchpad':t==='scp-16K'?null:SHORT[t]):(u.op==='amoaddl.w'?'shire tables':u.op==='amoaddg.w'?'chip table':null);
  /* the L2 and the own scratchpad run at the same rate and nearly the same energy: one label for the pair */
  const lab=t==='dram-4K'?'gather, add, scatter: the L2, own scratchpad':t==='scp-16K'?null:lng;
  const pos={'dram-512B':['end',-9,4],'dram-4K':['start',9,-5],'scp-16K':['start',9,12],'dram-256K':['start',9,4]}[t]||
   (t==='chip-8M'?(u.op.startsWith('f')?['start',9,-4]:['end',-9,16]):(u.op.startsWith('f')?['start',9,-2]:['start',9,12]));
  const posW=pos;
  P.push({key:u.cfg,fam:priv?'priv':'shared',near:w!=='L3'&&w!=='DRAM',where:w,lng,lab,sht,pos:posW,tip:code(u.label),
   rate:h=>CK.pick(e.elements_per_s,h), nj:h=>{const p=CK.pick(e.pj_per_element,h); return p&&{mean:p.mean/1000,se:p.se!=null?p.se/1000:null,n:p.n};},
   bar:e.pj_per_element,per:e.pj_per_element.per_card});});
 const hn=RR.hotline_nj_per_op||{};
 [['contended','amoaddg, one line','one line','one contended global atomic: 1,024 minions on one line, the bank serialises them',['start',9,4],['end',-6,14]],
  ['spread','amoaddg, 32 lines','32 lines','the same instruction spread over 32 lines, one per shire, each homed in its shire',['end',-9,-6]]].forEach(([k,lng,sht,tip,pos,posN])=>{
  const e=hn[k], r=at[k]; if(!e||!r)return;
  /* posN: on a phone the contended line's label goes below and left of its ring, clear of the DRAM square and of the
     1 W line through the ring */
  P.push({key:k,fam:'hot',near:false,where:'L3',lng,sht,pos,posN,tip:tip+` (the rate: ${cname(LAWCARD)}, 22 September; the energy: the hot line's passes, section 6's table)`,
   rate:h=>(h==='pooled'||CK.pick(e,h))?{mean:r.ops_per_s}:null, nj:h=>h==='pooled'?{mean:e.mean,lo:e.lo,hi:e.hi,n:e.n}:(p=>p&&{mean:p.mean,se:p.se,n:p.n})(CK.pick(e,h)),bar:{lo:e.lo,hi:e.hi},per:e.per_card});});
 if(P.length<3)return;
 const FAM={priv:['the vector unit’s gather, fadd.ps and scatter on a private table per hart','var(--c4)','box'],shared:['an atomic add on a table the harts share','var(--c7)','dot'],hot:['the hot line’s runs: one global line, or 32','var(--c5)','ring']};
 let card=CK.bus('card').value&&(CK.bus('card').value==='pooled'||gsCards.includes(CK.bus('card').value))?CK.bus('card').value:'pooled';
 const val=(p,h)=>{const r=p.rate(h), e=p.nj(h); if(!r||!e||!(r.mean>0)||!(e.mean>0))return null; const lo=h==='pooled'?(p.bar.lo!=null?p.bar.lo/(p.fam==='hot'?1:1000):e.mean):(e.se!=null?e.mean-e.se:e.mean), hi=h==='pooled'?(p.bar.hi!=null?p.bar.hi/(p.fam==='hot'?1:1000):e.mean):(e.se!=null?e.mean+e.se:e.mean);
  return {rate:r.mean,nj:e.mean,lo:Math.max(lo,e.mean*0.01),hi,se:e.se,n:e.n};};
 const allV=P.flatMap(p=>['pooled'].concat(gsCards).map(h=>val(p,h)).filter(Boolean));
 const X0=Math.pow(10,Math.floor(Math.log10(Math.min(...allV.map(v=>v.rate))/1.5))), X1=Math.pow(10,Math.ceil(Math.log10(Math.max(...allV.map(v=>v.rate))*1.5)));
 const Y0=Math.pow(10,Math.floor(Math.log10(Math.min(...allV.map(v=>v.lo))/1.3))), Y1=Math.pow(10,Math.ceil(Math.log10(Math.max(...allV.map(v=>v.hi))*1.3)));
 const fams=Object.keys(FAM).filter(k=>P.some(p=>p.fam===k));
 CK.legend('upd-legend',fams.map(k=>({key:k,label:FAM[k][0],color:FAM[k][1],mark:FAM[k][2]})).concat([{key:'ask',label:'10 G updates a second: the rate Influence functions asks of a scatter-add',color:'var(--ink-2)',mark:'dash'},{key:'w',label:'constant power over idle',color:'var(--muted)',mark:'line'}]));
 const nameOf=p=>p.lng.replace(/^gather, add, scatter: /,'gather, add and scatter in ');
 const f=CK.frame('updmap',{label:'Updates per second over the chip against energy per update, for every way to add into a table',height:W=>W<600?360:380,draw:f=>{
  const L=48, Rr=f.narrow?12:18, T=26, B=40, x=CK.log(X0,X1,L,f.W-Rr), y=CK.log(Y0,Y1,f.H-B,T), nodes=[];
  /* the x ticks CK.axes would choose, less the one in the corner, where it would meet the lowest y tick */
  const xt=x.ticks(Math.max(2,Math.round((f.W-L-Rr)/90))).filter(t=>t>X0*1.001);
  /* a label's halo in the colour behind it: the green of the region past the rate asked, or the page */
  const xAsk=ASK>X0&&ASK<X1?x(ASK):Infinity, haloFor=t=>{let w=0; try{w=t.getComputedTextLength();}catch(_){} const a=t.getAttribute('text-anchor')||'start', x0=+t.getAttribute('x')-(a==='end'?w:a==='middle'?w/2:0);
   if(x0>=xAsk)t.style.stroke='color-mix(in srgb, var(--c3) 7%, var(--page))';};
  CK.axes(f,{x,y,L,R:Rr,T,B,xt,xfmt:v=>v>=1e9?`${CK.fmt.num(v/1e9)} G`:`${CK.fmt.num(v/1e6)} M`,yfmt:v=>CK.fmt.num(v,v>=1?0:Math.ceil(-Math.log10(v)-1e-9)),xl:'updates per second over the chip, 1,024 minions (log)',yl:'nJ per update, above idle (log)'});
  /* the part of the plane past the rate asked for, and the line itself */
  if(ASK>X0&&ASK<X1){CK.el('rect',{x:x(ASK),y:T,width:f.W-Rr-x(ASK),height:f.H-B-T,fill:'var(--c3)','fill-opacity':0.07},f.svg);
   CK.el('line',{x1:x(ASK),x2:x(ASK),y1:T,y2:f.H-B,stroke:'var(--ink-2)','stroke-width':1.5,'stroke-dasharray':'5 4'},f.svg);
   CK.inside(f,[CK.txt(f.svg,f.W-Rr-4,T+13,f.narrow?'10 G/s asked':'past 10 G updates/s, the rate asked','lab','end')]);}
  /* constant power over idle: nJ x (updates/s) = W */
  const dl=[], xR=f.W-Rr, yB=f.H-B;
  (f.narrow?[1,10]:[1,3,10,30]).forEach(Wt=>{const ya=Wt/(X0*1e-9), yb=Wt/(X1*1e-9); let xa=X0, xb=X1, y1=ya, y2=yb;
   if(y1>Y1){xa=Wt/(Y1*1e-9); y1=Y1;} if(y2<Y0){xb=Wt/(Y0*1e-9); y2=Y0;} if(!(xa<xb&&xa<X1&&xb>X0))return;
   CK.el('line',{x1:x(xa),y1:y(y1),x2:x(xb),y2:y(y2),stroke:'var(--muted)','stroke-width':1,'stroke-opacity':0.7},f.svg);
   /* the label beside its line, never on it: along the top, just right of where the line comes in (the line falls to
      the right, so the label clears it by 4 px at the label's lowest point), which keeps the labels in one row over the
      empty top of the plot; else over where it enters at the left edge, right of where it meets the bottom, or under
      where it meets the right edge */
   const s=`${CK.fmt.num(Wt)} W`, tl=CK.txt(f.svg,0,0,s,'tick','start'); let w=0; try{w=tl.getComputedTextLength();}catch(_){} if(!(w>0))w=7.2*s.length;
   const xAt=yy=>x(xa)+(yy-y(y1))*(x(xb)-x(xa))/(y(y2)-y(y1)), yTop=T+14, xTop=xAt(yTop+3)+4;
   const X=[[xTop,yTop,'start',y1>=Y1*0.9999&&xTop+w<=xR-2],[L+3,y(y1)-6,'start',xa<=X0*1.0001&&y(y1)-18>=T],
    [x(xb)+5,yB-5,'start',y2<=Y0*1.0001&&x(xb)+5+w<=xR-2],[xR-3,y(y2)+12,'end',xb>=X1*0.9999&&y(y2)+12<=yB-3]].find(c=>c[3]);
   if(!X){tl.remove();return;}
   tl.setAttribute('x',X[0]); tl.setAttribute('y',X[1]); tl.setAttribute('text-anchor',X[2]); tl.setAttribute('class','tick halo'); dl.push(tl);});
  CK.inside(f,dl); dl.forEach(haloFor);
  /* the points */
  const labs=[];
  P.forEach(p=>{const v=val(p,card); if(!v)return; const [lab,col,mk]=FAM[p.fam], cx=x(v.rate), cy=y(v.nj), gg=CK.el('g',{'data-series':p.fam},f.svg);
   CK.el('circle',{cx,cy,r:10,class:'ck-hit'},gg);
   if(v.hi>v.lo)CK.el('line',{x1:cx,x2:cx,y1:y(v.hi),y2:y(v.lo),stroke:col,'stroke-width':1.5},gg);
   if(mk==='box')CK.el('rect',{x:cx-4.5,y:cy-4.5,width:9,height:9,rx:1.5,fill:col},gg);
   else if(mk==='ring')CK.el('circle',{cx,cy,r:4.5,fill:'var(--surface)',stroke:col,'stroke-width':2},gg);
   else CK.el('circle',{cx,cy,r:5,fill:col},gg);
   const W=v.nj*1e-9*v.rate;
   CK.tip(f,gg,`<b>${nameOf(p)}</b>, ${cname(card)}<br>${p.tip}<br>${gsRate(v.rate,' updates/s')} over the chip at <b>${v.nj>=1?f2(v.nj):f3(v.nj)} nJ</b> an update`+
    (card==='pooled'&&p.bar.lo!=null?` [${(p.fam==='hot'?[p.bar.lo,p.bar.hi]:[p.bar.lo/1000,p.bar.hi/1000]).map(z=>z>=1?f2(z):f3(z)).join('–')}]`:v.se!=null?` ± ${more(v.se,v.nj>=1?f2:f3)}`:'')+
    `, ${f1(W)} W over idle<br>${v.rate>ASK?'past':'short of'} the 10 G/s asked`+(card==='pooled'&&p.per?'<br>'+CK.cardsIn(p.per).map(h=>`${cname(h)} ${(p.fam==='hot'?p.per[h].mean:p.per[h].mean/1000).toFixed(v.nj>=1?2:3)} nJ`).join(' · '):''));
   nodes.push(gg);
   const s=f.narrow?p.sht:(p.lab===undefined?p.lng:p.lab); if(s){const [an,dx,dy]=(f.narrow&&p.posN)||p.pos; const t=CK.txt(f.svg,cx+dx,cy+dy,s,'lab',an); t.setAttribute('class','lab halo'); labs.push(t);}});
  CK.inside(f,labs); labs.forEach(haloFor);
  CK.keynav(f,nodes.sort((a,b)=>0));
  readout();
 }});
 function readout(){
  const V=P.map(p=>({p,v:val(p,card)})).filter(o=>o.v), fast=V.filter(o=>o.v.rate>ASK), slow=V.filter(o=>o.v.rate<=ASK);
  const hot=V.find(o=>o.p.key==='contended'), clean=fast.every(o=>o.p.near)&&slow.every(o=>!o.p.near);
  const lr=o=>`${nameOf(o.p).replace(/^gather, add and scatter in /,'').replace(/^own /,'the own ')} (${gsRate(o.v.rate)})`;
  const fa=fast.filter(o=>o.p.fam!=='priv');
  const missing=P.filter(p=>!val(p,card)).map(p=>p.lng);
  $('upd-readout').innerHTML=`On ${cname(card)}, ${fast.length} of the ${V.length} ways pass 10 G updates a second: gather, add and scatter on a private table in ${andList(fast.filter(o=>o.p.fam==='priv').map(lr))}, and ${andList(fa.map(o=>`<code>${o.p.lng.split(',')[0]}</code>`))} on ${fa.every(o=>o.p.where==='L2')?"the shire's tables":'shared tables'} (${andList(fa.map(o=>gsRate(o.v.rate)))}). `+
   (slow.length?`The others ${clean?'all update the home L3 or DRAM and ':''}run at ${gsRate(Math.min(...slow.map(o=>o.v.rate)))}–${gsRate(Math.max(...slow.map(o=>o.v.rate)))}. `:'')+
   (hot?`One contended line holds ${f1(hot.v.nj*1e-9*hot.v.rate)} W over idle for ${gsRate(hot.v.rate,' updates/s')}, ${f0(hot.v.nj/Math.min(...V.map(o=>o.v.nj)))}× the cheapest update's energy. `:'')+
   (missing.length?`Not measured on ${cname(card)}: ${andList(missing)}.`:'');
  if(!$('updlead').innerHTML){const Vp=P.map(p=>({p,v:val(p,'pooled')})).filter(o=>o.v), fp=Vp.filter(o=>o.v.rate>ASK), sp=Vp.filter(o=>o.v.rate<=ASK);
   $('updlead').innerHTML=(fp.every(o=>o.p.near)&&sp.every(o=>!o.p.near)?`<b>Only updates that stay in the L1, the L2 or the shire's own scratchpad reach 10 G a second</b>; every one that goes to the home L3 or to DRAM runs at ${gsRate(Math.max(...sp.map(o=>o.v.rate)))} or less. `:'')+
    `The chart puts each way the chip can add into a table at the rate the whole chip reached and the energy one update cost (E48 and the hot line, section 6's table).`;}
 }
 const cs=CK.cardSeg('upd-card',{cards:gsCards,pooled:true,label:'card',value:card,onChange:v=>{card=v;f.redraw();}}); if(cs.value!==card){card=cs.value;f.redraw();}
})();

/* ---------- 9. how the bars were made, from the data ---------- */
(function(){
 const C=D.catalogue, nc=CARDS.length, cnt=Object.values(CB).map(c=>c.n), nCat=cnt.length?Math.max(...cnt):0, perCard=nc?nCat/nc:0;
 const PP=RR.passes_per_card||{}, nPass=o=>{const n=[...new Set(CK.cardsIn(o||{}).map(h=>o[h].length))]; return n.length===1?`${WORD[n[0]]||n[0]} passes on each card`:'passes';};
 const nr=D.tensor.runs_per_card||{}, nrs=[...new Set(CK.cardsIn(nr).map(h=>nr[h]))];
 const hwOf=c=>(c.hi-c.lo)/2/c.mean, med=v=>{v=v.slice().sort((a,b)=>a-b); return v[v.length>>1];};
 const share=med(Object.values(CB).filter(c=>c.cards>1&&c.hi>c.lo).map(c=>c.card_diff/(c.hi-c.lo)));
 const instr=Object.entries(CB).filter(([k,c])=>/\/random\/h2$/.test(k)&&c.mean>0).map(([k,c])=>hwOf(c));
 const REP=(V3.catalogue||{}).rep_pct||{}, rh=CK.cardsIn(REP);
 const clk=CARDS.every(h=>{const q=(C.cards[h]||{}).idle_clock; return q&&q.frac_bursts_idle_600===1&&Object.keys(q.busy_by_mhz||{}).every(m=>m==='600');});
 const c1=cb('spin/zeros/h1'), c2=cb('spin/zeros/h2'), rr=RR.relay_pj_per_byte||{}, hn=(RR.hotline_nj_per_op||{}).contended;
 const nop=cb('nop/zeros/h2'), fen=cb('fence/zeros/h2'); if(nop&&fen)$('awakeslot').textContent=`${f1(Math.min(nop.mean,fen.mean))}–${f1(Math.max(nop.mean,fen.mean))}`;
 const aw=[c1,c2].filter(Boolean).map(c=>100*hwOf(c)), rl=['dram','hop','scp'].filter(k=>rr[k]).map(k=>100*hwOf(rr[k]));
 const rng=v=>Math.round(Math.min(...v))===Math.round(Math.max(...v))?f0(v[0]):`${f0(Math.min(...v))}–${f0(Math.max(...v))}`;
 $('barstext').innerHTML=`The catalogue (sections 2, 3, 4.1, 4.3, 8) is ${WORD[perCard]||perCard} passes in shuffled order on each of ${WORD[nc]||nc} cards, n = ${nCat} (the version-3 check's full catalogue, 26 September; 4.5's rail split is ${CARDS[0]}'s ${WORD[perCard]||perCard} passes alone); the rings, the levels and the relay (4.2, 5) are ${nPass(PP.rings)} (n = ${rr.dram?rr.dram.n:'—'}), and the tensor rows (3.2) ${nrs.length===1?`${WORD[nrs[0]]||nrs[0]} runs on each card`:'several runs on each card'} (n = ${(TB.fp32_randn||{}).n||'—'}), both from the same check; the hot line (6) is its 22 September session plus three warm passes on aifoundry2 and three on aifoundry3 (23 September), n = ${hn?hn.n:'—'}; the gathers and scatters (3.1's last table, 4.3, 4.4, 6's last six rows) are E48's three passes on each of ${gsN} cards, n = 9, under the catalogue's clock rule. `+
  `The range is used rather than a standard error because about half of a catalogue entry's bar is the difference between the cards (in the median entry the spread of the card means is ${f0(100*share)}% of the range), which a standard error of the pooled sample would understate; pass-to-pass scatter on one card is 1–2% for most entries (the median standard error is ${andList(rh.map(h=>`${f1(REP[h].median)}%`))} on ${andList(rh.map(cname))}). `+
  (clk?`The bars leave out a change of operating point, and on 26 September none was needed: every idle and busy sample of the catalogue was at 600 MHz on every card. `:`The bars leave out a change of operating point: bursts whose busy samples left 600 MHz are dropped. `)+
  `They do carry the drift of the idle between the two stretches that bracket each burst, which every "over idle" figure inherits; the idle law enters only through the leakage correction. `+
  (hn?`The hot line, the smallest signal (about ${f1(HOT?HOT.mean:1.2)} W over idle), carries one of the widest bars, ±${f0(100*hwOf(hn))}%, mostly its first session's ${f1(at.contended.over_idle_w)} W against 1.0–1.2 W since; `:'')+
  `the awake core (±${rng(aw)}%) and the relay (±${rng(rl)}%, mostly aifoundry1 card 1 against the others) are wider than a typical catalogue entry (the median instruction's range is ±${f1(100*med(instr))}%, section 3.1).`;
})();

/* ---------- contents: every h2 and h3, with its section number; runs before the template adds its # links ---------- */
(function(){const ol=$('toclist'); if(!ol)return;
 ol.style.listStyle='none'; ol.style.paddingLeft='0'; ol.style.margin='6px 0 0';
 document.querySelectorAll('main h2, main h3').forEach(hd=>{if(!hd.id)return;
  const li=document.createElement('li'), a=document.createElement('a'); a.href='#'+hd.id; a.textContent=hd.textContent.replace(/\s+/g,' ').trim();
  if(hd.tagName==='H3'){li.style.marginLeft='1.4em'; li.className='small';} li.appendChild(a); ol.appendChild(li);});})();
/* tables become stacked cards under 600 px (template CSS table.stack): each value keeps its column's name */
['awake','instrtab','tensor','memtab','memold','linetab','rowtab','neightab','comm','sync','relaycheck','gsl1tab','gspattab','gstab','gstabcards'].forEach(id=>{const t=$(id); if(!t||!t.tHead)return; CK.stackTable(t);
 /* the first header cell often names the table; stacked, the header row is hidden, so it becomes a caption there */
 const th=t.tHead.rows[0].cells[0], tx=th?th.textContent.replace(/\s+/g,' ').trim():''; if(tx.length>12){const c=t.createCaption(); c.className='stack-cap'; c.textContent=tx;}});
/* sortable tables (after stackTable): click a header to sort; the per-card and description columns are left alone, and
   #comm sorts its rings (the relay rows are a group of their own). #linetab is two small tables in different units and
   is not sorted. */
[['tensor'],['memtab'],['rowtab'],['neightab'],['comm',{filter:true,filterLabel:'Filter the rings'}],['sync'],['gsl1tab'],['gspattab']].forEach(([id,o])=>{const t=$(id); if(t&&t.tHead&&t.tBodies.length)CK.sortTable(t,o);});
/* the Terms box opens when the page is opened at #terms */
(function(){const t=$('terms'); const op=()=>{if(location.hash==='#terms'&&t)t.open=true;}; op(); window.addEventListener('hashchange',op);})();
