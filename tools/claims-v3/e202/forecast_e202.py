#!/usr/bin/env python3
"""E202's frozen forecasts: one pass over MNIST in int8 on aifoundry3 card 0 at 600 MHz (E202.md sections 4-6).

    python3 -I -B tools/claims-v3/e202/forecast_e202.py            # write forecast-e202.json and forecast-e202.txt
    python3 -I -B tools/claims-v3/e202/forecast_e202.py --check    # recompute and compare with the committed files

The load ledger v2 as frozen (tools/ledger/ledger_v2.py, frozen-v2.json at 06d60fa2: every constant, every term
function, predict() itself) prices a load built from E202's COUNTED events: the exact launch accounting of the
program's counts (docs/reports/data/2026-11-16-q193-mnistmlp/counts/counts-summary.json: per group at 32 minions a
shire, and per launch), the tile loop's instructions from the committed disassembly (classified by the counter's own
parser, tools/counter/count_kernel.py), and the operand statistics of the tile pairs the kernel issues
(desk/tiles-e202.json). Three things are added in memory, beside the frozen constants, and nothing frozen is changed:
  1. the tensor-data price D of E202's ten layer kinds (two weight configurations x five layers), by THE KINDS RULE:
     the three committed int8 kinds nearest the layer's mean tile numbers (g, the share of gate decisions the int8 zero
     gate turns off, and b / b_full, the input-bus bits flipped an op over int8.full's), each priced by M10's held-out
     prediction exactly as frozen-v2.json's kinds are (tools/ledger/freeze_ledger_v2.py m10_heldout and kind_entry,
     imported unchanged); the band widened to M10's int8 band_k times the rule's own leave-one-out rms over the 97
     committed aifoundry3 int8 kinds (M10's own features need the toggle bench, which is not on this box);
  2. the instruction classes' prices: one catalogue row a counted class (E189.md section 6's v2c rows: aifoundry3's
     random mean, the row's band), vector integer as frozen-v2.json's vec_int; each class's hart-cycles are its count
     over the ledger's issue_rate, so predict()'s point is count x price and its band the ledger's own;
  3. the seconds (section 5): a cycle model of a shire-round from the counted events, two-sided by rule.
The given-seconds formula (given()) is predict() at a burst's measured kernel seconds t_k (the awake term), wall
seconds t_w (the card at rest) and starting die T0; nothing is refitted at scoring.

Standard library only. Floats in the written files are rounded to 6 significant digits.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import math
import os
import platform
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
F_HZ = 600e6
N_MIN = 1024                       # minions; hart 0 of each works, hart 1 returns at once (as in the catalogue's runs)
P_SHIRE, N_SHIRES = 32, 32
T0_FORECAST, T0_BAND = 55.0, (52.0, 60.0)
SIG = 6
R_REGISTERED = 96
R_ALLOWED = (16, 32, 48, 64, 80, 96)
GROUPS_PER_PASS, IMAGES_PER_PASS = 3750, 60000
OPS_PER_GROUP, CHUNKS = 10892, 449
OPS_LAYER = [1456, 3136, 3136, 3136, 28]
MACS_ISSUED_PER_IMAGE, MACS_REAL_PER_IMAGE = 11153408, 11056640
TILE = 1024
INPUT_BYTES_PER_GROUP = 13 * TILE
FSWG_BYTES_PER_GROUP = 114688
LABEL_LINE = 64
WEIGHT_TILES = 10892
L2_LINES_PER_S = 27.4e9            # energy manual 04 (E48): L1 misses served at 27.4 G lines/s over the chip
H1_OVER_H2 = ("add", 0.581, 0.3727)  # the one row the catalogue measured with one hart and with both (E189 5.1)
STAGES = ("scp", "dram")
CONFIGS = ("trained", "random")
INTERPRETER = "/usr/bin/python3 %s wrote the files (named)" % platform.python_version()

DATA = "docs/reports/data/2026-11-16-q193-mnistmlp"
PINS = {
    "tools/ledger/ledger_v2.py": "214cf7a49c1edae206ae34133bb6e2dc1f99a414e367b4617b2607f451cd2886",
    "docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json": "59ff911705137e5486efcb15c482919e3d257f800193bcc9f1d78ee7283753ce",
    "tools/ledger/freeze_ledger_v2.py": None,
    "docs/reports/data/2026-11-04-q142m-m10/m10.json": None,
    "docs/reports/data/2026-11-04-q142m-m10/rows-m10.json": None,
    "docs/reports/data/2026-09-23-energy-manual/catalogue.json": "1186a9764838330369bc87f90f9ed4aed03d9d1373fd3185a8f107cf2eb1a7ae",
    "workloads/ledger/ledger_estimate.py": "e3670e78da97107c067512450e57698680be4a1def1a0d01a232d4f360eef2f2",
    "tools/counter/count_kernel.py": "089f354c12912026e70e0ee0c718454d1b079292e456c830d9b590c66111bff2",
    "workloads/nocroute/meshmap.py": None,
    "workloads/sparseparity/tools/cycle_model.py": None,
    DATA + "/counts/counts-summary.json": None,
    DATA + "/build/mnistmlp.dis": None,
    DATA + "/SHA256SUMS": None,
    "tools/claims-v3/e202/desk/tiles-e202.json": None,
}
PIN_FILE = os.path.join(HERE, "desk", "pins-e202.json")   # the None entries above, frozen by the first write
# v2c: one catalogue row per counted class (E189.md section 6; tools/claims-v3/e189/forecast_e189.py V2C_ROWS)
V2C_ROWS = {"scalar_int": "add", "load": "lw", "store": "sw", "branch_taken": "beq_taken",
            "branch_not_taken": "bne_nottaken", "jump": "jal", "mask_broadcast": "fbci.pi", "float_int_xfer": "fmv.x.w",
            "int_muldiv": "mul", "system": "csrr_fccnb", "sync": "fence", "atomic_local": "amoaddl.w"}
PRICED_ELSEWHERE = {"tensor": "the tensor term (M10's kernel term) and the scratchpad-load bytes",
                    "store_past_l1": "the activation stores' scratchpad-store bytes (fswg.ps, 32 B each)"}
# the seconds' rows for the classes the catalogue has no row of their own for (section 5)
TIME_ROWS = dict(V2C_ROWS, tensor="csrr_fccnb", store_past_l1="fsw.ps")
# the tile loop in the committed disassembly: run.constprop.0, 0x8005801d04 .. 0x8005801d62 (one op); the last op of a
# chunk skips 0x8005801d10 .. 0x8005801d2a (the next A load and its wait) and takes the first branch, not the second
LOOP_FIRST, LOOP_LAST = 0x8005801d04, 0x8005801d62
LOOP_SKIP = (0x8005801d10, 0x8005801d2a)
# the cycle model's ends (section 5): point, fast, slow
C_OP_SLOW = 511.94 * 1.15          # E37: private int8 tiles, 511.94 cycles an op (4.00 B a minion-cycle), plus 15 %
BARRIER = {"point": 233.0 + 300.0, "fast": 233.0, "slow": 233.0 + 600.0}
DRAM_GBS = {"point": 76.0, "fast": None, "slow": 70.0}
BYTES_PER_ROUND_SHIRE_EXTRA = None  # computed: chunk copies landing + input copies landing (cycle_model's U)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_module(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REPO, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def r6(x):
    if isinstance(x, dict):
        return {k: r6(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [r6(v) for v in x]
    if isinstance(x, float):
        if x == 0.0 or not math.isfinite(x):
            return x
        return float(f"{x:.{SIG - 1}e}")
    return x


def check_pins(write=False):
    frozen = {}
    if os.path.exists(PIN_FILE) and not write:
        frozen = json.load(open(PIN_FILE))
    got = {p: sha(os.path.join(REPO, p)) for p in PINS}
    bad = [p for p, h in PINS.items() if h is not None and got[p] != h]
    bad += [p for p, h in frozen.items() if got.get(p) != h]
    if bad:
        sys.exit("refused: pinned inputs differ: " + ", ".join(bad))
    if write:
        with open(PIN_FILE, "w") as f:
            json.dump({p: got[p] for p, h in PINS.items() if h is None}, f, indent=1, sort_keys=True)
            f.write("\n")
    elif not frozen:
        sys.exit("refused: no desk/pins-e202.json")
    # the program's data folder as committed (its own SHA256SUMS, itself pinned)
    d = os.path.join(REPO, DATA)
    for ln in open(os.path.join(d, "SHA256SUMS")):
        if ln.strip():
            h, p = ln.split(None, 1)
            if sha(os.path.join(d, p.strip())) != h:
                sys.exit(f"refused: {DATA}/{p.strip()} differs from its SHA256SUMS")
    return got


# ---------------------------------------------------------------- the launch, exactly (counts_scale.py's accounting)
def launch(R, stage="scp"):
    groups = GROUPS_PER_PASS * R
    rounds = -(-groups // P_SHIRE)
    slots = P_SHIRE * rounds
    busiest = -(-rounds // N_SHIRES)
    return {"R": R, "groups": groups, "shire_rounds": rounds, "group_slots": slots, "padding_groups": slots - groups,
            "busiest_shire_rounds": busiest, "shires_at_busiest": rounds - (busiest - 1) * N_SHIRES,
            "ops": slots * OPS_PER_GROUP, "chunk_copy_tiles": rounds * WEIGHT_TILES,
            "input_bytes": slots * INPUT_BYTES_PER_GROUP, "fswg_bytes": slots * FSWG_BYTES_PER_GROUP,
            "label_bytes": slots * LABEL_LINE, "resident_copy_bytes": WEIGHT_TILES * TILE if stage == "scp" else 0}


def check_launch(cs):
    """launch() against counts_scale.py's committed accounting for the planned launches (R 1, 16, 96)."""
    ls = cs["launch_scaling"]
    out = {}
    for key, R in (("train_R1", 1), ("train_R16", 16), ("train_R96", 96)):
        a, b = launch(R), ls[key]
        eq = (a["shire_rounds"] == b["shire_rounds"] and a["group_slots"] == b["group_slots"]
              and a["padding_groups"] == b["padding_groups"] and a["busiest_shire_rounds"] == b["busiest_shire_rounds"]
              and a["ops"] == b["fma_int8_ops_issued"] and a["chunk_copy_tiles"] == b["chunk_copy_tiles"]
              and a["input_bytes"] == b["l2scp_input_bytes_dram"] and a["fswg_bytes"] == b["fswg_bytes_scratchpad_own"]
              and a["resident_copy_bytes"] == b["scp_resident_copy_bytes"])
        out[key] = "EQUAL" if eq else "DIFFERS"
    if any(v != "EQUAL" for v in out.values()):
        sys.exit("refused: launch() differs from counts_scale.py's accounting: %s" % out)
    return out


