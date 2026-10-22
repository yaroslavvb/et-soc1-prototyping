#!/usr/bin/env python3
"""test_hm.py - does the E62 analysis chain recover a known answer, and stay quiet on real noise?

    uv run -q --with numpy python3 test_hm.py --work <scratch dir> [--fps 5] [--seed 1]
            [--idle-red <RED of a real idle capture>]
            [--idle-cam <capture> --idle-t0 <epoch s> --idle-t1 <epoch s>]

Two halves, and both are needed.

**Recovery.**  `synth_hm.py` writes a whole synthetic RUNDIR from a planted model - a blob per
active shire at an affine die->image map with a chosen roll and mirror, a first-order arrival lag,
drift, shutter steps, low-emissivity component tops, frame noise, the live preset's quantisation -
and also a *clean* RED of the same session with none of those artefacts.  `reduce_hm.py` and
`analyze_hm.py` then run on the dirty capture, and on the clean cube, and the two are compared.
That is what makes the amplitude test meaningful: both sides go through the same estimator, so the
comparison is about the artefacts, not about the smoothing kernel or the lag.

**Silence.**  A real five-minute capture with the card idle, cut up by a *fake* two-arm schedule.
There is nothing to find, so the amplitude must be small and the permutation p must not be
significant.  A reduction that invented a dipole out of drift, shutter steps or fixed pattern would
fail here and pass everything else.

Exit code 0 when every test passes, 1 otherwise; the same table goes to <work>/test_results.json.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from reduce_hm import bin_plane  # noqa: E402
import synth_hm  # noqa: E402

PY = sys.executable
RESULTS = []


def record(name, passed, evidence):
    RESULTS.append(dict(name=name, passed=bool(passed), evidence=evidence))
    print("  %-4s %-42s %s" % ("PASS" if passed else "FAIL", name, evidence), flush=True)
    return bool(passed)


REUSE = False


def have(path):
    return REUSE and os.path.exists(path)


def run(args, **kw):
    t = time.time()
    r = subprocess.run([PY] + args, cwd=HERE, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print(r.stdout[-4000:])
        print(r.stderr[-4000:], file=sys.stderr)
        raise SystemExit("step failed: %s" % " ".join(args[:2]))
    return r.stdout.strip(), time.time() - t


def adeg(x, y):
    """The absolute difference of two angles in degrees, on (-180, 180]."""
    if x is None or y is None:
        return None
    return abs((float(x) - float(y) + 180.0) % 360.0 - 180.0)


# ---------------------------------------------------------------- half 1: recovery

def recovery(a):
    work = a.work
    proto = os.path.join(work, "protocol.json")
    rundir = os.path.join(work, "run")
    red = os.path.join(work, "red")
    ana = os.path.join(work, "ana")
    ana_t = os.path.join(work, "ana_truth")
    if a.protocol:
        shutil.copyfile(a.protocol, proto)
    else:
        with open(proto, "w") as f:
            json.dump(synth_hm.demo_protocol(), f, indent=1)
    if not have(os.path.join(rundir, "truth", "truth.json")):
        print("  synth:   %s" % run(["synth_hm.py", "--protocol", proto, "--out", rundir,
                                     "--fps", str(a.fps), "--seed", str(a.seed)]
                                    + list(a.synth_arg))[0])
    if not have(os.path.join(red, "frames.npz")):
        print("  reduce:  %s" % run(["reduce_hm.py", rundir, "--out", red])[0])
    print("  analyze: %s" % run(["analyze_hm.py", red, "--protocol", proto, "--out", ana,
                                 "--perms", str(a.perms), "--seed",
                                 str(a.seed)])[0].splitlines()[0])
    print("  analyze(clean truth): %s"
          % run(["analyze_hm.py", os.path.join(rundir, "truth", "red"), "--protocol", proto,
                 "--out", ana_t, "--perms", str(a.perms),
                 "--seed", str(a.seed)])[0].splitlines()[0])

    truth = json.load(open(os.path.join(rundir, "truth", "truth.json")))
    sm = json.load(open(os.path.join(ana, "summary.json")))
    smt = json.load(open(os.path.join(ana_t, "summary.json")))
    ffc = json.load(open(os.path.join(red, "ffc.json")))
    blocks = {b["block"]: b for b in sm["blocks"]}
    blocks_t = {b["block"]: b for b in smt["blocks"]}
    tblocks = {b["block"]: b for b in truth["blocks"]}
    ok = True

    # --- every protocol block found its own phases.  The runner labels a phase with the block's
    #     `name` key or else `block<i>`, reading neither `block` nor `id`, so this is the join that
    #     has to hold before any number means anything: unresolved, every block comes out "no
    #     phases for this block".
    bl = sm.get("block_labels") or {}
    res = bl.get("resolved") or {}
    ok &= record("block_labels_resolved", res and not bl.get("unmatched_blocks"),
                 "%d blocks, %d session labels, all matched by %s; unmatched %s, labels nothing "
                 "claimed %s" % (len(res), len(bl.get("session_labels") or []),
                                 ",".join(sorted({str(v.get("how")) for v in res.values()})),
                                 bl.get("unmatched_blocks"), bl.get("labels_nothing_claimed")))

    # --- the shutter steps: every planted one found, and no extra
    planted = truth["ffc"]["n"]
    found = len(ffc)
    ok &= record("ffc_count", found == planted,
                 "planted %d, detected %d (cues: %s); median |step| %.0f mK, all bridged by a "
                 "per-pixel offset" % (planted, found,
                                       ",".join(sorted({e["method"] for e in ffc}))[:60],
                                       float(np.median([abs(e["step_mk_median"]) for e in ffc]))
                                       if ffc else 0.0))
    if ffc and found == planted:
        err = np.array([abs(e["step_mk_median"] - t["step_mk_median"])
                        for e, t in zip(ffc, truth["ffc"]["events"])])
        sz = np.array([abs(t["step_mk_median"]) for t in truth["ffc"]["events"]])
        nb = int(np.median([e["frames_before"] for e in ffc]))
        na = int(np.median([e["frames_after"] for e in ffc]))
        # The windows either side are half a second each, so at the test's 5 fps they hold a
        # handful of frames and the real camera's 25 fps holds twelve.  The bound is therefore on
        # the median and the 90th percentile, with the max reported: a sign error or a factor of
        # two would blow through all three, while a frame-starved window only widens the tail.
        ok &= record("ffc_step_recovered",
                     float(np.median(err)) < 15.0 and float(np.percentile(err, 90)) < 30.0,
                     "per-event |recovered - planted| median %.1f mK, p90 %.1f, max %.1f over %d "
                     "events whose steps run to %.0f mK (%.0f%% of their own size); windows held "
                     "%d frames before and %d after at %g fps"
                     % (float(np.median(err)), float(np.percentile(err, 90)), err.max(), len(err),
                        sz.max(), 100 * float(np.median(err / np.maximum(sz, 1e-9))), nb, na,
                        truth["fps"]))

    # --- the dipole directions.  A two-arm swap keeps its direction under the arrival lag, so it
    #     is checked against the planted geometry itself; a four-phase sequence does not (each
    #     phase is mixed with the one before it), so it is checked against the clean cube.
    for name, tb in tblocks.items():
        want = tb.get("contrast_dipole_deg")
        st = blocks.get(name) or {}
        if want is None or st.get("dipole_deg") is None or st.get("kind") == "null":
            continue
        if (st.get("n_arms") or 0) == 2:
            d = adeg(st["dipole_deg"], want)
            ok &= record("dipole_dir_%s" % name, d <= a.tol_deg,
                         "measured %.2f deg vs planted %.2f (%.2f off, tol %.0f); die offset "
                         "(col %+.1f, row %+.1f) shires"
                         % (st["dipole_deg"], want, d, a.tol_deg,
                            tb["contrast_die_offset"][0], tb["contrast_die_offset"][1]))
        else:
            wt = (blocks_t.get(name) or {}).get("dipole_deg")
            d = adeg(st["dipole_deg"], wt)
            ok &= record("dipole_dir_%s" % name, d is not None and d <= a.tol_deg,
                         "measured %.2f deg vs the clean cube's %.2f (%.2f off); the planted "
                         "geometry says %.2f, which a %d-arm cycle at a dwell near the arrival "
                         "lag does not preserve"
                         % (st["dipole_deg"], wt, d, want, st.get("n_arms") or 0))

    # --- orientation: roll and mirror
    o = sm["orientation"]
    tm = truth["map"]
    droll = adeg(o.get("roll_deg"), tm["roll_deg"])
    ok &= record("orientation_roll", bool(o.get("fitted")) and droll is not None and droll <= 10.0,
                 "fitted %.2f +- %.2f deg vs planted %.1f (%.2f off, tol 10); %d arm-pair "
                 "displacements, die-direction spread %.0f deg"
                 % (o.get("roll_deg", float("nan")), o.get("roll_deg_sd", float("nan")),
                    tm["roll_deg"], droll if droll is not None else float("nan"),
                    o.get("n_pairs", 0), o.get("die_direction_spread_deg", float("nan"))))
    ok &= record("orientation_mirror",
                 bool(o.get("mirrored")) == bool(tm["mirror"]) and bool(o.get("mirror_identified")),
                 "mirrored %s vs planted %s, identified %s (two die axes needed, spread %.0f deg)"
                 % (o.get("mirrored"), tm["mirror"], o.get("mirror_identified"),
                    o.get("die_direction_spread_deg", float("nan"))))
    for key in ("col_unit_xy", "row_unit_xy"):
        got, want = o.get(key), tm[key]
        if got and want:
            dot = float(np.dot(got, want))
            ok &= record("orientation_%s" % key, dot > math.cos(math.radians(10.0)),
                         "%s vs planted %s (%.2f deg apart)"
                         % ([round(v, 3) for v in got], [round(v, 3) for v in want],
                            math.degrees(math.acos(max(-1.0, min(1.0, dot))))))

    # --- amplitudes, against the same estimator on the clean cube
    for name, st in blocks.items():
        if st.get("kind") in ("bloom", "null") or st.get("amp_mk") is None:
            continue
        wt = (blocks_t.get(name) or {}).get("amp_mk")
        if not wt:
            continue
        rel = abs(st["amp_mk"] / wt - 1.0)
        ok &= record("amplitude_%s" % name, rel <= 0.30,
                     "%.1f mK against the clean cube's %.1f mK (%.1f%%, tol 30%%); p %s, "
                     "per-cycle SE %s mK over %d cycles"
                     % (st["amp_mk"], wt, 100 * rel, st.get("p"), st.get("amp_se_mk"),
                        st.get("n_cycles") or 0))

    # --- the null block: identical arms, so nothing may be significant
    nulls = [s for s in sm["blocks"] if s.get("kind") == "null"]
    for st in nulls:
        ok &= record("null_block_%s" % st["block"], (st.get("p") or 0) > 0.05,
                     "amp %.1f mK (null SD %.1f mK), p %.3f within cycles / %.3f unrestricted, "
                     "floor %.3f, %d cycles"
                     % (st.get("amp_mk") or 0.0, (st.get("perm") or {}).get("null_sd_mk") or 0.0,
                        st.get("p") or 0.0, st.get("p_unrestricted") or 0.0,
                        st.get("p_floor") or 0.0, st.get("n_cycles") or 0))

    # --- the gain map really does find the planted shiny pixels
    if not (sm.get("gain") or {}).get("found"):
        record("gain_map_tracks_emissivity", True,
               "SKIPPED: no bloom block in this protocol, so the gain map is 1.0 everywhere (%s)"
               % (sm.get("gain") or {}).get("why"))
    else:
        ok &= gain_test(ana, rundir, truth)

    # --- the monopole: a constant-power swap must not move the whole frame
    for name, st in blocks.items():
        if st.get("kind") in ("bloom", "null") or st.get("amp_mk") is None:
            continue
        mono = abs(st.get("monopole_mk") or 0.0)
        ok &= record("monopole_small_%s" % name, mono < 0.25 * abs(st["amp_mk"]),
                     "frame mean %.2f mK against a %.1f mK dipole (%.1f%%)"
                     % (st.get("monopole_mk") or 0.0, st["amp_mk"], 100 * mono / st["amp_mk"]))

    # --- the cycle movie exists and is centred.  Per pixel, not just over the whole cube: a
    #     frame-wide mean of zero is what you get whatever the per-pixel offsets are, so the
    #     earlier version of this check would have passed a movie with a fixed pattern in it.
    for name, st in blocks.items():
        if not st.get("cycle"):
            continue
        z = np.load(os.path.join(ana, name, "cycle.npz"), allow_pickle=False)
        d = z["diff_mk"]
        px = float(np.nanmax(np.abs(np.nanmean(d, axis=0))))
        ok &= record("cycle_movie_%s" % name,
                     d.shape[1:] == tuple(sm["shape"]) and px < 1e-2
                     and d.shape[0] == len(z["t_s"])
                     and len(z["phase_edges_s"]) == len(z["phase_sets"]) + 1,
                     "%d frames of %dx%d over %.1f s, %d cycles, +-%.0f mK; worst pixel's own "
                     "cycle mean %.1e mK; %d phase edges for %d phase sets"
                     % (d.shape[0], d.shape[1], d.shape[2], st["cycle"]["cycle_s"],
                        st["cycle"]["n_cycles"], st["cycle"]["range_mk"], px,
                        len(z["phase_edges_s"]), len(z["phase_sets"])))

    # --- the detrend must not pay for the drift with the signal.  The clean truth cube carries no
    #     drift at all, so anything the detrend removes from it is signal: compare the amplitude
    #     the normal settings recover from it against the amplitude with no detrend at all.  A
    #     plain block-wide line fitted over C cycles eats 3/(4C^2) of a square wave - 8.3% at
    #     three cycles, 19% at two - which is exactly what this bounds.
    ana_nd = os.path.join(work, "ana_truth_nodetrend")
    run(["analyze_hm.py", os.path.join(rundir, "truth", "red"), "--protocol", proto,
         "--out", ana_nd, "--perms", "200", "--seed", str(a.seed), "--detrend-order", "0", "-q"])
    nd = {b["block"]: b for b in json.load(open(os.path.join(ana_nd, "summary.json")))["blocks"]}
    worst, detail = 0.0, []
    for name, st in blocks_t.items():
        # a null/control block has no signal to keep, so the ratio is meaningless there
        if st.get("kind") in ("bloom", "null", "control") or not st.get("amp_mk"):
            continue
        base = (nd.get(name) or {}).get("amp_mk")
        if not base:
            continue
        rel = st["amp_mk"] / base - 1.0
        detail.append("%s %+.1f%%" % (name, 100 * rel))
        worst = max(worst, abs(rel))
    ok &= record("detrend_keeps_the_signal", worst <= 0.10,
                 "on the clean cube (no drift to remove) the detrend changes the amplitude by %s "
                 "- worst %.1f%%, tol 10%%" % (", ".join(detail) or "nothing measurable",
                                               100 * worst))

    # --- and it must still remove a drift that is not a straight line
    pl = truth.get("physics") or {}
    if pl.get("drift_curve_mk"):
        worst, detail = 0.0, []
        for name, st in blocks.items():
            if st.get("kind") in ("bloom", "null") or not st.get("amp_mk"):
                continue
            dl = (st.get("drift_leak") or {})
            if dl.get("frac_of_amp") is None:
                continue
            detail.append("%s %.0f%% (%.1f mK of %.1f)"
                          % (name, 100 * dl["frac_of_amp"], dl.get("leak_proj_mk") or 0.0,
                             st.get("amp_proj_mk") or 0.0))
            worst = max(worst, dl["frac_of_amp"])
        ok &= record("drift_leak_bounded", worst <= 0.25,
                     "planted %.0f mK of non-linear drift (%.1f mK/s linear plus a %.0f mK "
                     "settling curve); what the residual could still account for: %s - worst "
                     "%.0f%%, tol 25%%" % (pl.get("drift_total_mk") or 0.0, pl.get("drift_mk_s"),
                                           pl["drift_curve_mk"],
                                           "; ".join(detail) or "nothing", 100 * worst))
    return ok


def gain_test(ana, rundir, truth):
    g = np.load(os.path.join(ana, "gain.npy"))
    gt = bin_plane(np.load(os.path.join(rundir, "truth", "gain.npy")), truth["binning"])
    trusted = np.load(os.path.join(ana, "bloom_dt.npy"))
    m = trusted > np.percentile(trusted, 50)
    c = float(np.corrcoef(g[m].ravel(), gt[m].ravel())[0, 1])
    sl = float(np.polyfit(gt[m].ravel(), g[m].ravel(), 1)[0])
    return record("gain_map_tracks_emissivity", c > 0.3,
                 "corr(recovered, planted) = %.3f over the %d%% of pixels the bloom lights; "
                 "regression slope %.2f (1.0 would be a perfect recovery of each pixel's "
                 "emissivity)" % (c, round(100 * m.mean()), sl))


# ---------------------------------------------------------------- half 2: silence on real noise

def fake_schedule(red_dir, out_dir, t0_s, dwell_s, cycles, arms, lead_s, proto_path):
    """Copy a RED and lay a *fake* two-arm schedule over it, as if the card had been swapping."""
    os.makedirs(out_dir, exist_ok=True)
    for nm in ("frames.npz", "scene.npy", "ffc.json", "meta.json"):
        src = os.path.join(red_dir, nm)
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(out_dir, nm))
    meta = json.load(open(os.path.join(out_dir, "meta.json")))
    epoch0 = float(meta.get("t_zero_epoch_s") or 0.0)
    t_ms = lambda s: round((epoch0 + s) * 1000)                            # noqa: E731
    phases, launches = [], []
    t = lead_s
    for c in range(cycles):
        for pi, arm in enumerate(arms):
            phases.append(dict(block="idlenull", cycle=c, phase=pi, set=arm, idle=False,
                               planned_start_ms=t_ms(t), planned_end_ms=t_ms(t + dwell_s),
                               t_first_start_ms=t_ms(t), t_last_end_ms=t_ms(t + dwell_s),
                               n_launches=1))
            launches.append(dict(block="idlenull", cycle=c, phase=pi, set=arm, mask=None,
                                 per_shire=32, harts=384, seconds=dwell_s, budget=0,
                                 t_start_ms=t_ms(t), t_end_ms=t_ms(t + dwell_s), wall_s=dwell_s,
                                 rc=0, stderr_tail=""))
            t += dwell_s
    with open(os.path.join(out_dir, "phases.jsonl"), "w") as f:
        for p in phases:
            f.write(json.dumps(p) + "\n")
    with open(os.path.join(out_dir, "launches.jsonl"), "w") as f:
        for l in launches:
            f.write(json.dumps(l) + "\n")
    with open(os.path.join(out_dir, "blocks.jsonl"), "w") as f:
        f.write(json.dumps(dict(block="idlenull", t_start_ms=t_ms(lead_s), t_end_ms=t_ms(t),
                                status="done")) + "\n")
    # the telemetry a dry run writes, in the wrapped {host_ms, line} shape, so that path is tested
    with open(os.path.join(out_dir, "tel.jsonl"), "w") as f:
        s = 0.0
        while s <= t + 2:
            line = dict(t_ms=t_ms(s), board_w=24.1, temp_c=dict(minshire=[51, 50, 52]),
                        mhz=dict(minion=600))
            f.write(json.dumps(dict(host_ms=t_ms(s), line=json.dumps(line))) + "\n")
            s += 1.0
    with open(os.path.join(out_dir, "session.json"), "w") as f:
        json.dump(dict(experiment="E62-null", dry=True, host="n/a", user="n/a",
                       t_start_ms=t_ms(0.0), t_end_ms=t_ms(t + 2), stop_reason="done"), f)
    full = synth_hm.demo_protocol()
    pr = dict(experiment="E62-null", version=1, sets=full["sets"],
              note="a fake schedule laid over a real idle capture: there is nothing to find",
              blocks=[dict(block="idlenull", kind="swap", title="fake swap on an idle card",
                           cycles=cycles, warmup_cycles=1, dwell_s=dwell_s, arms=list(arms),
                           contrast=list(arms), movie=False,
                           predicted=dict(amp_mk=[0, 0]), pass_rule="p > 0.05")])
    with open(proto_path, "w") as f:
        json.dump(pr, f, indent=1)
    return t


def spellings(a):
    """The registered protocol's own shapes, which the test protocol does not have.

    `design/protocol.json` names its blocks under `id`, writes its pass rules as English prose,
    and leaves `arms`, `contrast` and `order` out entirely.  Each of those took a different route
    through the chain and the first two used to break it outright - block_name() returned None and
    the run died on a None path, and a prose rule came out as the verdict string
    "error: unmatched ')'".  So a small session in exactly that dialect is run here.
    """
    work = os.path.join(a.work, "spell")
    os.makedirs(work, exist_ok=True)
    full = synth_hm.demo_protocol()
    pr = os.path.join(work, "proto.json")
    proto = dict(experiment="E62-spell", version=1, sets=full["sets"], die=full["die"],
                 per_shire_w=1.3, idle_board_w=24.0, blocks=[
                     dict(id="E62-NS", kind="swap", title="named by id, nothing else",
                          cycles=6, warmup_cycles=1,
                          pass_rule="PASS if the lobe moves: a dipole whose two extrema change "
                                    "sides with the mask (p < 0.01), monopole |card mean| < 25 mK",
                          predicted=dict(what="prose", mk=306.0),
                          phases=[dict(set="N12", dwell_s=12.0), dict(set="S12", dwell_s=12.0)]),
                     dict(id="E62-NULLAA", kind="control", title="same mask in both arms",
                          cycles=2, warmup_cycles=1,
                          pass_rule="PASS if the half-patch statistic is 0 +/- 25 mK",
                          predicted=dict(mk=0.0),
                          phases=[dict(set="NULLA", dwell_s=12.0),
                                  dict(set="NULLB", dwell_s=12.0)])])
    json.dump(proto, open(pr, "w"), indent=1)
    rundir, red, ana = os.path.join(work, "run"), os.path.join(work, "red"), os.path.join(work, "ana")
    if not have(os.path.join(rundir, "truth", "truth.json")):
        run(["synth_hm.py", "--protocol", pr, "--out", rundir, "--fps", "4",
             "--seed", str(a.seed)])
    if not have(os.path.join(red, "frames.npz")):
        run(["reduce_hm.py", rundir, "--out", red, "-q"])
    run(["analyze_hm.py", red, "--protocol", pr, "--out", ana, "--perms", "400",
         "--seed", str(a.seed), "-q"])
    sm = json.load(open(os.path.join(ana, "summary.json")))
    blocks = {b["block"]: b for b in sm["blocks"]}
    bl = sm.get("block_labels") or {}
    ok = record("spelling_id_block_names",
                set(blocks) == {"E62-NS", "E62-NULLAA"}
                and not (bl.get("unmatched_blocks") or []),
                "blocks named only by `id` came through as %s, joined to the runner's labels %s "
                "by %s" % (sorted(blocks), bl.get("session_labels"),
                           ",".join(sorted({str(v.get("how"))
                                            for v in (bl.get("resolved") or {}).values()}))))
    ns = blocks.get("E62-NS") or {}
    ok &= record("spelling_arms_and_contrast_derived",
                 ns.get("arms") == ["N12", "S12"] and ns.get("contrast") == ["N12", "S12"]
                 and (ns.get("amp_mk") or 0) > 30,
                 "with no `arms`, `contrast` or `dwell_s` in the block, arms %s, contrast %s, "
                 "dwell %s s realised, amp %.1f mK"
                 % (ns.get("arms"), ns.get("contrast"), ns.get("dwell_s_realised"),
                    ns.get("amp_mk") or float("nan")))
    verdicts = [(n, b.get("verdict"), b.get("verdict_note")) for n, b in blocks.items()]
    ok &= record("spelling_prose_pass_rule_is_not_a_verdict",
                 all(v is None and bool(note) for _, v, note in verdicts),
                 "a pass rule written in English gives verdict None with a note, not a parser "
                 "error as the result: %s" % "; ".join("%s -> %r" % (n, (note or "")[:46])
                                                       for n, _, note in verdicts))
    # the floor the registered cycle counts really live under
    ok &= record("p_floor_reported_and_honest",
                 all(b.get("p_floor") is not None
                     and abs(b["p_floor"] - 2.0 / 2 ** b["n_cycles"]) < 1e-9
                     and (b["p_floor"] <= 0.05) == (b.get("p_primary_scheme") == "within")
                     for b in blocks.values() if b.get("n_cycles")),
                 "the exhaustive sign-flip floor is 2/2^C, measured not assumed: %s; a block "
                 "whose floor is above 0.05 quotes the unrestricted p instead"
                 % ", ".join("%s C=%d floor %.4g (%s)"
                             % (n, b.get("n_cycles") or 0, b.get("p_floor") or 0,
                                b.get("p_primary_scheme"))
                             for n, b in blocks.items() if b.get("n_cycles")))
    return ok


def silence(a):
    red = a.idle_red
    if not red and a.idle_cam:
        red = os.path.join(a.work, "red_idle")
        cmd = ["reduce_hm.py", "--out", red, "--cam", a.idle_cam]
        if a.idle_t0:
            cmd += ["--t0", str(a.idle_t0)]
        if a.idle_t1:
            cmd += ["--t1", str(a.idle_t1)]
        out, dt = run(cmd)
        print("  reduce(idle): %s" % out)
    if not red:
        return record("idle_null_dipole", True,
                      "SKIPPED: pass --idle-red <RED> (or --idle-cam with --idle-t0/--idle-t1) "
                      "to run the real-capture null test")
    meta = json.load(open(os.path.join(red, "meta.json")))
    ffc = json.load(open(os.path.join(red, "ffc.json")))
    span = float(meta["last_frame_t_s"]) - float(meta["first_frame_t_s"])
    ok = True
    results = []
    # Four fake schedules, so one unlucky phase alignment cannot decide the test.  The last is the
    # registered protocol's own control shape - a 42.5 s dwell over three laps, two analysed, the
    # arm order never alternating - which is the case with no margin at all: the sign-flip null of
    # two cycles cannot return below 0.5, so the p-value is not the test there and the measured
    # amplitude has to be read against `drift_leak`.
    for i, (dwell, lead) in enumerate(((16.0, 20.0), (20.0, 10.0), (16.0, 28.0), (42.5, 6.0))):
        cycles = int((span - lead - 4.0) // (2 * dwell))
        if cycles < 3:
            continue
        d = os.path.join(a.work, "idle_fake%d" % i)
        pr = os.path.join(a.work, "idle_fake%d.json" % i)
        fake_schedule(red, d, 0.0, dwell, cycles, ("N12", "S12"), lead, pr)
        out, _ = run(["analyze_hm.py", d, "--protocol", pr, "--out", d + "_ana",
                      "--perms", str(a.perms), "--seed", str(a.seed)])
        st = json.load(open(os.path.join(d + "_ana", "idlenull", "stats.json")))
        results.append(dict(dwell_s=dwell, lead_s=lead, cycles=st.get("n_cycles"),
                            amp_mk=st.get("amp_mk"), excess_mk=st.get("amp_excess_mk"),
                            excess_sd=st.get("amp_excess_sd"), p=st.get("p"),
                            p_unrestricted=st.get("p_unrestricted"),
                            null_sd_mk=(st.get("perm") or {}).get("null_sd_mk"),
                            null_mean_mk=(st.get("perm") or {}).get("null_mean_mk"),
                            monopole_mk=st.get("monopole_mk"), dipole_deg=st.get("dipole_deg"),
                            ffc_in_block=st.get("ffc_count"),
                            p_floor=st.get("p_floor"), p_scheme=st.get("p_primary_scheme"),
                            leak_mk=(st.get("drift_leak") or {}).get("leak_proj_mk"),
                            leak_frac=(st.get("drift_leak") or {}).get("frac_of_amp"),
                            drift_mk_s=(st.get("drift_leak") or {}).get("residual_drift_mk_s"),
                            arm_dt_s=(st.get("drift_leak") or {}).get("arm_dt_s")))
    bad = [r for r in results if (r["p"] or 1.0) <= 0.05]
    ok &= record("idle_null_dipole", results and not bad,
                 "%d fake two-arm schedules over a real %.0f s idle capture (%d shutter events, "
                 "%d frames): %s" % (len(results), span, len(ffc), meta["packets"],
                                     "; ".join("%gs dwell x%d: amp %.1f mK (null SD %.1f), p %.3f"
                                               % (r["dwell_s"], r["cycles"], r["amp_mk"],
                                                  r["null_sd_mk"] or 0.0, r["p"]) for r in results)))
    sds = [abs(r["excess_sd"] or 0.0) for r in results]
    if sds:
        ok &= record("idle_null_amplitude", max(sds) < 3.0,
                     "the statistic's own null level is where it lands: excess over it %s, i.e. "
                     "%s SD (tol 3).  The lobe contrast cannot go below that floor, which is "
                     "%.0f-%.0f mK here - the real detection floor of a 7-cycle swap on this "
                     "camera, against the registered 373 mK of a half-die swap"
                     % (", ".join("%+.1f mK" % (r["excess_mk"] or 0.0) for r in results),
                        ", ".join("%+.1f" % (r["excess_sd"] or 0.0) for r in results),
                        min(r["null_mean_mk"] or 0.0 for r in results),
                        max(r["null_mean_mk"] or 0.0 for r in results)))
    RESULTS[-1]["detail"] = results
    # Whatever apparent dipole an idle card leaves must be *accounted for*, not merely small: on
    # the registered controls' shape the sign-flip null cannot say anything (floor 0.5 at two
    # cycles), so the thing that has to hold is that the reported drift leak covers the amplitude.
    few = [r for r in results if (r["cycles"] or 0) <= 3]
    if few:
        ok &= record("idle_null_amplitude_explained",
                     all((r["leak_mk"] is not None
                          and abs(r["leak_mk"]) >= 0.5 * abs(r["amp_mk"]))
                         or abs(r["excess_sd"] or 0.0) < 3.0 for r in few),
                     "the few-cycle shapes - where the sign-flip null's floor is %s and the "
                     "p-value cannot be the test - report %s, i.e. a residual drift of %s mK/s "
                     "over an arm gap of %s s, which covers the apparent %s mK"
                     % (", ".join("%.3g" % (r["p_floor"] or 0) for r in few),
                        ", ".join("leak %.0f mK (%.0f%% of amp)"
                                  % (r["leak_mk"] or 0, 100 * (r["leak_frac"] or 0)) for r in few),
                        ", ".join("%.3g" % (r["drift_mk_s"] or 0) for r in few),
                        ", ".join("%.1f" % (r["arm_dt_s"] or 0) for r in few),
                        ", ".join("%.0f" % r["amp_mk"] for r in few)))
    return ok


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--work", default=os.path.join(os.path.expanduser("~"), ".hm-test"))
    p.add_argument("--fps", type=float, default=5.0)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--perms", type=int, default=2000)
    p.add_argument("--tol-deg", type=float, default=15.0)
    p.add_argument("--idle-red", help="a RED already reduced from a real idle capture")
    p.add_argument("--idle-cam", help="a real idle capture, to reduce here")
    p.add_argument("--idle-t0", type=float)
    p.add_argument("--idle-t1", type=float)
    p.add_argument("--idle-amp-mk", type=float, default=30.0)
    p.add_argument("--protocol", help="use this protocol instead of synth_hm's demo one")
    p.add_argument("--synth-arg", action="append", default=[],
                   help="extra argument passed through to synth_hm.py; repeatable")
    p.add_argument("--skip-synth", action="store_true")
    p.add_argument("--skip-idle", action="store_true")
    p.add_argument("--reuse", action="store_true",
                   help="keep an existing synthetic RUNDIR and RED in the work dir")
    a = p.parse_args(argv)
    global REUSE
    REUSE = bool(a.reuse)
    os.makedirs(a.work, exist_ok=True)
    t0 = time.time()
    print("E62 heat-movie analysis tests, work dir %s" % a.work)
    ok = True
    if not a.skip_synth:
        print(" synthetic recovery:")
        ok &= recovery(a)
        print(" the registered protocol's own spellings:")
        ok &= spellings(a)
    if not a.skip_idle:
        print(" silence on a real idle capture:")
        ok &= silence(a)
    npass = sum(1 for r in RESULTS if r["passed"])
    out = dict(tool="test_hm.py", when=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
               work=os.path.abspath(a.work), python=sys.version.split()[0],
               numpy=np.__version__, knobs=vars(a), passed=npass, total=len(RESULTS),
               all_passed=bool(ok), elapsed_s=round(time.time() - t0, 1), tests=RESULTS)
    with open(os.path.join(a.work, "test_results.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("%d/%d passed in %.0f s -> %s"
          % (npass, len(RESULTS), time.time() - t0,
             os.path.join(a.work, "test_results.json")))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
