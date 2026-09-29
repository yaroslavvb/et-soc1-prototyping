# TAU dry-run stubs: the shared virtual clock and the simulated card. Never opens a device.
# Virtual time runs 1/TAU_STUB_SCALE times faster than the wall clock, from the epoch the block writes into
# $TAU_STUB_STATE/epoch ("<wall ms> <virtual ms>"), so the stubs' timestamps look like a real card's.
# stubs/simulate.py uses the same model without the clock (sample_row, burst_record, launches), for calibration.
import json, math, os, random, time

ST = os.environ.get("TAU_STUB_STATE", "")
SCALE = float(os.environ.get("TAU_STUB_SCALE", "0.1"))
FAIL = set(filter(None, os.environ.get("TAU_STUB_FAIL", "").split(",")))
# The simulated cards, from the offline fits (tools/claims-v3/tau/offline.json):
#   tau      each channel's first-order filter (s)
#   pass     the SP pass (s) under a 10 Hz ("100") and a 20 Hz ("50") sampler (E41)
#   extra_d  the rails' delay beyond one pass (s): the offline one-pass fit's d (aifoundry1-c1's SRAM rail +0.03)
#   creep    board_w's rise during a burst, per second, as a fraction of its step: the median in-burst drift of
#            board_w on the catalogue's 15-40 W steps (offline.py --drift). Only board_w (the board's instantaneous
#            input power) creeps: offline, the deconvolved rails and board_avg_w stay flat during a burst (in-burst
#            slope 0.000-0.003 /s against board_w's 0.012-0.021 /s), so the averaged channels get a square input
#   resid    [the offline fit residual of that card and channel (offline.json, of the step), the simulator's own
#            residual with no added noise (calibrate.py match)]
#   noise_w  white noise (W) added to each SP pass's reading, so that the simulated block's fit residual (P4a) equals
#            the offline one (calibrate.py match; 0 where the simulator's own residual is already larger: aifoundry1-c1's
#            minion and board_avg); board_w: its scatter inside a burst (0.4-0.5% of a 20 W step)
# TAU_STUB_NOISE=k (default 1) sets the added noise so that the residual is k times the offline one (sigma() below);
# TAU_STUB_EXTRA_D=0 and TAU_STUB_CREEP=0 turn those off.
CARDS = {
    "aifoundry3": {"tau": {"minion_w": 1.04, "sram_w": 1.03, "noc_w": 1.04, "board_avg_w": 1.05},
                   "pass": {100: 0.263, 50: 0.320},
                   "extra_d": {"minion_w": -0.01, "sram_w": 0.0, "noc_w": -0.02},
                   "creep": 0.0113,
                   "resid": {"minion_w": [0.01023, 0.00825], "sram_w": [0.01104, 0.00823], "noc_w": [0.00979, 0.00822],
                             "board_avg_w": [0.00806, 0.0079]},
                   "noise_w": {"minion_w": 0.1099, "sram_w": 0.0653, "noc_w": 0.0495, "board_avg_w": 0.0351, "board_w": 0.1}},
    "aifoundry1-c1": {"tau": {"minion_w": 1.06, "sram_w": 0.53, "noc_w": 1.07, "board_avg_w": 1.11},
                      "pass": {100: 0.158, 50: 0.188},
                      "extra_d": {"minion_w": -0.01, "sram_w": 0.03, "noc_w": -0.02},
                      "creep": 0.0208,
                      "resid": {"minion_w": [0.00767, 0.00797], "sram_w": [0.01355, 0.01138], "noc_w": [0.00827, 0.00795],
                                "board_avg_w": [0.00724, 0.00769]},
                      "noise_w": {"minion_w": 0.0, "sram_w": 0.063, "noc_w": 0.0204, "board_avg_w": 0.0, "board_w": 0.1}},
    "aifoundry2": {"tau": {"minion_w": 1.06, "sram_w": 1.02, "noc_w": 1.05, "board_avg_w": 1.08},
                   "pass": {100: 0.156, 50: 0.187},
                   "extra_d": {"minion_w": 0.0, "sram_w": 0.02, "noc_w": 0.0},
                   "creep": 0.019,
                   "resid": {"minion_w": [0.01058, 0.00787], "sram_w": [0.01104, 0.00819], "noc_w": [0.0119, 0.00812],
                             "board_avg_w": [0.00851, 0.00788]},
                   "noise_w": {"minion_w": 0.143, "sram_w": 0.0604, "noc_w": 0.0742, "board_avg_w": 0.067, "board_w": 0.1}}}
STEP_W = {"minion_w": 20.5, "sram_w": 7.9, "noc_w": 7.9, "board_avg_w": 22.0}   # each channel's typical step in a block
CARD_NAME = os.environ.get("TAU_STUB_CARD", "aifoundry3")
CARD = CARDS[CARD_NAME]
NOISE = float(os.environ.get("TAU_STUB_NOISE", "1"))
EXTRA_D = os.environ.get("TAU_STUB_EXTRA_D", "1") != "0"
CREEP = os.environ.get("TAU_STUB_CREEP", "1") != "0"
RAW_NOISE = False
IDLE = {"minion_w": 8.0, "sram_w": 2.3, "noc_w": 2.6, "board_w": 26.0}
AMP = {"M": {"minion_w": 20.5, "sram_w": 0.25, "noc_w": 0.15}, "H": {"minion_w": 10.0, "sram_w": 0.2, "noc_w": 0.07},
       "D": {"minion_w": 1.2, "sram_w": 7.9, "noc_w": 7.9}}