# ---------------------------------------------------------------- the counted instructions: loop and the rest
def loop_split(cs, CK):
    """The tile loop's instructions per group, from the committed disassembly classified by the counter's own parser,
    and the rest of the group's counted instructions (counts-summary.json per_group_p32, minion 0, the most work)."""
    ins = [i for i in CK.parse_dis(os.path.join(REPO, DATA, "build", "mnistmlp.dis")) if LOOP_FIRST <= i.addr <= LOOP_LAST]
    if len(ins) != 28 or ins[-1].mn != "bne" or ins[3].mn != "bgeu":
        sys.exit("refused: the tile loop in mnistmlp.dis is not the registered 28 instructions")
    full, last = {}, {}
    for i in ins:
        c = i.cls
        if c == "branch":
            full["branch_taken" if i.mn == "bne" else "branch_not_taken"] = full.get(
                "branch_taken" if i.mn == "bne" else "branch_not_taken", 0) + 1
            last["branch_not_taken" if i.mn == "bne" else "branch_taken"] = last.get(
                "branch_not_taken" if i.mn == "bne" else "branch_taken", 0) + 1
            continue
        full[c] = full.get(c, 0) + 1
        if not (LOOP_SKIP[0] <= i.addr <= LOOP_SKIP[1]):
            last[c] = last.get(c, 0) + 1
    per_group = {c: full.get(c, 0) * (OPS_PER_GROUP - CHUNKS) + last.get(c, 0) * CHUNKS for c in set(full) | set(last)}
    g = cs["per_group_p32"]["0"]
    cls = {k.split(".", 1)[1]: v for k, v in g.items() if k.startswith("class.")}
    rest = {c: cls.get(c, 0) - per_group.get(c, 0) for c in cls}
    if any(v < 0 for v in rest.values()) or sum(cls.values()) != g["instructions"]:
        sys.exit("refused: the loop's counts exceed the counted group's")
    return {"loop_per_op": full, "loop_last_op": last, "loop_per_group": per_group, "counted_per_group": cls,
            "rest_per_group": rest, "instructions_per_group": g["instructions"],
            "loop_instructions_per_group": sum(per_group.values()), "rest_instructions_per_group": sum(rest.values()),
            "how": "loop: 28 instructions an op (21 scalar integer, 5 tensor-unit CSR writes, 1 taken and 1 not-taken "
                   "branch), 20 on a chunk's last op (15 scalar, 3 CSR, the two branch outcomes swapped); rest = the "
                   "counted group (counts-summary.json per_group_p32 minion 0) less the loop"}


