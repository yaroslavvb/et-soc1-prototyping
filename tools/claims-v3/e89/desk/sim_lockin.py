"""Desk simulation of the E89 lock-in design on the Foster chain (11-thermal-model.md), with E78's powers."""
import numpy as np, random
TAU = np.array([1.5, 4, 60, 150, 400, 2500.0]); R = np.array([0.106, 0.050, 0.234, 0.136, 0.860, 0.081])
KLEAK = 0.20; DT = 0.1
S = {"idle": 0.0, "Zf": 1.986, "Zi": 2.605, "i8full": 9.648, "i8gauss": 9.161, "i8small": 8.628, "i8sp50": 8.061,
     "i8neg1": 4.176, "f32ones": 10.288, "f32randn": 26.701}
BLOCKS = {"i8full": ("i8full", "Zi"), "i8gauss": ("i8gauss", "Zi"), "i8small": ("i8small", "Zi"), "i8sp50": ("i8sp50", "Zi"),
          "i8neg1": ("i8neg1", "Zi"), "i8zero": ("Zi", "idle"), "f32ones": ("f32ones", "Zf"), "f32randn": ("f32randn", "Zf")}
H, M, LEAD, LAUNCH, GAP = 30.0, 2, 30.0, 6.8, 0.7
def half(item, secs):
    n = int(round(secs / DT)); out = []
    if item == "idle": return [0.0] * n
    per = LAUNCH + GAP
    for i in range(n):
        tt = (i * DT) % per
        out.append(S[item] if tt >= GAP else 0.0)
    return out
def session(order):
    P = [0.0] * 200; marks = []
    for b in order:
        k, z = BLOCKS[b]; t0 = len(P) * DT
        P += half(z, LEAD); ta = len(P) * DT
        for c in range(M):
            P += half(k, H) + half(z, H)
        marks.append((b, ta, len(P) * DT))
    return np.array(P), marks
def simulate(P):
    x = np.zeros(6); T = np.empty(len(P))
    for i, p in enumerate(P):
        x += DT / TAU * (R * (p + KLEAK * x.sum()) - x); T[i] = x.sum()
    return T
def lockin(t, y, ta, tb):
    m = (t >= ta) & (t < tb); tt = t[m] - ta; w = 2 * np.pi / (2 * H)
    X = np.column_stack([np.ones_like(tt), tt, tt ** 2, np.cos(w * tt), np.sin(w * tt)])
    c, *_ = np.linalg.lstsq(X, y[m], rcond=None)
    return complex(c[3], -c[4])
def lockin_laps(t, y, ta, tb):
    out = []
    for c in range(M):
        a = ta + c * 2 * H; out.append(lockin(t, y, a, a + 2 * H))
    return out
rng = np.random.default_rng(1)
offs = rng.uniform(0, 1, 34)
for passes in [(7810, 7811)]:
    res = {}
    allP = []; allT = []; allm = []; tshift = 0
    for p in passes:
        order = [b for b in BLOCKS if b != "f32randn"]; random.Random(p).shuffle(order); order.append("f32randn")
        P, marks = session(order); allP.append(P); allm += [(b, a + tshift, e + tshift) for b, a, e in marks]; tshift += len(P) * DT
    P = np.concatenate(allP); T = simulate(P) + 55.0; t = np.arange(len(P)) * DT
    # 34 sensors, each truncated to whole degrees, offsets uniform; plus 0.05 C white noise per sensor
    sens = np.floor(T[:, None] + offs[None, :] + rng.normal(0, 0.05, (len(T), 34)))
    Tm = sens.mean(axis=1)
    print(f"session {len(P)*DT/60:.1f} min of blocks, peak die {T.max():.1f} C")
    Href = []
    for b, ta, tb in allm:
        k, z = BLOCKS[b]; D = S[k] - S[z]
        hp = lockin(t, P, ta, tb); ht = lockin(t, T, ta, tb); hm = lockin(t, Tm, ta, tb)
        res.setdefault(b, []).append((abs(ht), abs(hm), ht / hp, hm / hp, abs(hp), D))
    href = np.mean([abs(v[3]) for v in res["f32randn"]])
    for b, v in res.items():
        v = np.array(v, dtype=complex)
        Ht = np.abs(v[:, 2]).mean(); Hm = np.abs(v[:, 3]).mean()
        print(f"  {b:9s} D {v[0,5].real:6.3f} W  board fund {abs(v[:,4]).mean():6.3f} W  T fund {abs(v[:,0]).mean():6.3f} C (true) {abs(v[:,1]).mean():6.3f} C (34-sensor)  H {Ht:.4f} / {Hm:.4f} C/W  ratio to ref {Hm/href:.3f}  phase {np.degrees(np.angle(v[:,3])).mean():6.1f}")
