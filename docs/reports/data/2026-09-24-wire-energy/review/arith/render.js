const fs=require('fs');
const html=fs.readFileSync(process.argv[2],'utf8');
const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const store={};
function mk(id){
  const e={id,_html:null,children:[],attrs:{},style:{},dataset:{},
    get innerHTML(){ if(this._html===null && id){ const m=html.match(new RegExp('id="'+id+'"[^>]*>([\\s\\S]*?)</(p|div|b|table|ol)>')); return m?m[1]:''; } return this._html||'';},
    set innerHTML(v){this._html=v;},
    set textContent(v){this._html=v;}, get textContent(){return this._html||'';},
    appendChild(c){this.children.push(c);return c;}, setAttribute(k,v){this.attrs[k]=v;},
    addEventListener(){}, querySelectorAll(){return [];}, getBoundingClientRect(){return {left:0,top:0,width:700};}};
  return e;}
global.document={getElementById(id){return store[id]||(store[id]=mk(id));},
  createElementNS(ns,t){const e=mk(null); e.tag=t; return e;}, createElement(t){return mk(null);}, querySelectorAll(){return [];}};
try{ (0,eval)(scripts[0]); }catch(e){ console.error('script error',e.stack); }
const strip=s=>s.replace(/<[^>]+>/g,'').replace(/&nbsp;/g,' ');
for(const id of ['l-hop','l-unc','l-uncd','l-uncb','l-load','l-09','k-hop','k-noc','k-noc-sub','k-one','k-09','modeltext','comparetext','practice','modeltab']){
  const e=store[id]; console.log('#'+id+': '+(e&&e._html!==null?strip(e._html):'(unset)')); }
// collect text labels from svg charts (compare chart, contention)
function texts(e,out){ if(e.tag==='text'&&e._html) out.push(e._html); for(const c of e.children) texts(c,out); return out;}
for(const id of ['comparechart','cont','alt','mesh']){ const e=store[id]; if(!e) continue; console.log('## '+id+': '+texts(e,[]).join(' | ')); }
