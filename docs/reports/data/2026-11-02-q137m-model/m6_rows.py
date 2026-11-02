# SPDX-License-Identifier: Apache-2.0
"""Q137(m): assemble M6's rows: M5's (fit_m5.assemble) plus the newer kinds experiments, counts matched by tile sha256."""
import json,os,glob,hashlib,collections,re,sys
ROOT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","..","..",".."))
DD=f"{ROOT}/docs/reports/data"; K=f"{ROOT}/tools/claims-v3/kinds"
sys.path.insert(0,f"{DD}/2026-11-01-q133b-power-model"); import fit_m5 as F
sha=lambda b: hashlib.sha256(b).hexdigest()
NEW={"E102":"2026-11-01-e102-balanced-bit-prices/e102.json","E108":"2026-11-01-e108-sign-located/e108.json","E115":"2026-11-01-e115-blind-pool/e115.json",
"E121":"2026-11-01-e121-zero-gate-replicate/e121.json","E122":"2026-11-01-e122-signs-replicate/e122.json","E123":"2026-11-01-e123-tile-spread-rest/e123.json",
"E127":"2026-11-02-e127-b-gate/e127.json","E128":"2026-11-02-e128-fp16-signs/e128.json","E131":"2026-11-02-e131-real-tiles-card1/e131.json"}
COUNTS=[("q132",f"{DD}/2026-11-01-q132-rtl-bench/counts-v2.json"),("e92",f"{DD}/2026-11-01-q132-rtl-bench/counts-e92.json"),
("e90",f"{DD}/2026-11-01-q132-rtl-bench/counts-e90.json"),("rpath",f"{DD}/2026-11-01-q132-rtl-bench/counts-e88.json"),
("real",f"{DD}/2026-11-01-q132-rtl-bench/counts-e86.json"),("e94",f"{DD}/2026-11-01-q132-rtl-bench/counts-e94e95.json"),
("e103",f"{DD}/2026-11-01-q132-rtl-bench/counts-e103-pool.json"),("train",f"{DD}/2026-11-01-q133b-power-model/counts-q133b-train.json"),
("blind3",f"{K}/blind3/counts-blind3.json"),("e106",f"{DD}/2026-11-01-e106-held-signs/desk/counts-e106.json"),
("e102",f"{DD}/2026-11-01-e102-balanced-bit-prices/bench/counts-e102.json"),("e104",f"{DD}/2026-11-01-e104-c-readback/desk/counts-e104.json"),
("e104",f"{DD}/2026-11-01-e104-c-readback/desk/counts-e104b.json"),("e104",f"{DD}/2026-11-01-e104-c-readback/desk/counts-e104c.json"),
("e108",f"{DD}/2026-11-01-e108-sign-located/desk/counts-e108.json"),("e108",f"{DD}/2026-11-01-e108-sign-located/desk/counts-e108b.json"),
("e127",f"{ROOT}/tools/claims-v3/e127/counts-e127.json"),("e128",f"{DD}/2026-11-02-e128-fp16-signs/desk/counts-e128.json"),
("e134",f"{DD}/2026-11-02-e134-bit-prices-more/bench/counts-e134.json"),
("e123",os.path.join(os.path.dirname(os.path.abspath(__file__)),"counts-e123.json"))]
_bins=None
def bins():
    global _bins
    if _bins is None:
        _bins=collections.defaultdict(list)
        for p in glob.glob(f"{ROOT}/tools/claims-v3/**/*.bin",recursive=True)+glob.glob(f"{DD}/**/*.bin",recursive=True):
            if os.path.getsize(p)==2048 and "/blind4/" not in p:
                _bins[(p.split('/')[-2],os.path.basename(p)[:-4])].append(p)
    return _bins