def stack_bytes(cs):
    """Loads from and stores to DRAM addresses a group (stack, tables, the label line), level unknown (the simulator
    has no cache model): the label line's 64 B are priced as a DRAM store, the rest bracketed L1..L2 (section 4.3)."""
    g = cs["per_group_p32"]["0"]
    return g["memory.load.dram.read_bytes"] + g["memory.store.dram.write_bytes"] - LABEL_LINE


# ---------------------------------------------------------------- THE KINDS RULE (section 4.2)
def kinds_rule(T, FZ):
    H, bands, var = FZ.m10_heldout()
    K = T["kinds_a3"]
    rows = json.load(open(os.path.join(REPO, "docs/reports/data/2026-11-04-q142m-m10/rows-m10.json")))
    meas = {}
    for r in rows:
        if r["type"] == "int8" and r["card"] == "a3":
            meas.setdefault(r["kind"], []).append(r["D"])
    bfull = K["int8.full"]["b"]
    kinds = sorted(k for k in K if (k, "a3") in H)
    if len(kinds) != len(K):
        sys.exit("refused: a committed kind without M10 rows on aifoundry3")
    hp = {k: statistics.fmean(x["pred"] for x in H[(k, "a3")]) for k in kinds}

    def nearest(g, b, exclude=None):
        d = sorted((math.hypot(g - K[k]["g"], (b - K[k]["b"]) / bfull), k) for k in kinds if k != exclude)
        return d[:3]
    loo = []
    for j in kinds:
        nb = nearest(K[j]["g"], K[j]["b"], exclude=j)
        loo.append(statistics.fmean(hp[k] for _, k in nb) - statistics.fmean(meas[j]))
    rms_loo = math.sqrt(statistics.fmean(e * e for e in loo))
    m10 = json.load(open(os.path.join(REPO, "docs/reports/data/2026-11-04-q142m-m10/m10.json")))
    band_k = m10["families"]["int8"]["band_k"]
    hb = bands["int8|a3"]["half_w"]
    h = max(hb, band_k * rms_loo)
    out = {"rule": "three nearest committed aifoundry3 int8 kinds by d = sqrt((g - g_k)^2 + ((b - b_k) / b_full)^2), "
                   "b_full = int8.full's committed tile's %d bus bits an op; D = the mean of their M10 held-out "
                   "predictions (freeze_ledger_v2.kind_entry, unchanged); band [their least - h, their largest + h], "
                   "h = max(M10's int8|a3 half-width %.4f W, M10's int8 band_k %.4f x the rule's leave-one-out rms "
                   "%.4f W over the %d committed kinds) = %.4f W, clipped at 0" % (bfull, hb, band_k, rms_loo,
                                                                                   len(kinds), h),
           "b_full": bfull, "rms_loo_w": rms_loo, "loo_bias_w": statistics.fmean(loo), "loo_max_abs_w": max(abs(e) for e in loo),
           "m10_heldout_rms_same_kinds_w": math.sqrt(statistics.fmean((hp[k] - statistics.fmean(meas[k])) ** 2 for k in kinds)),
           "half_width_w": h, "n_kinds": len(kinds), "layers": {}}
    for c in CONFIGS:
        out["layers"][c] = {}
        for l in range(5):
            L = T["configs"][c]["layers"][str(l + 1)]
            nb = nearest(L["g_mean"], L["b_mean"])
            names = [k for _, k in nb]
            e = FZ.kind_entry(H, bands, names, "a3", "int8", "E202 %s layer %d: the three nearest committed kinds" % (c, l + 1))
            means = [u["heldout_pred_w"] for u in e["m10_kinds"]]
            out["layers"][c][str(l + 1)] = {
                "g_mean": L["g_mean"], "b_mean": L["b_mean"], "nearest": [{"kind": k, "distance": d, "g": K[k]["g"], "b": K[k]["b"],
                                                                            "heldout_pred_w": hp[k]} for d, k in nb],
                "D_w": e["D_w"], "D_band_w": [max(0.0, min(means) - h), max(means) + h], "ops_per_group": OPS_LAYER[l]}
    return out


