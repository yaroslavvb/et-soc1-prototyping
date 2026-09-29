#!/usr/bin/env python3
"""NV helpers for nv/block.sh: no device access, files only.

    nvlib.py env  --card C --pass P --mode full|smoke|probe [--data ROOT]   shell assignments for the block (or exit 2
                                                                            + why); NV_SKIP says why a spare or a pass
                                                                            beyond the plan does not run
    nvlib.py plan --card C --pass P --mode M [--data ROOT] --json OUT       the pass's segments: TSV seg, mV, cfg, fill
                                                                            pattern, fill operands, burst args ("-" in
                                                                            probe mode)
    nvlib.py dms  ok|module|asic|fw|bl2|uptime|nocmhz|temps FILE            parse one dev_mngt_service output (prints the
                                                                            value; uptime in minutes)
    nvlib.py bl2ok VERSION                                                  exit 0 if VERSION >= nv.json min_bl2
    nvlib.py wincheck RAW --level MV [--kind K] [--die-ref MV] [--hi-ref C] check one sampler window; prints a JSON line,
                                                                            exit 0 ok, 1 not ok ("status" says why)
    nvlib.py nrule SD                                                       the validation's pass count N for a
                                                                            development SD of n_D (predictions.json)
    nvlib.py jline [--compact] k=v ...                                      one JSON object line (ints and floats unquoted)

Every number used here is in nv.json or predictions.json (next to this file).
"""
import json
import math
import os
import random
import re
import shlex
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONF = json.load(open(os.path.join(HERE, "nv.json")))
PRED = json.load(open(os.path.join(HERE, "predictions.json")))
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086}


