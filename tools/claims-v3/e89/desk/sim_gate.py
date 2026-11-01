"""Desk simulation: E78's gated frame with a sustained window W, on the Foster chain (11-thermal-model.md)."""
import numpy as np, random, sys
TAU = np.array([1.5, 4, 60, 150, 400, 2500.0]); R = np.array([0.106, 0.050, 0.234, 0.136, 0.860, 0.081])
KLEAK = 0.20; DT = 0.1; IDLE_T = 50.0
S = {"Zf": 1.986, "Zi": 2.605, "i8full": 9.648, "i8gauss": 9.161, "i8small": 8.628, "i8sp50": 8.061, "i8neg1": 4.176,
     "f32ones": 10.288, "f32sp90": 2.509, "f32sp50": 9.243, "f16wsp50": 9.090, "f32randn": 26.701}
class Die:
    def __init__(s):
        s.x = np.zeros(6); s.t = 0.0; s.log = []
    def T(s): return IDLE_T + s.x.sum()
    def step(s, p, n):
        for _ in range(n):
            ptot = p + KLEAK * s.x.sum()
            s.x += DT / TAU * (R * ptot - s.x); s.t += DT
            s.log.append((s.t, s.T(), p))
def launch(d, item, secs):   # one process: 0.7 s start-up at idle power, then secs at S
    d.step(0.0, 7); d.step(S[item], int(secs / DT))
def run_session(order, W, G, launches, seed=0):
    d = Die(); d.step(0.0, 600)        # 60 s idle start
    out = []; heats = 0; tcard0 = d.t
    for item in order:
        # approach: heat to G+1 if below, wait to fall to G, then 2 s quiet with T <= G
        while True:
            while d.T() < G + 1.0:
                launch(d, "f32randn", 2.0); heats += 1
            while d.T() > G: d.step(0.0, 1)
            d.step(0.0, 20)
            if d.T() >= G - 0.5: break
        T0 = d.T(); t0 = d.t + 0.7
        n_l = launches
        for i in range(n_l): launch(d, item, W / n_l)
        a = np.array(d.log); tt = a[:, 0]; TT = a[:, 1]
        w2 = (tt >= t0 + 1) & (tt < t0 + 3); wW = (tt >= t0 + W - 5) & (tt < t0 + W)
        out.append((item, TT[w2].mean() - T0, TT[wW].mean() - T0))
    return out, (d.t - tcard0) / 60, heats
items = ["Zf", "Zi", "i8full", "i8gauss", "i8small", "i8sp50", "i8neg1", "f32ones", "f32sp90", "f32randn"]
for W, nl in [(26, 3), (44, 5), (60, 7)]:
    for G in (58.0, 60.0):
        res = {}; mins = 0; H = 0
        for p in range(2):
            order = items[:]; random.Random(7810 + p).shuffle(order)
            o, m, h = run_session(order, W, G, nl); mins += m; H += h
            for it, a2, aW in o: res.setdefault(it, []).append((a2, aW))
        print(f"== W {W} s ({nl} launches), gate {G}: 2 passes {mins:.1f} min, {H} heater launches")
        cW = np.mean([v[1] for v in res["f32randn"]]) / S["f32randn"]; c2 = np.mean([v[0] for v in res["f32randn"]]) / S["f32randn"]
        for it in items:
            v = np.array(res[it]); s_ = S[it]
            print(f"   {it:9s} S {s_:6.3f}  2s: {v[:,0].mean():6.3f} C ({v[:,0].mean()/s_:.3f} C/W, x ref {v[:,0].mean()/s_/c2:.2f}, passes {v[0,0]:.3f}/{v[1,0]:.3f})"
                  f"   W: {v[:,1].mean():6.3f} C ({v[:,1].mean()/s_:.3f} C/W, x ref {v[:,1].mean()/s_/cW:.2f}, passes {v[0,1]:.3f}/{v[1,1]:.3f})")