def cands(tag,t,n):
    b=bins(); names=[n]
    for pre in ("r2_","real_"):
        if n.startswith(pre): names.append(n[len(pre):])
    if "_" in n: names.append(n.split("_",1)[1])
    out=[]
    for nm in names:
        c=b.get((t,nm),[])
        ct=[p for p in c if f"/{tag}/" in p or f"-{tag}-" in p or f"/{tag}" in p]
        if ct: return ct
        if tag in("q132",) : 
            c0=[p for p in c if p.startswith(f"{K}/tiles/")]
            if c0: return c0
    return out
def count_index():
    idx={}
    for tag,f in COUNTS:
        if not os.path.exists(f): continue
        for k,v in json.load(open(f))["rows"].items():
            t,n=v["type"],v["kind"]
            for p in cands(tag,t,n)[:1]:
                h=sha(open(p,'rb').read()); idx.setdefault(h,v)
    return idx
def tile_for(e,t,n):
    tag=e.lower(); c=cands(tag,t,n)
    if c: return c[0]
    b=bins()
    for nm in (n, n[3:] if n.startswith("r2_") else None, n[5:] if n.startswith("real_") else None):
        if nm and b.get((t,nm)):
            ps=b[(t,nm)]; pk=[p for p in ps if p.startswith(f"{K}/tiles/")] or ([p for p in ps if "/real2/" in p] if n.startswith("r2_") else []) or ps
            if len(set(sha(open(p,'rb').read()) for p in ps))==1 or pk: return pk[0]
    return None
def assemble():
    rows,missing=F.assemble()
    old_sha={r["tile_sha256"]:r["kind"] for r in rows}
    old_f={r["tile_sha256"]:r["f"] for r in rows}
    idx=count_index()
    zc=json.load(open(f"{DD}/2026-11-01-q132-rtl-bench/counts-v2.json"))["rows"]; zeros={t:zc[f"{t}.zeros"]["mean"] for t in F.CPO}
    uncounted={}
    for e,f in NEW.items():
        d=json.load(open(f"{DD}/{f}")); card="a3" if d.get("card","").startswith("aifoundry3") else "c1"
        for key,it in d["items"].items():
            if key=="anchor_pi" or not isinstance(it.get("D"),dict) or it["D"].get("mean") is None: continue
            t=it["type"]; n=key.split(".",1)[1]
            if n in F.ANCHOR_NAMES or n in("randn","full"): continue
            p=tile_for(e,t,n)
            if p is None: missing.append(f"{e}:{key} (no tile)"); continue
            h=sha(open(p,'rb').read())
            if h not in idx and h not in old_f: uncounted[h]=(t,f"{e.lower()}_{n}",p); missing.append(f"{e}:{key} (no counts)"); continue
            base=re.sub(r"_e1\d\dd\d+$","",n)
            lab=old_sha.get(h) or (f"{t}.{base}" if os.path.exists(F.kinds_tile(t,base)) else f"{t}.{e.lower()}:{n}")
            if h in old_f:
                fe=dict(old_f[h]); cm=None
            else:
                crow=idx[h]; cm=crow["mean"].get("check_mismatch")
                fe=F.fmt_feats(F.bench_feats(crow["mean"],zeros[t]),t); fe.update({k:v for k,v in F.tile_feats(p,t).items() if k!="sha256"})
            rate=it["rate"]["mean"] if isinstance(it.get("rate"),dict) and it["rate"].get("mean") else F.RATE[t]
            rows.append({"exp":e,"card":card,"key":key,"type":t,"kind":lab,"tile_sha256":h,"tile_path":os.path.relpath(p,ROOT),"D":float(it["D"]["mean"]),
                         "D_se":it["D"].get("se"),"rate":float(rate),"f":fe,"check_mismatch":cm,
                         "dT_win":(it.get("dT_win") or {}).get("mean"),"p80":(it.get("p80") or {}).get("mean")})
    return rows,missing,uncounted
if __name__=="__main__":
    rows,missing,unc=assemble()
    c=collections.Counter(r["exp"] for r in rows); print(len(rows),dict(c))
    print("missing",len(missing),missing[:80])
    print("uncounted tiles",len(unc))
