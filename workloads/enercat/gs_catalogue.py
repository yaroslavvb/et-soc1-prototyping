#!/usr/bin/env python3
"""The gather/scatter configurations of V3-GS (E48): the energy set E, the rate set R, the check set C, the smoke.

    python3 workloads/enercat/gs_catalogue.py [--set E|R|C|smoke|all] [--count] [--names]
    python3 workloads/enercat/gs_catalogue.py --sim-suite <file> [--sim-set C]   # the simulator versions (sys_emu)

configs(set) returns the same {"cfg", "args"} dicts as run_catalogue.configs(), so tools/claims-v3/cat/
run_catalogue_t10.py runs them unchanged (tools/claims-v3/gs/run_gs_t10.py puts this list in its place). There is no
"prefill": the kernel writes its own scratchpad tables at every launch, and DRAM tables are filled by DMA.

Names: gs/<set>/<op>/<target>-<WS>/<pattern>/<data>/h<harts>/m<mask>/n<minions>, every field always present.
  target  dram (a private table per hart), scp (the hart's 16 KB of its own shire's scratchpad), rscp (of a shire two
          hops away, at most two readers per target, each its own region), shire (one 256 KB counter table per
          shire), chip (one 8 MB counter table)
  n       n1024 (every minion), nS32 (the 32 minions of shire 0), nX32 (minion 0 of every shire), nM1 (one minion)
No name is a prefix of another (the runner selects by prefix); check_names() asserts it.
The C set holds one verify launch per E and R configuration (sets CE and CR: the same name with the set CE/CR) and
the semantic probe (CP).
"""
import argparse
import json
import sys

WS_NAME = {256: "256B", 512: "512B", 1024: "1K", 4096: "4K", 8192: "8K", 16384: "16K", 65536: "64K", 262144: "256K"}
TILE = {"unit": 256, "s2": 512, "s4": 1024, "s16": 4096, "line": 512, "rand": 4096, "bcast": 512}
MIN = {"n1024": [], "nS32": ["--shires", "0x1"], "nX32": ["--minions", "0x1"], "nM1": ["--shires", "0x1", "--minions", "0x1"]}
SCALAR = ("flw", "fsw", "amoaddl.w", "amoaddg.w")
RESTRICTED = ("fg32w.ps", "fg32h.ps", "fg32b.ps", "fsc32w.ps", "fsc32h.ps", "fsc32b.ps")
ATOMIC = ("famoaddl.pi", "famoaddg.pi", "amoaddl.w", "amoaddg.w")