LAUNCH_MS, GAP_MS = 400.5, 1.5        # one enercat launch of the catalogue's window, and the host's gap between two


def vnow():
    w0, v0 = map(float, open(os.path.join(ST, "epoch")).read().split())
    return v0 + (time.time() * 1000 - w0) / SCALE


def vsleep(ms):
    time.sleep(ms / 1000.0 * SCALE)


def counter(name):
    p = os.path.join(ST, name)
    k = (int(open(p).read()) if os.path.exists(p) else 0) + 1
    open(p, "w").write(str(k))
    return k


def bursts():
    p = os.path.join(ST, "bursts.jsonl")
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def launches(secs):
    """enercat_host's loop: launch while less than --seconds has passed (2 s -> 5 launches, 3 s -> 8, 4 s -> 10)."""
    n, t = 0, 0.0
    while t < secs * 1000:
        n += 1; t += LAUNCH_MS + GAP_MS
    return max(n, 1)


def burst_record(on_ms, secs, kind):
    n = launches(secs)
    return {"on": on_ms, "off": on_ms + n * LAUNCH_MS + (n - 1) * GAP_MS, "kind": kind, "amp": AMP[kind], "n": n}


def _sq(t, a, e, tau, k):
    """A unit square on [a, e) whose height creeps as 1 + k (t - a), seen through a first-order filter of tau
    (tau None: the square itself)."""
    if tau is None:
        return (1 + k * (t - a)) if a <= t < e else 0.0
    if t <= a:
        return 0.0
    u = min(t, e) - a
    s = -math.expm1(-u / tau)
    y = s + k * (u - tau * s)
    return y * math.exp(-(t - e) / tau) if t > e else y


def power(t_s, ch, bs, tau=None, creep=False):
    """True power (tau None) or its first-order average at virtual time t_s (s); creep: board_w's in-burst rise."""
    v = IDLE.get(ch, 0.0)
    k = CARD["creep"] if (CREEP and creep) else 0.0
    for b in bs:
        a, e = b["on"] / 1e3, b["off"] / 1e3
        amp = b["amp"].get(ch, 0.0) if ch != "board_w" else 1.2 * sum(b["amp"].values())
        v += amp * _sq(t_s, a, e, tau, k)
    return v


def sigma(ch):
    """The added noise (W) for which the simulated residual is NOISE times the offline one: r^2 = r0^2 + (s / A)^2."""
    if RAW_NOISE or ch not in CARD["resid"]:       # calibrate.py match sets noise_w itself
        return CARD["noise_w"].get(ch, 0.0) * (NOISE if RAW_NOISE else 1.0)
    t, r0 = CARD["resid"][ch]; s1 = CARD["noise_w"][ch]
    want = (NOISE * t) ** 2 - r0 ** 2
    if want <= 0:
        return 0.0
    A = STEP_W[ch]                                 # the step the residual is relative to; where the match added a
    if s1 > 0 and t * t - r0 * r0 >= 0.2 * t * t:  # clear share of it, the step it implies (so that NOISE 1 gives s1)
        A = s1 / math.sqrt(t * t - r0 * r0)
    return A * math.sqrt(want)


def noise(ch, tp, salt=0):
    """The same noise for every sample of one SP pass (the SP copies each value once per pass)."""
    s = sigma(ch)
    return random.Random(int(round(tp * 1e3)) * 7919 + len(ch) * 104729 + salt).gauss(0, s) if s > 0 else 0.0


def sample_row(ts_ms, every, bs, hot=57, fixed_delay=None, phase=0.0, salt=0, temp=True):
    """One ettelem-format line at virtual time ts_ms under a sampler of every ms. The SP copies its values once per
    pass (P = the card's pass at that rate, from phase); board_w is the true power at the pass, board_avg_w its
    first-order average, and the three rails the first-order average at the previous pass (one pass late, plus the
    card's extra_d), or (fixed_delay, the rival theory) a fixed time late."""
    P = CARD["pass"].get(every, 0.263)
    ts = ts_ms / 1e3
    tp = phase + math.floor((ts - phase) / P) * P
    s = {"t_ms": int(ts_ms), "took_ms": 22, "since_reset_ms": -1,
         "board_w": round(power(tp, "board_w", bs, creep=True) + noise("board_w", tp, salt), 2),
         "sp": {"board_avg_w": round(power(tp, "board_w", bs, CARD["tau"]["board_avg_w"]) + noise("board_avg_w", tp, salt), 2),
                "board_min_w": 24.6, "board_max_w": 53.6},
         "mhz": {"minion": 600, "noc": 400, "ddr": 933}}
    if temp:
        s["temp_c"] = {"pmic": hot, "ioshire": [hot, hot - 3, hot + 6], "minshire": [hot, hot - 3, hot + 8]}
    for ch in ("minion_w", "sram_w", "noc_w"):
        late = fixed_delay if fixed_delay is not None else P + (CARD["extra_d"][ch] if EXTRA_D else 0.0)
        v = power(tp - late, ch, bs, CARD["tau"][ch]) + noise(ch, tp, salt) + random.Random(int(tp * 1e3) * 7 + len(ch)).gauss(0, 0.004)
        s["sp"][ch] = [round(v, 3), 1.0, 30.0]
    return s