# ---------------------------------------------------------------- the mesh: the chunk copies' hops (scp staging)
def mean_hops(MM):
    tiles = [13] * 112 + [28] * 336 + [28]     # chunk q: layer 1's 112 blocks of 13 tiles, then 28-tile chunks
    num = den = 0
    for s in range(N_SHIRES):
        for q, n in enumerate(tiles):
            num += n * MM.hops(s, q % N_SHIRES)
            den += n
    return num / den


# ---------------------------------------------------------------- the seconds (section 5)
def seconds_model(LS, CM_FIT, cat, F):
    rest = LS["rest_per_group"]
    lone = H1_OVER_H2[1] / H1_OVER_H2[2]

    def rate(c):
        if c == "vector_int":
            return F["constants"]["issue_rate"]["value"]   # frozen-v2.json: the vector-integer class, both harts
        return cat.rate(TIME_ROWS[c], "random")
    slow_branch = ("branch_taken", "jump")
    epi = {}
    epi["point"] = sum(n / (rate(c) if c in slow_branch else min(1.0, rate(c) * lone)) for c, n in rest.items() if n)
    epi["fast"] = sum(n / (rate(c) * lone if c in slow_branch else 1.0) for c, n in rest.items() if n)
    epi["slow"] = sum(n / rate(c) for c, n in rest.items() if n)
    l2_wait = (LS["stack_bytes_per_group"] / 64.0) * (N_MIN * F_HZ / L2_LINES_PER_S)
    c_fast = N_MIN * F_HZ / LS["int8_rate_ops_per_s"]
    shire_bytes = P_SHIRE * OPS_PER_GROUP * 2048.0 + WEIGHT_TILES * TILE + P_SHIRE * INPUT_BYTES_PER_GROUP

    def c_in(end):
        if DRAM_GBS[end] is None:
            return 0.0
        return N_MIN * INPUT_BYTES_PER_GROUP / (DRAM_GBS[end] * 1e9) * F_HZ
    # the point: sparse parity's fitted streamed loop at E202's own shire demand U (cycle_model.py's definition:
    # the shire's L2 demand over 128 B a cycle while its minions run), solved with the round it sets
    c_op, U = CM_FIT["C_OP_str"], 1.0
    for _ in range(50):
        rnd = OPS_PER_GROUP * c_op + epi["point"] + CHUNKS * BARRIER["point"] + c_in("point")
        U = shire_bytes / (rnd * 128.0)
        c_new = CM_FIT["C_OP_str"] * (1.0 + CM_FIT["KAPPA_T"] * U)
        if abs(c_new - c_op) < 1e-12:
            break
        c_op = c_new
    cop = {"point": c_op, "fast": c_fast, "slow": C_OP_SLOW}
    rounds = {}
    for end in ("point", "fast", "slow"):
        rounds[end] = {"c_op": cop[end], "tile_loop": OPS_PER_GROUP * cop[end], "rest_instructions": epi[end],
                       "barriers": CHUNKS * BARRIER[end], "input_copy": c_in(end),
                       "l2_line_waits": l2_wait if end == "slow" else 0.0}
        rounds[end]["cycles"] = sum(v for k, v in rounds[end].items() if k != "c_op")
    pre = {"point": WEIGHT_TILES * TILE / 76e9 * F_HZ + 2 * BARRIER["point"],
           "fast": 0.0, "slow": WEIGHT_TILES * TILE / 70e9 * F_HZ + 2 * BARRIER["slow"]}
    return {"round": rounds, "pre_scp_cycles": pre, "U_point": U, "lone_hart_factor": lone,
            "how": {"c_op": "point: sparse parity's fitted streamed-A loop (workloads/sparseparity/tools/cycle_model.py "
                            "FITTED C_OP_str %.1f x (1 + KAPPA_T %.5f x U), the model E189 scored within 0.3%% on a "
                            "never-run instance), U = E202's shire demand over 128 B a cycle (2 KiB an op for 32 "
                            "minions, the chunk and input copies landing), solved with the round; fast: the int8 "
                            "tensor unit's own rate (E78, 1,024 x 600 MHz / %.6e ops/s); slow: E37's private int8 "
                            "tiles (511.94 cycles an op, both operands private) x 1.15" % (
                                CM_FIT["C_OP_str"], CM_FIT["KAPPA_T"], LS["int8_rate_ops_per_s"]),
                    "rest_instructions": "the counted instructions outside the tile loop, by class: point at each "
                                         "class's catalogue rate times the lone-hart factor %.4f (add: 0.581 alone, "
                                         "0.3727 with both harts; hart 1 returns at once), taken branches and jumps at "
                                         "their both-harts rate (E189 5.1's rule), at most 1 a cycle; fast: 1 a cycle, "
                                         "taken branches and jumps at their rate x the factor; slow: every class at "
                                         "its catalogue (both-harts) rate, plus every DRAM-address line of the stack "
                                         "and tables waited for at the L2's line rate (27.4 G lines/s over the chip)" % lone,
                    "barriers": "449 shire barriers a round: 233 cycles (the 32-minion FLB and credit barrier) plus "
                                "skew 300 [0, 600]",
                    "input_copy": "the round's 13 input tiles a minion from DRAM, all 1,024 minions at once, at 76 GB/s "
                                  "(slow 70; fast: hidden)",
                    "pre": "scp staging, once a launch: the resident copy (11,153,408 B from DRAM) and two barriers"}}