def ntiles(op, target, ws, pattern):
    if target == "shire":
        ws = 256 * 1024
    elif target == "chip":
        ws = 8 * 1024 * 1024
    if op in RESTRICTED:
        tile = 256
    elif op in SCALAR:
        tile = 512 if (op in ("flw", "fsw") and ws < 4096) else 4096
    elif op == "probe":
        return 1
    else:
        tile = min(TILE[pattern], ws)
    return max(1, ws // tile)


def verify_visits(op, target, ws, pattern):
    """Tile visits of a verify launch: every tile twice up to 64 visits; 8 on the shared counter tables."""
    if target in ("shire", "chip"):
        return 8
    if op == "probe":
        return 1
    return min(64, max(8, 2 * ntiles(op, target, ws, pattern)))


def mk(set_, op, target, ws=4096, pattern="rand", data="random", harts=2, mask=0xFF, n="n1024", verify=None):
    wsname = {"shire": "256K", "chip": "8M"}.get(target, WS_NAME.get(ws, str(ws)))
    if op in ATOMIC:
        data = "zeros"   # counters start at zero; addend 1
    name = f"gs/{set_}/{op}/{target}-{wsname}/{pattern}/{data}/h{harts}/m{mask:02x}/{n}"
    args = ["--pattern", f"gs.{op}", "--gs-index", pattern, "--operands", data, "--harts", str(harts), "--mask", hex(mask)]
    if target == "dram":
        args += ["--ws", str(ws)]
    elif target == "scp":
        args += ["--scp", "--ws", str(ws)]
    elif target == "rscp":
        args += ["--hop-distance", "2", "--uniq-regions", "--ws", str(ws)]
    elif target in ("shire", "chip"):
        args += ["--share", target]
    else:
        raise ValueError(target)
    args += MIN[n]
    c = {"cfg": name, "args": args, "op": op, "target": target, "ws": ws, "pattern": pattern, "data": data,
         "harts": harts, "mask": mask, "n": n}
    if verify:
        c["args"] = args + ["--verify", str(verify_visits(op, target, ws, pattern))]
    return c


K = 1024


def set_E():
    E = []
    add = lambda *a, **k: E.append(mk("E", *a, **k))
    # G: working-set sweep (rand), zeros at three levels
    for ws in (256, 512, 1 * K, 4 * K, 16 * K, 64 * K, 256 * K):
        add("fgw.ps", "dram", ws)
    for ws in (512, 4 * K, 256 * K):
        add("fgw.ps", "dram", ws, data="zeros")
    # G: pattern sweep at L1 (512 B) and L2 (4 KB); DRAM patterns
    for ws in (512, 4 * K):
        for pat in ("unit", "s2", "s4", "s16", "line", "bcast"):
            add("fgw.ps", "dram", ws, pat)
    for pat in ("unit", "s16"):
        add("fgw.ps", "dram", 256 * K, pat)
    # G: own and remote scratchpad
    add("fgw.ps", "scp", 16 * K, "unit")
    add("fgw.ps", "scp", 16 * K, "s16")
    add("fgw.ps", "scp", 16 * K, "rand")
    add("fgw.ps", "scp", 16 * K, "rand", data="zeros")
    add("fgw.ps", "rscp", 16 * K, "unit")
    add("fgw.ps", "rscp", 16 * K, "rand")
    # G: hart 0 only (L2 at 8 KB per minion: the same total), masks, element size
    add("fgw.ps", "dram", 512, harts=1)
    add("fgw.ps", "dram", 8 * K, harts=1)
    add("fgw.ps", "dram", 256 * K, harts=1)
    for ws in (512, 4 * K):
        for m in (0x0F, 0x01):
            add("fgw.ps", "dram", ws, mask=m)
    for ws in (512, 4 * K):
        for op in ("fgh.ps", "fgb.ps"):
            add(op, "dram", ws)
    # GL / GG
    add("fgwl.ps", "dram", 4 * K)
    add("fgwl.ps", "dram", 4 * K, "unit")
    add("fgwl.ps", "scp", 16 * K)
    add("fgwg.ps", "dram", 4 * K)
    add("fgwg.ps", "dram", 256 * K)
    add("fgwg.ps", "rscp", 16 * K)
    # G32
    for ws in (512, 4 * K):
        add("fg32w.ps", "dram", ws)
    add("fg32w.ps", "scp", 16 * K)
    add("fg32w.ps", "dram", 256 * K)
    add("fg32b.ps", "dram", 512)
    # S: working-set sweep, zeros, patterns
    for ws in (512, 4 * K, 16 * K, 256 * K):
        add("fscw.ps", "dram", ws)
    for ws in (512, 4 * K):
        add("fscw.ps", "dram", ws, data="zeros")
    for ws in (512, 4 * K):
        for pat in ("unit", "s16", "line", "bcast"):
            add("fscw.ps", "dram", ws, pat)
    add("fscw.ps", "scp", 16 * K, "unit")
    add("fscw.ps", "scp", 16 * K, "rand")
    add("fscw.ps", "rscp", 16 * K, "rand")
    add("fscw.ps", "dram", 256 * K, "unit")
    add("fscw.ps", "dram", 512, harts=1)
    add("fscw.ps", "dram", 8 * K, harts=1)
    for ws in (512, 4 * K):
        for op in ("fsch.ps", "fscb.ps"):
            add(op, "dram", ws)
    # SL / SG
    add("fscwl.ps", "dram", 4 * K)
    add("fscwl.ps", "scp", 16 * K)
    add("fscwg.ps", "dram", 4 * K)
    add("fscwg.ps", "dram", 256 * K)
    add("fscwg.ps", "rscp", 16 * K)
    # S32
    for ws in (512, 4 * K):
        add("fsc32w.ps", "dram", ws)
    add("fsc32w.ps", "scp", 16 * K)
    # B: scalar baselines on the same address stream
    for tgt, ws in (("dram", 512), ("dram", 4 * K), ("scp", 16 * K), ("dram", 256 * K)):
        add("flw", tgt, ws)
    for tgt, ws in (("dram", 512), ("dram", 4 * K), ("scp", 16 * K)):
        add("fsw", tgt, ws)
    # U: scatter-add four ways
    for tgt, ws in (("dram", 512), ("dram", 4 * K), ("scp", 16 * K), ("dram", 256 * K)):
        add("upd", tgt, ws)
    add("famoaddl.pi", "shire")
    add("famoaddl.pi", "dram", 512, "bcast")
    add("famoaddg.pi", "chip")
    add("famoaddg.pi", "dram", 512, "bcast")
    add("amoaddl.w", "shire")
    add("amoaddg.w", "chip")
    return E


def set_R():
    R = []
    add = lambda *a, **k: R.append(mk("R", *a, **k))
    levels = (("dram", 512), ("dram", 4 * K), ("scp", 16 * K), ("rscp", 16 * K), ("dram", 256 * K))
    for tgt, ws in levels:
        add("fgw.ps", tgt, ws, harts=1, n="nM1")
        add("fgw.ps", tgt, ws, harts=2, n="nM1")
        add("fgw.ps", tgt, ws, n="nS32")
        add("fgw.ps", tgt, ws, n="nX32")
    for tgt, ws in (("dram", 512), ("dram", 4 * K), ("scp", 16 * K), ("dram", 256 * K)):
        add("fscw.ps", tgt, ws, harts=1, n="nM1")
        add("fscw.ps", tgt, ws, n="nS32")
        add("fscw.ps", tgt, ws, n="nX32")
    for op, ws in (("fgwl.ps", 4 * K), ("fgwg.ps", 4 * K), ("fgwg.ps", 256 * K)):
        add(op, "dram", ws, harts=1, n="nM1")
        add(op, "dram", ws, n="nS32")
    # GS-UC needs h2 against h1 on one minion (strict per-thread order of L1-bypassing ops): not in the design's
    # 56, added before any data
    add("fgwl.ps", "dram", 4 * K, harts=2, n="nM1")
    for op, tgt in (("famoaddl.pi", "shire"), ("famoaddg.pi", "chip")):
        add(op, tgt, harts=1, n="nM1")
        add(op, tgt, n="nS32")
    for ws in (512, 4 * K):
        for pat in ("unit", "s2", "s4", "s16", "line", "bcast"):
            add("fgw.ps", "dram", ws, pat, harts=1, n="nM1")
    for ws in (4 * K, 256 * K):
        add("flw", "dram", ws, harts=1, n="nM1")
    return R


def set_C():
    C = []
    for src in (set_E(), set_R()):
        for c in src:
            set_ = "CE" if c["cfg"].startswith("gs/E/") else "CR"
            C.append(mk(set_, c["op"], c["target"], c["ws"], c["pattern"], c["data"], c["harts"], c["mask"], c["n"], verify=True))
    C.append(mk("CP", "probe", "dram", 4096, "rand", "random", 2, 0xFF, "n1024", verify=True))
    return C


def set_smoke():
    S = []
    for op, tgt, ws in (("fgw.ps", "dram", 512), ("fscw.ps", "scp", 16 * K), ("famoaddg.pi", "chip", 0), ("fgw.ps", "dram", 256 * K)):
        S.append(mk("SM", op, tgt, ws))
        S.append(mk("SMC", op, tgt, ws, verify=True))
    return S


def configs(set_="E"):
    s = {"E": set_E, "R": set_R, "C": set_C, "smoke": set_smoke}
    if set_ == "all":
        out = []
        for k in ("C", "E", "R", "smoke"):
            out += s[k]()
        return check_names(out)
    return check_names(s[set_]())


def check_names(cfgs):
    names = [c["cfg"] for c in cfgs]
    assert len(set(names)) == len(names), "duplicate configuration names"
    for n in names:
        hits = [m for m in names if m.startswith(n)]
        assert hits == [n], f"{n} is a prefix of {hits}"
    return cfgs


def check_of(name):
    """The C configuration that verifies an E or R configuration (gs/E/... -> gs/CE/...)."""
    parts = name.split("/")
    parts[1] = {"E": "CE", "R": "CR"}[parts[1]]
    return "/".join(parts)


# ---------------- simulator versions ----------------
def sim_line(c, visits=None, timed=False, multi=False):
    """A --suite line for sys_emu. Minions: one minion stays one (0x1); every other configuration runs two minions
    (0x3) of shire 0, or with multi=True two shires (0 and 2: --shires 0x5) for n1024 and nX32, so the rank, the
    shared-table and the remote-target logic see more than one shire. Verify visits are capped (8); timed=True gives
    every configuration one short timed launch (--seconds 0.0001 --window 30000) instead of its --verify."""
    a = list(c["args"])
    out, i = [], 0
    while i < len(a):
        if a[i] in ("--shires", "--minions"):
            i += 2
            continue
        if a[i] == "--verify":
            if not timed:
                out += ["--verify", str(min(int(a[i + 1]), visits or 8))]
            i += 2
            continue
        out.append(a[i])
        i += 1
    if timed:
        out += ["--seconds", "0.0001", "--window", "30000"]
    n = c["n"]
    if n == "nM1":
        sm = ["--shires", "0x1", "--minions", "0x1"]
    elif multi and n in ("n1024", "nX32"):
        sm = ["--shires", "0x5", "--minions", "0x3" if n == "n1024" else "0x1"]
    else:
        sm = ["--shires", "0x1", "--minions", "0x3"]
    return f"label={c['cfg']} " + " ".join(out + sm)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="E")
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--names", action="store_true")
    ap.add_argument("--sim-suite")
    ap.add_argument("--sim-set", default="C")
    ap.add_argument("--sim-visits", type=int, default=8)
    ap.add_argument("--sim-timed", action="store_true")
    ap.add_argument("--sim-multi", action="store_true")
    a = ap.parse_args()
    if a.sim_suite:
        cs = []
        for st in a.sim_set.split(","):
            cs += configs(st)
        open(a.sim_suite, "w").write("\n".join(sim_line(c, a.sim_visits, a.sim_timed, a.sim_multi) for c in cs) + "\n")
        print(f"{len(cs)} suite lines -> {a.sim_suite}")
        sys.exit(0)
    cs = configs(a.set)
    if a.count:
        print(len(cs))
    elif a.names:
        print("\n".join(c["cfg"] for c in cs))
    else:
        print(json.dumps([{"cfg": c["cfg"], "args": c["args"]} for c in cs], indent=1))