def die(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def card_conf(card):
    if card in CONF["refused_cards"]:
        die(f"nv: card {card} is refused: {CONF['refused_cards'][card]}")
    c = CONF["cards"].get(card)
    if c is None:
        die(f"nv: no parameters for card {card} (nv.json cards: {', '.join(CONF['cards'])})")
    return c


def check_levels(levels):
    for mv in levels:
        if mv not in CONF["allowed_mv"] or not (485 <= mv <= 600):
            die(f"nv: level {mv} mV is not allowed (allowed: {CONF['allowed_mv']})")
    return levels


def version_tuple(v):
    try:
        t = tuple(int(x) for x in str(v).split("."))
        return t if len(t) == 3 else None
    except ValueError:
        return None


def nrule(sd):
    """The validation's pass count for a development SD of n_D, or None when more than the rule's max is needed."""
    r = PRED["val_passes_rule"]
    for n in range(r["min"], r["max"] + 1):
        if T975[n - 1] * sd / math.sqrt(n) <= r["target_half_width"]:
            return n
    return None


def val_needed():
    """N from prereg.json (fixed at the freeze); before the freeze, the rule's minimum (provisional)."""
    r = PRED["val_passes_rule"]
    try:
        n = json.load(open(os.path.join(HERE, "prereg.json"))).get("val_passes")
    except (OSError, ValueError):
        n = None
    if isinstance(n, int) and r["min"] <= n <= r["max"]:
        return n, False
    return r["min"], True


def status_of(data, p):
    b = os.path.join(data, "nv", f"p{p}", "block.json")
    try:
        return json.load(open(b)).get("status")
    except (OSError, ValueError):
        return None


def replaces_of(data, p):
    try:
        return json.load(open(os.path.join(data, "nv", f"p{p}", "order.json"))).get("replaces")
    except (OSError, ValueError):
        return None


def plan_pass(card, pas, mode, data=None):
    """The pass's order: {"levels", "order_index", "spare", "replaces", "skip"}. A validation spare (a pass after the
    N regular ones) takes the order of the earliest regular pass that did not end ok and that no spare has yet
    replaced with an ok pass, so that the six orders stay balanced whatever failed (DESIGN.md §4)."""
    c = card_conf(card)
    if mode == "probe":
        return {"levels": check_levels(list(CONF["probe_levels_mv"])), "order_index": None, "spare": False}
    if mode == "smoke":
        return {"levels": check_levels(list(CONF["smoke_levels_mv"])), "order_index": None, "spare": False}
    orders = CONF["orders"]
    k = pas - c["pass_min"]
    out = {"spare": False, "replaces": None, "skip": None}
    if c["role"] != "val":
        out["order_index"] = k % len(orders)
    else:
        need, _ = val_needed()
        spares = PRED["val_passes_rule"]["spares"]
        if k < need:
            out["order_index"] = k % len(orders)
        elif k >= need + spares:
            out["skip"] = f"pass {pas} is beyond the plan ({need} passes and {spares} spares from {c['pass_min']})"
            out["order_index"] = k % len(orders)
        else:
            out["spare"] = True
            ok = [q for q in range(c["pass_min"], pas) if data and status_of(data, q) == "ok"]
            if len(ok) >= need:
                out["skip"] = f"a spare, not needed ({len(ok)} validation passes ended ok)"
                out["order_index"] = k % len(orders)
            else:
                regular = range(c["pass_min"], c["pass_min"] + need)
                covered = {q for q in regular if data and status_of(data, q) == "ok"}
                for s in range(c["pass_min"] + need, pas):
                    if data and status_of(data, s) == "ok" and replaces_of(data, s) is not None:
                        covered.add(replaces_of(data, s))
                q = next(q for q in regular if q not in covered)
                out["replaces"] = q
                out["order_index"] = (q - c["pass_min"]) % len(orders)
    out["levels"] = check_levels(list(orders[out["order_index"]]))
    return out


def cmd_env(a):
    c = card_conf(a.card)
    p = a.pass_
    if not (c["pass_min"] <= p <= c["pass_max"]):
        die(f"nv: pass {p} is not a {c['role']} pass of {a.card} ({c['pass_min']}-{c['pass_max']}); "
            f"development passes are 1-99 on aifoundry3, validation passes 101-199 on aifoundry2")
    if c["role"] == "val" and a.mode == "smoke":
        die("nv: no smoke on the validation card (DESIGN.md §6): only --probe before the freeze, then passes 101+")
    if CONF["base_mv"] not in CONF["allowed_mv"] or CONF["base_mv"] != PRED["base_mv"]:
        die("nv: base_mv is not an allowed level, or differs from predictions.json")
    if CONF["levels_mv"] != PRED["levels_mv"]:
        die("nv: nv.json levels_mv differs from predictions.json")
    if version_tuple(CONF["min_bl2"]) is None or version_tuple(CONF["min_bl2"]) < (0, 19, 0):
        die("nv: nv.json min_bl2 must be 0.19.0 or later")
    check_levels(CONF["levels_mv"])
    pl = plan_pass(a.card, p, a.mode, a.data)
    exp = {"full": "nv", "smoke": "nv-smoke", "probe": "nv-probe"}[a.mode]
    t = CONF["timing_s"]
    lim = CONF["limits"]
    d = CONF["dms"]
    h = CONF["heater"]
    need, prov = val_needed() if c["role"] == "val" else (CONF["dev_passes"], False)
    out = {
        "NV_ROLE": c["role"], "NV_EXP": exp, "NV_DMS_IDX": c["dms_index"], "NV_FW_EXPECT": c["fw_release"],
        "NV_MIN_BL2": CONF["min_bl2"], "NV_RELEASE_FILE": c.get("release_file", ""),
        "NV_BASE_MV": CONF["base_mv"], "NV_ALLOWED": " ".join(map(str, CONF["allowed_mv"])),
        "NV_LEVELS": " ".join(map(str, pl["levels"])), "NV_SKIP": pl.get("skip") or "",
        "NV_SPARE": "1" if pl.get("spare") else "", "NV_REPLACES": pl.get("replaces") or "",
        "NV_NEEDED": need, "NV_NEEDED_PROVISIONAL": "1" if prov else "",
        "NV_DMS_PATH": d["path"], "NV_U_GET": d["u_get_ms"], "NV_U_SET": d["u_set_ms"], "NV_SET_ARG": d["set_arg"],
        "NV_VMIN_FILE": d["vmin_file"].replace("{idx}", str(c["dms_index"])),
        "NV_RESTORE_TRIES": CONF["restore_tries"], "NV_SAMPLER_ATTEMPTS": CONF["sampler_attempts"],
        "NV_START_MAX_C": lim["die_mean_start_max_c"], "NV_SENSOR_MAX_C": lim["any_sensor_abort_c"],
        "NV_ASIC_TOL": lim["asic_tol_frac"], "NV_DIE_TOL": lim["die_tol_mv"], "NV_NOC_MHZ": lim["noc_mhz"],
        "NV_IDLE_BACK_W": lim["idle_back_w"], "NV_CURRENT_STOP": lim["current_aborts_before_stop"],
        "NV_PASS_MIN": c["pass_min"],
        "NV_HEATER": "1" if c.get("heater") else "", "NV_HEAT_C": h["heat_c"], "NV_WARM_C": h["warm_c"],
        "NV_HEAT_MAX": h["max_launches"], "NV_HEATER_ARGS": h["args"],
    }
    for k, v in t.items():
        out["NV_T_" + k.upper()] = v
    for k, v in out.items():
        print(f"{k}={shlex.quote(str(v))}")


def load_wire_cfgs():
    path = os.path.join(HERE, "..", "..", "..", CONF["configs_from"])
    return {c["cfg"]: c for c in json.load(open(path))["configs"]}


def cmd_plan(a):
    c = card_conf(a.card)
    pl = plan_pass(a.card, a.pass_, a.mode, a.data)
    if pl.get("skip"):
        die(f"nv: {pl['skip']}")
    levels = pl["levels"]
    rows, segs = [], []
    if a.mode == "probe":
        for k, mv in enumerate(levels):
            rows.append([str(k), str(mv), "-", "-", "-", "-"])
            segs.append({"seg": k, "mv": mv, "cfgs": []})
    else:
        table = load_wire_cfgs()
        names = CONF["smoke_cfgs"] if a.mode == "smoke" else CONF["cfgs"]
        for n in names:
            if n not in table:
                die(f"nv: configuration {n} is not in {CONF['configs_from']}")
        for k, mv in enumerate(levels):
            order = list(names)
            if a.mode == "full":   # an independent shuffle per segment, reproducible from the pass and segment
                random.Random(CONF["seed0"] + 100 * a.pass_ + k).shuffle(order)
            for n in order:
                w = table[n]
                rows.append([str(k), str(mv), n, w["fill_pattern"], w["fill_operands"], " ".join(w["args"])])
            segs.append({"seg": k, "mv": mv, "cfgs": order})
    if a.json:
        json.dump({"card": a.card, "pass": a.pass_, "mode": a.mode, "role": c["role"], "base_mv": CONF["base_mv"],
                   "levels_mv": levels, "order_index": pl.get("order_index"), "spare": pl.get("spare"),
                   "replaces": pl.get("replaces"), "seed0": CONF["seed0"], "segments": segs}, open(a.json, "w"), indent=1)
    for r in rows:
        print("\t".join(r))


def cmd_dms(a):
    txt = open(a.file, errors="replace").read() if os.path.exists(a.file) else ""
    d = CONF["dms"]
    if a.kind == "ok":
        sys.exit(0 if re.search(d["ok_re"], txt) else 1)
    if a.kind in ("module", "asic", "nocmhz"):
        m = re.findall(d[{"module": "module_re", "asic": "asic_re", "nocmhz": "noc_mhz_re"}[a.kind]], txt)
        if m:
            print(m[-1])
        return
    if a.kind in ("fw", "bl2"):
        m = re.findall(d["fw_re" if a.kind == "fw" else "bl2_re"], txt)
        if m:
            print(".".join(m[-1]))
        return
    if a.kind == "uptime":
        m = re.findall(d["uptime_re"], txt)
        if m:
            dd, hh, mm = (int(x) for x in m[-1])
            print(dd * 1440 + hh * 60 + mm)
        return
    if a.kind == "temps":
        # "<minshire mean> <hottest current reading> <highest watermark>" from GET_MODULE_CURRENT_TEMPERATURE. The
        # "High" and "Low" values are the PVT's latched HILO watermarks (constant for hours: E42 on aifoundry2 read a
        # minion-shire high of 93-106 C all through each pass), not current readings: the current ones are the
        # minion-shire mean, the IO shire's current reading and the PMIC's
        vals = {k: int(v) for k, v in re.findall(r"([A-Z]+ [A-Za-z]+) Temperature Output: *(-?[0-9]+) *c", txt)}
        cur = vals.get("MINSHIRE Current")
        now = [vals[k] for k in ("MINSHIRE Current", "IOSHIRE Current", "PMIC SYS") if k in vals]
        wm = [vals[k] for k in ("MINSHIRE High", "IOSHIRE High") if k in vals]
        if cur is not None and now:
            print(cur, max(now), max(wm) if wm else max(now))
        return


def cmd_bl2ok(a):
    v, m = version_tuple(a.version), version_tuple(CONF["min_bl2"])
    sys.exit(0 if v is not None and m is not None and v >= m and v >= (0, 19, 0) else 1)


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def cmd_wincheck(a):
    lim = CONF["limits"]
    rows = []
    for line in open(a.raw, errors="replace") if os.path.exists(a.raw) else []:
        if line.startswith("{"):
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
    lv = a.level
    # the on-die monitor's expected reading: the level scaled by the block's own reading at the base (its offset)
    ref = a.die_ref if a.die_ref else CONF["base_mv"]
    die_expect = lv * ref / CONF["base_mv"]
    reg = [r.get("reg_mv", {}).get("noc") for r in rows]
    die_mv = [r["die_mv"]["noc"] for r in rows if "die_mv" in r]
    mhz = [r.get("mhz", {}).get("noc") for r in rows]
    mmhz = [r.get("mhz", {}).get("minion") for r in rows]
    tmean = [r["temp_c"]["minshire"][0] for r in rows if "temp_c" in r]
    tany, wmark = [], []
    for r in rows:   # current readings; [2] of each pair is the PVT's latched high watermark (see cmd_dms temps)
        tc = r.get("temp_c")
        if tc:
            tany += [tc["minshire"][0], tc["ioshire"][0], tc.get("pmic", 0)]
            wmark += [tc["minshire"][2], tc["ioshire"][2]]
    amps = []
    for r in rows:
        w = num(r.get("sp", {}).get("noc_w", [None])[0])
        v = r.get("die_mv", {}).get("noc")
        if w is not None and v:
            amps.append(w / (v / 1000.0))
    t0 = rows[0]["t_ms"] if rows else 0
    tail = [r["sp"]["noc_w"][0] for r in rows
            if "sp" in r and r["t_ms"] >= t0 + CONF["analysis"]["idle_skip_s"] * 1000]
    s = {"n": len(rows), "level_mv": lv, "die_ref_mv": ref, "die_expect_mv": round(die_expect, 1),
         "reg_noc": sorted({x for x in reg if x is not None}), "reg_missing": sum(x is None for x in reg),
         "die_noc_med": statistics.median(die_mv) if die_mv else None,
         "noc_mhz": sorted({x for x in mhz if x is not None}),
         "minion_mhz": sorted({x for x in mmhz if x is not None}),
         "die_mean_max_c": max(tmean) if tmean else None, "die_mean_last_c": tmean[-1] if tmean else None,
         "sensor_max_c": max(tany) if tany else None,
         "watermark_max_c": max(wmark) if wmark else None, "watermark_ref_c": a.hi_ref,
         # the third-highest sample: a real overcurrent persists, a one-sample telemetry glitch (E42 saw 7 W spikes) does not
         "noc_a_max": round(sorted(amps)[-3], 2) if len(amps) >= 3 else None,
         "noc_w_idle_mean": round(statistics.mean(tail), 4) if tail else None,
         "t_first_ms": t0, "t_last_ms": rows[-1]["t_ms"] if rows else 0}
    st = "ok"
    if len(rows) < lim["min_window_lines"]:
        st = "short"
    elif s["sensor_max_c"] is not None and s["sensor_max_c"] >= lim["any_sensor_abort_c"]:
        st = "hot_sensor"
    elif (s["watermark_max_c"] is not None and a.hi_ref is not None and s["watermark_max_c"] > a.hi_ref
          and s["watermark_max_c"] >= lim["any_sensor_abort_c"]):
        st = "hot_sensor"     # a watermark rose to the limit during this block: some sensor reached it
    elif s["die_mean_max_c"] is not None and s["die_mean_max_c"] >= lim["die_mean_abort_c"]:
        st = "hot"
    elif s["reg_missing"] or any(abs(x - lv) > lim["reg_tol_mv"] for x in s["reg_noc"]):
        st = "volt_reg"
    elif s["die_noc_med"] is None or abs(s["die_noc_med"] - die_expect) > lim["die_tol_mv"]:
        st = "volt_die"
    elif s["noc_mhz"] != [lim["noc_mhz"]]:
        st = "clock_noc"
    elif s["noc_a_max"] is not None and s["noc_a_max"] > lim["noc_max_a"]:
        st = "current"
    s["status"] = st
    s["kind"] = a.kind
    print(json.dumps(s))
    sys.exit(0 if st == "ok" else 1)


def cmd_nrule(a):
    n = nrule(a.sd)
    if n is None:
        die(f"nv: a development SD of {a.sd} needs more than {PRED['val_passes_rule']['max']} validation passes: "
            "revisit the design before any validation pass", 1)
    print(n)


def cmd_jline(a):
    o = {}
    compact = a.compact
    for kv in a.kv:
        k, _, v = kv.partition("=")
        if re.fullmatch(r"-?[0-9]+", v):
            o[k] = int(v)
        elif re.fullmatch(r"-?[0-9]*\.[0-9]+", v):
            o[k] = float(v)
        elif v in ("true", "false", "null"):
            o[k] = json.loads(v)
        elif v.startswith("{") or v.startswith("["):
            try:
                o[k] = json.loads(v)
            except ValueError:
                o[k] = v
        else:
            o[k] = v
    print(json.dumps(o, separators=(",", ":")) if compact else json.dumps(o))


def main():
    import argparse
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    for name in ("env", "plan"):
        p = sp.add_parser(name)
        p.add_argument("--card", required=True)
        p.add_argument("--pass", dest="pass_", type=int, required=True)
        p.add_argument("--mode", choices=["full", "smoke", "probe"], default="full")
        p.add_argument("--data", help="the card's data root (build/claims-v3/<card>): spares read the earlier passes")
        if name == "plan":
            p.add_argument("--json")
    p = sp.add_parser("dms")
    p.add_argument("kind", choices=["ok", "module", "asic", "fw", "bl2", "uptime", "nocmhz", "temps"])
    p.add_argument("file")
    p = sp.add_parser("bl2ok")
    p.add_argument("version")
    p = sp.add_parser("wincheck")
    p.add_argument("raw")
    p.add_argument("--level", type=int, required=True)
    p.add_argument("--kind", default="burst")
    p.add_argument("--die-ref", type=float, default=None)
    p.add_argument("--hi-ref", type=float, default=None, help="the highest temperature watermark at the block's start")
    p = sp.add_parser("nrule")
    p.add_argument("sd", type=float)
    p = sp.add_parser("jline")
    p.add_argument("--compact", action="store_true")
    p.add_argument("kv", nargs="*")
    a = ap.parse_args()
    {"env": cmd_env, "plan": cmd_plan, "dms": cmd_dms, "bl2ok": cmd_bl2ok, "wincheck": cmd_wincheck,
     "nrule": cmd_nrule, "jline": cmd_jline}[a.cmd](a)


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    main()