def t_kernel(SM, R, end, stage):
    L = launch(R, stage)
    return (L["busiest_shire_rounds"] * SM["round"][end]["cycles"] + (SM["pre_scp_cycles"][end] if stage == "scp" else 0.0)) / F_HZ


# ---------------------------------------------------------------- the load (section 4.3)
def build_F2(F, KR, cat):
    F2 = copy.deepcopy(F)
    for c in CONFIGS:
        for l in range(5):
            e = KR["layers"][c][str(l + 1)]
            F2["kinds"][f"int8.e202:{c}:L{l + 1}"] = {"a3": {"D_w": e["D_w"], "D_band_w": e["D_band_w"],
                                                             "how": "E202's kinds rule (section 4.2)"}}
    for cls, row in V2C_ROWS.items():
        mean, lo, hi = cat.row(row, "random")
        F2["instr_classes"][cls] = {"random_pj": {"a3": mean}, "band_pj": [lo, hi],
                                    "source": f"catalogue.json combined.{row}/random/h2 (aifoundry3 mean; band lo..hi)"}
    return F2


def make_load(F2, T, LS, KR, hops, cfg, stage, R, t_k, t_w, T0, busy, arm="primary"):
    L = launch(R, stage)
    st = T["configs"][cfg]["streams"]

    def sh(name):
        return st[name]["rho"], st[name]["tau"]
    tensor = [{"format": "int8", "kind": f"int8.e202:{cfg}:L{l + 1}", "ops": L["group_slots"] * OPS_LAYER[l]}
              for l in range(5)]
    counts = LS["counted_per_group"] if arm != "epi-only" else LS["rest_per_group"]
    instr = []
    for cls, n in sorted(counts.items()):
        if not n or cls in PRICED_ELSEWHERE:
            continue
        fc = "vec_int" if cls == "vector_int" else cls
        instr.append({"class": fc, "what": cls, "hart_cycles": n * L["group_slots"] / F2["constants"]["issue_rate"]["value"]})
    for cls, n in sorted(LS["per_launch_minion"].items()):
        if n and cls not in PRICED_ELSEWHERE and cls in V2C_ROWS:
            instr.append({"class": cls, "what": cls + " (per launch)", "hart_cycles": n * N_MIN / F2["constants"]["issue_rate"]["value"]})
    ra, ta = sh("A")
    rb, tb = sh("B")
    rw, tw = sh("weights_once")
    ri, ti = sh("input")
    rs, ts = sh("act_store")
    by = [{"path": "scp_load", "bytes": float(TILE * L["ops"]), "rho": ra, "tau": ta, "what": "A tiles, own scratchpad"},
          {"path": "scp_load", "bytes": float(TILE * L["ops"]), "rho": rb, "tau": tb, "what": "B tiles, staging buffer"},
          {"path": "scp_store", "bytes": float(TILE * L["chunk_copy_tiles"]), "rho": rw, "tau": tw, "what": "chunk copies landing"},
          {"path": "scp_store", "bytes": float(L["input_bytes"]), "rho": ri, "tau": ti, "what": "input tiles landing"},
          {"path": "scp_store", "bytes": float(L["fswg_bytes"]), "rho": rs, "tau": ts, "what": "activation stores (fswg.ps)"},
          {"path": "dram_load", "bytes": float(L["input_bytes"]), "rho": ri, "tau": ti, "what": "input tiles from DRAM"},
          {"path": "dram_store", "bytes": float(L["label_bytes"]), "rho": 0.5, "tau": 0.5, "what": "label lines"},
          {"path": "l2_stream", "bytes": float(LS["stack_bytes_per_group"] * L["group_slots"]), "rho": 0.5, "tau": 0.5,
           "what": "stack and tables (L1..L2)"}]
    mesh = []
    if stage == "scp":
        by += [{"path": "scp_load", "bytes": float(TILE * L["chunk_copy_tiles"]), "rho": rw, "tau": tw,
                "what": "chunk copies read at the keeping shire"},
               {"path": "dram_load", "bytes": float(L["resident_copy_bytes"]), "rho": rw, "tau": tw, "what": "resident copy from DRAM"},
               {"path": "scp_store", "bytes": float(L["resident_copy_bytes"]), "rho": rw, "tau": tw, "what": "resident copy landing"}]
        mesh = [{"bytes": float(TILE * L["chunk_copy_tiles"]), "hops": hops, "rho": rw, "tau": tw}]
    else:
        by += [{"path": "l3_load" if arm != "dram-top" else "dram_load", "bytes": float(TILE * L["chunk_copy_tiles"]),
                "rho": rw, "tau": tw, "what": "chunk copies from DRAM addresses (L3 point, DRAM top)"}]
    awake = max(0.0, N_MIN * F_HZ * t_k - busy(R, stage))
    if arm == "v2.1":
        loop = N_MIN * F_HZ / F2["zeros_anchor"]["int8"]["a3"]["rate_ops_per_s"]
        scp = 2048.0 / F2["probe_rates_b_per_minion_cycle"]["scp_load"]
        awake -= max(0.0, loop + scp - LS["c_op_point"]) * L["ops"]
    load = {"card": "aifoundry3", "f_mhz": 600.0, "die_start_c": T0, "seconds": t_w, "tensor": tensor, "instr": instr,
            "bytes": by, "mesh": mesh, "work_units": R, "work_unit": "pass"}
    return load, awake


