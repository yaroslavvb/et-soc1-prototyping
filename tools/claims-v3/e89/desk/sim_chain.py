"""Desk simulation of candidate E89 sessions on the Foster chain of docs/findings/11-thermal-model.md."""
import numpy as np, sys
TAU = np.array([1.5, 4, 60, 150, 400, 2500.0]); R = np.array([0.106, 0.050, 0.234, 0.136, 0.860, 0.081])
SCALE = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0   # scale of R (aifoundry3 today vs September)
KLEAK = 0.20                                               # W per degC (E78's auto slope 0.1994)
DT = 0.1
# S over idle (E78) per item; D over own zeros; D32 over fp32 zeros
S = {"idle": 0.0, "Zf": 1.986, "Zi": 2.605, "i8full": 9.648, "i8gauss": 9.161, "i8small": 8.628, "i8sp50": 8.061,
     "i8neg1": 4.176, "f32ones": 10.288, "f32randn": 26.701, "f32sp90": 2.509}
def session(segs, launch=8.0, gap=0.7):
    """segs: list of (item, seconds). Returns t, P (W over idle), labels per sample."""
    P = []; lab = []; seg_id = []
    for k, (it, L) in enumerate(segs):
        n = int(round(L / DT))
        if it == "idle":
            P += [0.0] * n
        else:
            per = launch + gap
            for i in range(n):
                tt = (i * DT) % per
                P.append(S[it] if tt >= gap else 0.0)
        lab += [it] * n; seg_id += [k] * n
    return np.array(P), lab, np.array(seg_id)
def simulate(P, T0=0.0):
    x = np.zeros(len(TAU)); out = np.empty(len(P)); Rs = R * SCALE
    for i, p in enumerate(P):
        T = x.sum()
        ptot = p + KLEAK * T if p > 0 or True else p
        x += DT / TAU * (Rs * ptot - x)
        out[i] = x.sum()
    return out
def plateau(T, seg_id, k, last):
    idx = np.where(seg_id == k)[0]; n = int(last / DT)
    return T[idx[-n:]].mean(), idx[-n:].mean() * DT
def est(T, seg_id, segs, k, pk=30, pz=20):
    """three-point: plateau(K) minus time-interpolated plateaus of the flanking Z segments; also K - Zbefore."""
    yk, tk = plateau(T, seg_id, k, pk); yb, tb = plateau(T, seg_id, k - 1, pz); ya, ta = plateau(T, seg_id, k + 1, pz)
    w = (tk - tb) / (ta - tb)
    return yk - ((1 - w) * yb + w * ya), yk - yb
def run(design, LK, LZ, settle, title):
    segs = design(LK, LZ, settle)
    P, lab, sid = session(segs)
    T = simulate(P)
    print(f"== {title}: LK {LK} s, LZ {LZ} s, total {len(P)*DT/60:.1f} min, peak rise {T.max():.1f} C")
    rows = []
    for k, (it, L) in enumerate(segs):
        if it in ("idle", "Zf", "Zi") or k + 1 >= len(segs):
            continue
        z = segs[k - 1][0]
        D = S[it] - S[z]
        e3, eb = est(T, sid, segs, k)
        rows.append((it, k, D, e3, eb))
    ref = [r for r in rows if r[0] == "f32randn"]
    cref = np.mean([r[3] / r[2] for r in ref]) if ref else None
    for it, k, D, e3, eb in rows:
        print(f"  {it:9s} seg {k:2d}  D {D:6.3f} W  3pt {e3:6.3f} C ({e3/D:.3f} C/W{'' if cref is None else f', ratio to ref {e3/D/cref:.3f}'})   K-Zbefore {eb:6.3f} C ({eb/D:.3f} C/W)")
def design_a(LK, LZ, settle):
    p = lambda: ([("Zf", settle), ("Zi", LK), ("Zf", LZ), ("f32ones", LK), ("Zf", LZ), ("Zi", LZ)] +
                 sum([[(k, LK), ("Zi", LZ)] for k in ["i8full", "i8gauss", "i8small", "i8sp50", "i8neg1"]], []))
    ref = [("Zf", settle), ("f32randn", LK), ("Zf", LZ), ("f32randn", LK), ("Zf", LZ)]
    return [("idle", 15)] + p() + [("idle", 30)] + p() + [("idle", 30)] + ref
def design_b(LK, LZ, settle):   # randn at the end of each pass
    p = lambda: ([("Zf", settle), ("Zi", LK), ("Zf", LZ), ("f32ones", LK), ("Zf", LZ), ("Zi", LZ)] +
                 sum([[(k, LK), ("Zi", LZ)] for k in ["i8full", "i8gauss", "i8small", "i8sp50", "i8neg1"]], []) +
                 [("Zf", LZ), ("f32randn", LK), ("Zf", LZ)])
    return [("idle", 15)] + p() + [("idle", 30)] + p()
for LK, LZ in [(90, 40), (120, 40), (90, 60)]:
    run(design_a, LK, LZ, 60, "A: reference block at the end")
run(design_b, 90, 40, 60, "B: randn closes each pass")