def predict(LV, F2, load, awake):
    """ledger_v2.predict() as frozen; the awake hart-cycles may be negative only in the v2.1 arm (E189's rule)."""
    ld = dict(load)
    if awake > 0:
        ld["awake_hart_cycles"] = awake
    pr = LV.predict(ld, F2)
    if awake < 0:   # v2.1 only: the overlap taken out of the joules over idle (posthoc_ledger_v2.py's E59 rule), with
        #             the ledger's own heat on it (k_leak x k_rise x the change)
        e = LV.awake_term(F2, "aifoundry3", 600.0, -awake)
        kk = pr["heat"]["k_leak_w_per_c"] * F2["constants"]["k_rise_c_per_w"]["value"]
        pr["j_over_idle"] -= e["j"]
        pr["j_over_idle_band"] = [pr["j_over_idle_band"][0] - e["band"][1], pr["j_over_idle_band"][1] - e["band"][0]]
        pr["j_total"] -= e["j"] * (1.0 + kk)
        pr["j_total_band"] = [pr["j_total_band"][0] - e["band"][1] * (1.0 + kk),
                              pr["j_total_band"][1] - e["band"][0] * (1.0 + kk)]
    return pr


class Model:
    def __init__(self):
        check_pins_ok = os.path.exists(PIN_FILE)
        self.pins = check_pins(write=not check_pins_ok)
        self.LV = load_module("ledger_v2", "tools/ledger/ledger_v2.py")
        self.FZ = load_module("freeze_ledger_v2", "tools/ledger/freeze_ledger_v2.py")
        self.LE = load_module("ledger_estimate", "workloads/ledger/ledger_estimate.py")
        self.CK = load_module("count_kernel", "tools/counter/count_kernel.py")
        self.MM = load_module("meshmap", "workloads/nocroute/meshmap.py")
        self.CMF = load_module("cycle_model", "workloads/sparseparity/tools/cycle_model.py").FITTED
        self.F = self.LV.load_frozen(os.path.join(REPO, "docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json"))
        if self.CMF["C_OP_str"] != self.F["cycle_model"]["FITTED"]["C_OP_str"] or \
                self.CMF["KAPPA_T"] != self.F["cycle_model"]["FITTED"]["KAPPA_T"]:
            sys.exit("refused: cycle_model.py's FITTED differs from frozen-v2.json's copy")
        self.cat = self.LE.Catalogue(os.path.join(REPO, self.LE.CAT_REL))
        self.cs = json.load(open(os.path.join(REPO, DATA, "counts", "counts-summary.json")))
        self.T = json.load(open(os.path.join(HERE, "desk", "tiles-e202.json")))
        self.launch_check = check_launch(self.cs)
        self.LS = loop_split(self.cs, self.CK)
        self.LS["stack_bytes_per_group"] = stack_bytes(self.cs)
        self.LS["per_launch_minion"] = {k.split(".", 1)[1]: v for k, v in self.cs["per_launch_part_p2_minion0"].items()
                                        if k.startswith("class.")}
        self.LS["int8_rate_ops_per_s"] = self.F["zeros_anchor"]["int8"]["a3"]["rate_ops_per_s"]
        self.KR = kinds_rule(self.T, self.FZ)
        self.hops = mean_hops(self.MM)
        self.SM = seconds_model(self.LS, self.CMF, self.cat, self.F)
        self.LS["c_op_point"] = self.SM["round"]["point"]["c_op"]
        self.F2 = build_F2(self.F, self.KR, self.cat)
        rp = self.SM["round"]["point"]
        self.busy_group = rp["tile_loop"] + rp["rest_instructions"]
        self.busy_pre = self.SM["pre_scp_cycles"]["point"] - 2 * BARRIER["point"]

    def busy(self, R, stage):
        L = launch(R, stage)
        return L["group_slots"] * self.busy_group + (N_MIN * self.busy_pre if stage == "scp" else 0.0)

    def given(self, cfg, stage, R, t_k, t_w, T0, arm="primary"):
        """The given-seconds forecast of one launch of R passes (E202.md 6.2): predict() at the measured t_k (awake),
        t_w (the card at rest) and T0. Returns per launch and per pass (point and band)."""
        a2 = "primary" if arm == "dram-top" else arm
        load, awake = make_load(self.F2, self.T, self.LS, self.KR, self.hops, cfg, stage, R, t_k, t_w, T0, self.busy, a2)
        pr = predict(self.LV, self.F2, load, awake)
        if stage == "dram" and arm in ("primary", "dram-top"):
            lt, aw = make_load(self.F2, self.T, self.LS, self.KR, self.hops, cfg, stage, R, t_k, t_w, T0, self.busy, "dram-top")
            top = predict(self.LV, self.F2, lt, aw)
            pr["j_over_idle_band"] = [pr["j_over_idle_band"][0], top["j_over_idle_band"][1]]
            pr["j_total_band"] = [pr["j_total_band"][0], top["j_total_band"][1]]
        out = {"j_over_idle": pr["j_over_idle"], "j_over_idle_band": pr["j_over_idle_band"], "j_total": pr["j_total"],
               "j_total_band": pr["j_total_band"], "heat_j": pr["heat"]["j"], "rest_w": pr["rest"]["w"],
               "w_over_idle": pr["w_over_idle"], "awake_hart_cycles": awake, "terms": pr["terms"], "heat": pr["heat"]}
        out["per_pass"] = {k: (v / R if not isinstance(v, list) else [x / R for x in v])
                           for k, v in out.items() if k in ("j_over_idle", "j_over_idle_band", "j_total", "j_total_band")}
        return out


def split_terms(terms, R):
    groups = {}
    for k, v in terms.items():
        if k.startswith("tensor:"):
            g = "tensor (M10 kinds rule)"
        elif k.startswith("instr:"):
            g = "instructions by class"
        elif k == "awake":
            g = "awake, not issuing"
        elif k.startswith("mesh"):
            g = "mesh (chunk copies' hops)"
        else:
            g = "bytes: " + k.split(":", 2)[2]
        x = groups.setdefault(g, {"j": 0.0, "band": [0.0, 0.0]})
        x["j"] += v["j"] / R
        x["band"][0] += v["band"][0] / R
        x["band"][1] += v["band"][1] / R
    return groups


def build():
    M = Model()
    R = R_REGISTERED
    out = {"_what": "E202's frozen forecasts (forecast_e202.py): one pass over the 60,000-image MNIST training split in int8, "
                    "aifoundry3 card 0 at 600 MHz, the ledger v2 as frozen with a load from E202's counted events; every "
                    "figure per pass unless named; frozen before any E202 datum",
           "label": "forecast, frozen before any datum; desk check of code; not blind to E189-E201's results (none is "
                    "of this program)", "interpreter": INTERPRETER,
           "inputs_sha256": M.pins, "R_registered": R, "R_allowed": list(R_ALLOWED), "T0_forecast_c": T0_FORECAST,
           "T0_band_c": list(T0_BAND), "launch_check": M.launch_check, "launch_R96": launch(R),
           "instructions": M.LS, "kinds_rule": M.KR, "mean_hops_chunk_copies": M.hops, "seconds_model": M.SM,
           "per_pass_units": {"images": IMAGES_PER_PASS, "macs_issued": MACS_ISSUED_PER_IMAGE * IMAGES_PER_PASS,
                              "macs_real": MACS_REAL_PER_IMAGE * IMAGES_PER_PASS, "groups": GROUPS_PER_PASS},
           "configs": {}}
    for cfg in CONFIGS:
        for stage in STAGES:
            key = f"{cfg}-{stage}"
            t = {e: t_kernel(M.SM, R, e, stage) for e in ("point", "fast", "slow")}
            p0 = M.given(cfg, stage, R, t["point"], t["point"], T0_FORECAST)
            f_lo = M.given(cfg, stage, R, t["fast"], t["fast"], T0_FORECAST)
            f_hi = M.given(cfg, stage, R, t["slow"], t["slow"], T0_FORECAST)
            T_lo = M.given(cfg, stage, R, t["fast"], t["fast"], T0_BAND[0])
            T_hi = M.given(cfg, stage, R, t["slow"], t["slow"], T0_BAND[1])
            pp = p0["per_pass"]
            rec = {"config": cfg, "stage": stage, "role": ("SCORED PAIR" if stage == "scp" else
                                                           "REGISTERED FALLBACK (scored only if the scp smoke fails)"),
                   "seconds": {"point": t["point"] / R, "band": [t["fast"] / R, t["slow"] / R],
                               "launch_R96": {"point": t["point"], "band": [t["fast"], t["slow"]]}},
                   "j_over_idle": pp["j_over_idle"], "j_over_idle_band_at_point": pp["j_over_idle_band"],
                   "j_over_idle_band": [min(f_lo["per_pass"]["j_over_idle_band"][0], pp["j_over_idle_band"][0]),
                                        max(f_hi["per_pass"]["j_over_idle_band"][1], pp["j_over_idle_band"][1])],
                   "j_total": pp["j_total"],
                   "j_total_band": [min(T_lo["per_pass"]["j_total_band"][0], pp["j_total_band"][0]),
                                    max(T_hi["per_pass"]["j_total_band"][1], pp["j_total_band"][1])],
                   "w_over_idle": p0["w_over_idle"], "rest_w": p0["rest_w"], "heat_w": p0["heat_j"] / t["point"],
                   "board_w_point": p0["rest_w"] + p0["w_over_idle"] + p0["heat_j"] / t["point"],
                   "awake_hart_cycles_per_pass": p0["awake_hart_cycles"] / R,
                   "split_per_pass": split_terms(p0["terms"], R)}
            rec["board_w_band_top"] = (M.LV.idle_w(M.F2, "aifoundry3", T0_BAND[1])[0] +
                                       f_lo["j_over_idle_band"][1] / t["fast"] + f_lo["heat"]["band"][1] / t["fast"])
            u = out["per_pass_units"]
            rec["per_image"] = {"j_over_idle": rec["j_over_idle"] / u["images"], "j_total": rec["j_total"] / u["images"],
                                "seconds": rec["seconds"]["point"] / u["images"]}
            rec["per_mac_issued_pj"] = {"j_over_idle": rec["j_over_idle"] / u["macs_issued"] * 1e12,
                                        "j_total": rec["j_total"] / u["macs_issued"] * 1e12}
            rec["per_mac_real_pj"] = {"j_over_idle": rec["j_over_idle"] / u["macs_real"] * 1e12,
                                      "j_total": rec["j_total"] / u["macs_real"] * 1e12}
            rec["arms"] = {}
            for arm in ("v2.1", "epi-only"):
                a = M.given(cfg, stage, R, t["point"], t["point"], T0_FORECAST, arm=arm)["per_pass"]
                rec["arms"][arm] = {"j_over_idle": a["j_over_idle"], "j_total": a["j_total"],
                                    "label": "REPORTED, never a verdict"}
            # self-check of code: given() at the point reproduces the frozen point
            g = M.given(cfg, stage, R, t["point"], t["point"], T0_FORECAST)["per_pass"]
            rec["selfcheck_given_at_point"] = max(abs(g["j_over_idle"] - pp["j_over_idle"]), abs(g["j_total"] - pp["j_total"]))
            out["configs"][key] = rec
    peaks = [out["configs"][k]["board_w_band_top"] for k in out["configs"]]
    out["peak"] = {"board_w_point_max": max(out["configs"][k]["board_w_point"] for k in out["configs"]),
                   "board_w_band_top_max": max(peaks), "stop_w": 65.0,
                   "under_the_stop": max(peaks) < 65.0}
    return M, r6(out)


def text(o):
    L = ["E202's frozen forecasts (forecast_e202.py); per pass of the 60,000-image training split; aifoundry3 card 0, "
         "600 MHz, die 55 C [52, 60]; " + o["interpreter"], ""]
    L.append("%-14s %-24s %-26s %-26s %8s %8s" % ("config", "seconds [band]", "J over idle [band]", "J with rest [band]",
                                                   "W over", "board W"))
    for k, r in o["configs"].items():
        L.append("%-14s %.5f [%.5f, %.5f] %.4f [%.4f, %.4f] %.4f [%.4f, %.4f] %8.3f %8.3f" % (
            k, r["seconds"]["point"], *r["seconds"]["band"], r["j_over_idle"], *r["j_over_idle_band"], r["j_total"],
            *r["j_total_band"], r["w_over_idle"], r["board_w_point"]))
    L += ["", "per image (uJ) and per multiply-add issued (pJ), over idle / with the card at rest:"]
    for k, r in o["configs"].items():
        L.append("  %-14s %.4f / %.4f uJ   %.4f / %.4f pJ   (real MACs: %.4f / %.4f pJ)" % (
            k, r["per_image"]["j_over_idle"] * 1e6, r["per_image"]["j_total"] * 1e6, r["per_mac_issued_pj"]["j_over_idle"],
            r["per_mac_issued_pj"]["j_total"], r["per_mac_real_pj"]["j_over_idle"], r["per_mac_real_pj"]["j_total"]))
    L += ["", "split of the J over idle a pass (point [band]):"]
    for k, r in o["configs"].items():
        L.append("  " + k)
        for t, v in sorted(r["split_per_pass"].items(), key=lambda kv: -kv[1]["j"]):
            L.append("    %-44s %.5f [%.5f, %.5f]" % (t, v["j"], *v["band"]))
    kr = o["kinds_rule"]
    L += ["", "THE KINDS RULE: " + kr["rule"],
          "  leave-one-out rms %.4f W, bias %+.4f W, max |err| %.4f W (M10's own held-out rms on the same kinds %.4f W)" % (
              kr["rms_loo_w"], kr["loo_bias_w"], kr["loo_max_abs_w"], kr["m10_heldout_rms_same_kinds_w"])]
    for c, ls in kr["layers"].items():
        for l, e in ls.items():
            L.append("  %-8s L%s g %.4f b %8.1f -> D %.4f [%.4f, %.4f] W from %s" % (
                c, l, e["g_mean"], e["b_mean"], e["D_w"], *e["D_band_w"], ", ".join(n["kind"] for n in e["nearest"])))
    sm = o["seconds_model"]
    L += ["", "THE SECONDS (cycles a shire-round; U at the point %.4f):" % sm["U_point"]]
    for e in ("point", "fast", "slow"):
        x = sm["round"][e]
        L.append("  %-5s c_op %.2f  loop %.0f  rest %.0f  barriers %.0f  input %.0f  L2 waits %.0f  = %.0f" % (
            e, x["c_op"], x["tile_loop"], x["rest_instructions"], x["barriers"], x["input_copy"], x["l2_line_waits"],
            x["cycles"]))
    L += ["", "peak board W: point %.2f, band top %.2f, stop 65 W: %s" % (
        o["peak"]["board_w_point_max"], o["peak"]["board_w_band_top_max"], "under" if o["peak"]["under_the_stop"] else "NOT UNDER")]
    return "\n".join(L) + "\n"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    M, out = build()
    js = json.dumps(out, indent=1, sort_keys=True) + "\n"
    tx = text(out)
    fj, ft = os.path.join(HERE, "forecast-e202.json"), os.path.join(HERE, "forecast-e202.txt")
    if a.check:
        ok = open(fj).read() == js and open(ft).read() == tx
        worst = max(r["selfcheck_given_at_point"] for r in out["configs"].values())
        print(json.dumps({"check": "PASS" if ok and worst <= 1e-12 and out["peak"]["under_the_stop"] else "FAIL",
                          "recomputed_equals_committed": ok, "given_at_point_worst": worst,
                          "peak_under_stop": out["peak"]["under_the_stop"], "launch_check": out["launch_check"]}))
        return 0 if ok else 1
    open(fj, "w").write(js)
    open(ft, "w").write(tx)
    print(tx)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
