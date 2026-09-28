#!/usr/bin/env python3
"""OH (the effect of overheating, E53): the block plans, the live watcher, the card checks, the pre-registration lock
and the V3_DRY simulator of tools/claims-v3/oh/block.sh. Standard library only. A pruned copy of ../hp/hplib.py
(hp/ is locked and untouched): kept are the watcher (with OH's caps: soft caps pause the heater, the 88 C line ends the
block and the session), the card-0 guard check, envcheck, binhash and the dry simulator; dropped are the SP log level,
the edge, TRIG-B, the plans and statistics of heat placement.

Subcommands (block.sh calls them; each prints plain text a shell can read):
  check-card --pass P --card C       refuse aifoundry1 card 0, aifoundry2, an unknown card or a pass kind (exit 2)
  plan --pass P --card C             SET lines (caps, bands, the OH-1 order) for the block
  watch --tel RAW --state F --ctl F --stop-file F --session-stop F [--guard RAW]   the live watcher of one run
  guardcheck --guard RAW --gate C --max-age S                                     card 0's guard: exit 0 if fresh and <= gate
  kcheck --file OUT --tool T         one kernel process's output: "OK n", "BAD why", "UNCHECKED why", "NORESULT"
  envcheck --card C                  exit 1 if V3_FORCE or an OH_* override is set without V3_DRY
  binhash role=path ...              {role: {path, sha256}}
  preregcheck --card C --bins F      the PREREG lock: PREREG.md = PREREG.sha256 = $OH_PREREG_SHA256; every locked file
                                     and this card's binaries unchanged (exit 1 with the reason otherwise)
  dry-sampler|dry-guard|dry-die|dry-heater|dry-kernel   the V3_DRY=1 simulator (numbers mean nothing about the cards)
  selftest                           the watcher's caps and the checks on synthetic input

Pass numbers: pass = T*100 + k (k = 1..99): T 1 OH-1 block, 2 OH-2 block, 9 smoke.
"""
import glob
import gzip
import hashlib
import json
import math
import os
import random
import re
import signal
import struct
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_root(d):
    x = d
    for _ in range(6):
        if os.path.exists(os.path.join(x, "tools", "claims-v3", "lib.sh")):
            return x
        x = os.path.dirname(x)
    return os.path.abspath(os.path.join(d, "..", "..", ".."))


ROOT = _find_root(HERE)
KINDS = {1: "OH1", 2: "OH2", 9: "SMOKE"}
CARDS = ("aifoundry3", "aifoundry1-c1")
FORBIDDEN = {
    "aifoundry1-c0": "aifoundry1 card 0 is never used (owner rule): only the read-only card-0 guard of a card-1 block reads it",
    "aifoundry2": "aifoundry2 is not an OH card (its Master Minion is hung since 28 Sep 02:50, and no page claim needs it)",
}


class Refused(ValueError):
    pass


def load_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def params():
    p = os.environ.get("OH_PARAMS")
    if p and not dry():
        raise Refused("OH_PARAMS is honoured only under V3_DRY=1")
    P = load_json(p or os.path.join(HERE, "params-oh.json"))
    if dry():   # V3_DRY's clock runs OH_DRY_SPEED times faster: the staleness limits keep their real-time length
        sp = float(os.environ.get("OH_DRY_SPEED", "40") or 40)
        for k in ("sampler_stale_s", "guard_stale_s"):
            P["caps"][k] = int(P["caps"][k] * sp)
    return P


def dry():
    return bool(os.environ.get("V3_DRY"))


def check_card(card):
    if card in FORBIDDEN:
        raise Refused("%s: %s" % (card, FORBIDDEN[card]))
    if card not in CARDS:
        raise Refused("unknown card %r (OH runs on %s)" % (card, ", ".join(CARDS)))


def decode_pass(p):
    p = int(p)
    T, k = p // 100, p % 100
    if T not in KINDS or not 1 <= k <= 99:
        raise ValueError("pass %d: expected T*100 + k with T in %s and k 1-99" % (p, sorted(KINDS)))
    return KINDS[T], k


def plan(pass_no, card):
    """(info, lines) for block.sh: the caps, the kind, the OH-1 condition order or the OH-2 bands."""
    check_card(card)
    pass_no = int(pass_no)
    kind, k = decode_pass(pass_no)
    P = params()
    info = {"kind": kind, "k": k}
    if kind == "OH1":
        nb = P["oh1"]["blocks"][card]
        if k > nb:
            raise Refused("%s runs %d OH-1 blocks (passes 101-%d); pass %d is not planned" % (card, nb, 100 + nb, pass_no))
        rows = P["oh1"]["williams_rows"]
        info["order"] = rows[(k - 1) % len(rows)]
        info["williams_row"] = (k - 1) % len(rows) + 1
    if kind == "OH2" and k != 1:
        raise Refused("one OH-2 block per card (pass 201)")
    return info, P


def sh(v):
    if isinstance(v, bool):
        return "1" if v else ""
    if isinstance(v, (list, dict)):
        v = json.dumps(v)
    if v is None:
        v = ""
    s = str(v)
    return "'" + s.replace("'", "'\\''") + "'"


# ----------------------------------------------------------------------------------------------- telemetry
def open_any(path):
    if path.endswith(".gz"):
        return gzip.open(path, "rt", errors="replace")
    return open(path, errors="replace")


def load_jsonl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    out = []
    if not os.path.exists(path):
        return out
    try:
        with open_any(path) as f:
            for line in f:
                line = line.strip()
                i = line.find("{")
                if i >= 0:
                    try:
                        out.append(json.loads(line[i:]))
                    except Exception:
                        pass
    except (OSError, EOFError):
        pass
    return out


def sample_fields(s):
    """(t_ms, mean, low, high, board_w, mhz, io_high, since_reset) of one sampler line (None where absent)."""
    tc = s.get("temp_c") or {}
    ms = tc.get("minshire") or [None, None, None]
    io = tc.get("ioshire") or [None, None, None]
    return (s.get("t_ms"), ms[0], ms[1], ms[2], s.get("board_w"), (s.get("mhz") or {}).get("minion"), io[2],
            s.get("since_reset_ms"))


def windows(samples, reset_ms=1000):
    """Reset windows of a --reset-ms sampler (as ../hp/hplib.py): a sample with since_reset_ms >= reset_ms closes its
    window. A window lasting > 1.5 reset_ms or with < 3 samples is a failed reset: ok False."""
    out, cur = [], []
    for s in samples:
        cur.append(s)
        sr = s.get("since_reset_ms")
        if sr is not None and sr >= reset_ms:
            out.append(cur)
            cur = []
    res = []
    for w in out:
        f = [sample_fields(s) for s in w]
        dur = f[-1][7]
        ok = len(w) >= 3 and dur is not None and dur <= 1.5 * reset_ms
        means = [x[1] for x in f if x[1] is not None]
        highs = [x[3] for x in f if x[3] is not None]
        ios = [x[6] for x in f if x[6] is not None]
        ws = [x[4] for x in f if x[4] is not None]
        mhz = [x[5] for x in f if x[5] is not None]
        res.append({"t_start": f[0][0], "t_end": f[-1][0], "ok": ok, "n": len(w),
                    "max_mean": max(means) if means else None, "min_mean": min(means) if means else None,
                    "max_high": max(highs) if highs else None, "max_io": max(ios) if ios else None,
                    "board_w": sorted(ws)[len(ws) // 2] if ws else None, "mhz": sorted(set(mhz))})
    return res


# ----------------------------------------------------------------------------------------------- virtual time
def vnow_ms():
    r = time.time() * 1000.0
    if dry():
        vt0 = float(os.environ.get("OH_VT0", "0") or 0)
        sp = float(os.environ.get("OH_DRY_SPEED", "1") or 1)
        if vt0:
            return vt0 + (r - vt0) * sp
    return r


def vsleep(s):
    sp = float(os.environ.get("OH_DRY_SPEED", "1") or 1) if dry() else 1.0
    time.sleep(max(0.0, s / sp))


# ----------------------------------------------------------------------------------------------- the watcher
def watch_step(caps, st, x):
    """One sample through the caps (pure; the self-test drives it). st keeps: hard, soft, n_w_soft, n_w_hard,
    target. Returns (stop_file_needed, session_stop_needed)."""
    t, m, hi, w = x[0], x[1], x[3], x[4]
    sess = False
    if st.get("hard") is None:
        if m >= caps["abs_stop_c"] or (hi is not None and hi >= caps["abs_stop_c"]):
            st["hard"] = "ABS88"
            sess = True
        if w is not None and w >= caps["hard_board_w"]:
            st["n_w_hard"] = st.get("n_w_hard", 0) + 1
            if st["n_w_hard"] >= caps["cap_consecutive"] and st.get("hard") is None:
                st["hard"] = "HARDW"
                sess = True
        else:
            st["n_w_hard"] = 0
    # soft caps: the temperature caps act on one sample (the high is a 1 s peak-hold, so a spike stays for its window
    # anyway), the board cap on cap_consecutive samples; released 1 C / 2 W below the cap
    reason = None
    if hi is not None and hi >= caps["cap_high_c"]:
        reason = "SOFT_HIGH"
    elif m >= caps["cap_mean_c"]:
        reason = "SOFT_MEAN"
    if w is not None and w >= caps["cap_board_w"]:
        st["n_w_soft"] = st.get("n_w_soft", 0) + 1
        if st["n_w_soft"] >= caps["cap_consecutive"] and reason is None:
            reason = "SOFT_W"
    else:
        st["n_w_soft"] = 0
    if reason:
        st["soft"] = reason
    elif st.get("soft"):
        clear = ((hi is None or hi <= caps["cap_high_c"] - caps["soft_release_c"]) and
                 m <= caps["cap_mean_c"] - caps["soft_release_c"] and
                 (w is None or w <= caps["cap_board_w"] - caps["soft_release_w"]))
        if clear:
            st["soft"] = None
    tgt = st.get("target")
    at_target = tgt is not None and m >= tgt
    return (st.get("hard") is not None or st.get("soft") is not None or at_target), sess


def watch(a):
    """One run's live watcher. Reads the sampler's raw output as it grows and writes one state line atomically:
        t_ms mean high board_w mhz n hard soft target age_ms g_mean g_age_s wall_ms io_high tgt_hit
    (tgt_hit, amendment 1: 1 once a sample read the mean at or above the current heating target, sticky until the next
    target line)
    hard (sticky): ABS88 (mean or any sensor >= abs_stop_c: the session stops), HARDW (board >= hard_board_w for
    cap_consecutive samples: the session stops), GUARD90 / GUARD_STALE (card 0). soft: SOFT_HIGH / SOFT_MEAN / SOFT_W
    (released 1 C / 2 W below the cap). While any stop, a soft cap or the heating target (ctl "target <C>") holds, the
    heater's --stop-file is touched at every sample (level-triggered: block.sh removes it only before a heater launch
    it may start)."""
    P = params()
    caps = {k: float(v) for k, v in P["caps"].items()}
    tel, state, ctl = a["tel"], a["state"], a["ctl"]
    guard = a.get("guard") or ""
    stop_file, session_stop = a.get("stop_file") or "", a.get("session_stop") or ""
    pos, buf, gpos, gbuf = 0, "", 0, ""
    last, g_last = None, None
    n = 0
    st = {"hard": None, "soft": None, "target": None, "tgt_hit": 0}
    ctl_sig = None
    t_start = vnow_ms()
    parent = os.getppid()

    def touch(f):
        if f:
            try:
                open(f, "a").close()
            except Exception:
                pass

    def write_state():
        now = vnow_ms()
        f = lambda v: "-" if v is None else (("%.3f" % v) if isinstance(v, float) else str(v))
        age = (now - last[0]) if last else None
        g_age = ((now - g_last[0]) / 1000.0) if g_last else None
        line = " ".join(f(v) for v in [last[0] if last else None, last[1] if last else None, last[3] if last else None,
                                       last[4] if last else None, last[5] if last else None, n, st["hard"], st["soft"],
                                       st["target"], int(age) if age is not None else None,
                                       g_last[1] if g_last else None, g_age, int(time.time() * 1000),
                                       last[6] if last else None, st.get("tgt_hit", 0)])
        tmp = state + ".tmp"
        with open(tmp, "w") as fh:
            fh.write(line + "\n")
        os.replace(tmp, state)

    while True:
        try:
            s_ = os.stat(ctl)
            sig = (s_.st_mtime_ns, s_.st_size)
            if sig != ctl_sig:
                ctl_sig = sig
                for line in open(ctl):
                    p = line.split()
                    if not p:
                        continue
                    if p[0] == "quit":
                        write_state()
                        return 0
                    if p[0] == "target":
                        st["target"] = None if p[1] == "off" else float(p[1])
                        st["tgt_hit"] = 0          # amendment 1: sticky, set by the first sample at or above it
        except FileNotFoundError:
            pass
        try:
            with open(tel, errors="replace") as fh:
                fh.seek(pos)
                chunk = fh.read()
                pos = fh.tell()
        except FileNotFoundError:
            chunk = ""
        buf += chunk
        lines = buf.split("\n")
        buf = lines.pop()
        need_stop = False
        for line in lines:
            if not line.startswith("{"):
                continue
            try:
                s = json.loads(line)
            except Exception:
                continue
            x = sample_fields(s)
            if x[0] is None or x[1] is None:
                continue
            last = x
            n += 1
            was_hard = st["hard"]
            if st.get("target") is not None and x[1] >= st["target"]:
                st["tgt_hit"] = 1
            ns, sess = watch_step(caps, st, x)
            need_stop = need_stop or ns
            if st["hard"] and not was_hard:        # the reading that tripped the hard stop, for the block's marks
                with open(state + ".hard", "w") as fh:
                    fh.write(json.dumps({"hard": st["hard"], "t_ms": x[0], "mean": x[1], "high": x[3], "board_w": x[4]}) + "\n")
            if sess:
                touch(session_stop)
        if guard:
            try:
                if os.path.getsize(guard) < gpos:
                    gpos, gbuf = 0, ""
            except OSError:
                pass
            try:
                with open(guard, errors="replace") as fh:
                    fh.seek(gpos)
                    gchunk = fh.read()
                    gpos = fh.tell()
            except FileNotFoundError:
                gchunk = ""
            gbuf += gchunk
            gl = gbuf.split("\n")
            gbuf = gl.pop()
            for line in gl:
                if line.startswith("{"):
                    try:
                        gx = sample_fields(json.loads(line))
                    except Exception:
                        continue
                    if gx[0] is not None and gx[1] is not None:
                        g_last = gx
                        if gx[1] > caps["guard_stop_c"] and st["hard"] is None:
                            st["hard"] = "GUARD90"
                            with open(state + ".hard", "w") as fh:
                                fh.write(json.dumps({"hard": "GUARD90", "t_ms": gx[0], "card0_mean": gx[1]}) + "\n")
                            touch(session_stop)
            ref = g_last[0] if g_last else t_start + 20000.0
            if vnow_ms() - ref > caps["guard_stale_s"] * 1000.0 and st["hard"] is None:
                st["hard"] = "GUARD_STALE"
                touch(session_stop)
        if last is not None:
            tgt = st.get("target")
            if st["hard"] or st["soft"] or (tgt is not None and last[1] >= tgt) or need_stop:
                touch(stop_file)
        write_state()
        try:
            os.kill(parent, 0)
        except OSError:
            return 0
        time.sleep(0.05)


def guardcheck(path, gate, max_age):
    lines = [l for l in open(path, errors="replace").read().splitlines() if l.startswith("{")] if os.path.exists(path) else []
    if not lines:
        return False, "no guard line"
    try:
        x = sample_fields(json.loads(lines[-1]))
    except Exception:
        return False, "unreadable guard line"
    age = (vnow_ms() - x[0]) / 1000.0
    if age > max_age:
        return False, "guard stale %.1f s" % age
    if x[1] is None or x[1] > gate:
        return False, "card 0 mean %s C > %s" % (x[1], gate)
    return True, "card 0 mean %s C, age %.1f s" % (x[1], age)


# ----------------------------------------------------------------------------------------------- kernel checks
PREFIX = {"SPARSITY": "SPARSITY {", "MMB": "MMBENCH {", "ONCHIP": "ONCHIP {", "MEMPROBE": "MEMPROBE {"}


def result_lines(path, tool):
    pre = PREFIX[tool]
    out = []
    if not os.path.exists(path):
        return out
    with open_any(path) as f:
        for line in f:
            i = line.find(pre)
            if i >= 0:
                try:
                    out.append(json.loads(line[i + len(pre) - 1:]))
                except Exception:
                    pass
    return out


def check_record(r, tool):
    """(checked, bad reason or None) of one result record (the host-side comparisons each tool makes)."""
    te = (r.get("tensor_errors") or 0) > 0
    notok = r.get("ok") is False
    if tool == "SPARSITY":
        if r.get("test") == "fma":
            res = r.get("result")
            if res in ("both", "math", "prm-literal"):
                chk, bad = True, None
            elif res == "wrong":
                chk, bad = True, "wrong result"
            else:
                chk, bad = False, None
        elif "wrong" in r:
            chk = True
            bad = "wrong %s" % r["wrong"] if (r.get("wrong") or 0) > 0 else None
            if (r.get("timeouts") or 0) > 0:
                bad = (bad + "; " if bad else "") + "timeouts %s" % r["timeouts"]
        else:
            chk, bad = False, None
    elif tool == "MMB":
        chk = r.get("check") in ("exact", "approx")
        bad = None
        if (r.get("bad_minions") or 0) > 0 or (r.get("launch_errors") or 0) > 0:
            bad = "bad_minions %s launch_errors %s" % (r.get("bad_minions"), r.get("launch_errors"))
        if r.get("check") not in ("exact", "approx"):
            chk = False
    elif tool == "ONCHIP":
        if r.get("test") == "relay":
            chk = True
            bad = "wrong_elements %s" % r["wrong_elements"] if (r.get("wrong_elements") or 0) > 0 else None
        elif r.get("test") == "probe":
            chk = (r.get("minions_wrote") or 0) > 0 and (r.get("minions_read") or 0) > 0
            w = (r.get("self_readback_wrong") or 0) + (r.get("remote_blocks_wrong") or 0)
            bad = "probe wrong self %s remote %s" % (r.get("self_readback_wrong"), r.get("remote_blocks_wrong")) if w else None
        else:
            chk, bad = False, None
    elif tool == "MEMPROBE":
        chk, bad = False, None
    else:
        chk, bad = False, None
    if te:
        bad = (bad + "; " if bad else "") + "tensor_errors %s" % r.get("tensor_errors")
    if notok and bad is None and chk:
        bad = "ok false"
    return chk, bad


def kcheck(path, tool):
    recs = result_lines(path, tool)
    if not recs:
        return "NORESULT", 0, []
    bads, n_chk, unchk = [], 0, 0
    for r in recs:
        chk, bad = check_record(r, tool)
        n_chk += chk
        unchk += (not chk) and tool != "MEMPROBE"
        if bad:
            bads.append(bad)
    if bads:
        return "BAD", n_chk, bads
    if tool != "MEMPROBE" and n_chk == 0:
        return "UNCHECKED", 0, ["%d record(s), none compared" % len(recs)]
    if unchk:
        return "PARTIAL", n_chk, ["%d record(s) not compared" % unchk]
    return "OK", n_chk, []


# ----------------------------------------------------------------------------------------------- locks, overrides
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def rel(p):
    return os.path.relpath(os.path.abspath(p), ROOT)


def binhash(pairs):
    out = {}
    for kv in pairs:
        role, path = kv.split("=", 1)
        full = path if os.path.isabs(path) else os.path.join(ROOT, path)
        out[role] = {"path": path, "sha256": sha256(full) if os.path.isfile(full) else None}
    return out


OVERRIDES = ["V3_FORCE", "OH_PARAMS", "OH_PREREG_DIR", "OH_BATTERY"]


def envcheck(card=None):
    bad = sorted(k for k in OVERRIDES if os.environ.get(k))
    return (dry() or not bad), bad


LOCK_BEGIN, LOCK_END = "<!-- lock-begin -->", "<!-- lock-end -->"


def prereg_dir():
    d = os.environ.get("OH_PREREG_DIR")
    if d and not dry():
        raise Refused("OH_PREREG_DIR is honoured only under V3_DRY=1")
    return d or os.path.join(HERE, "prereg")


def parse_lock(md_path):
    txt = open(md_path, errors="replace").read()
    if LOCK_BEGIN not in txt or LOCK_END not in txt:
        raise ValueError("%s has no lock block" % md_path)
    body = txt.split(LOCK_BEGIN, 1)[1].split(LOCK_END, 1)[0].strip().strip("`").strip()
    if body.startswith("json"):
        body = body[4:]
    return json.loads(body)


def preregcheck(card, bins_path):
    """The PREREG lock of every non-smoke block: PREREG.md's sha256 equals PREREG.sha256 and $OH_PREREG_SHA256 (the
    value recorded outside the tree when prereg.py printed it); every locked file unchanged; this card's binaries as
    frozen. Returns (ok, why, record)."""
    d = prereg_dir()
    md, shaf = os.path.join(d, "PREREG.md"), os.path.join(d, "PREREG.sha256")
    if not os.path.exists(md) or not os.path.exists(shaf):
        if dry():
            return True, "DRY: no PREREG yet in %s (a card block would be refused)" % rel(d), {"prereg_sha256": None, "dry": True}
        return False, "no PREREG.md / PREREG.sha256 in %s" % rel(d), None
    h = sha256(md)
    rec = open(shaf).read().split()[0] if open(shaf).read().split() else ""
    if h != rec:
        return False, "PREREG.md sha256 %s != PREREG.sha256 %s" % (h[:12], rec[:12]), None
    env = os.environ.get("OH_PREREG_SHA256", "")
    if not dry() and env != h:
        return False, "OH_PREREG_SHA256 (%s) != PREREG.md's sha256 %s" % (env[:12] or "unset", h[:12]), None
    lock = parse_lock(md)
    bad = []
    for f, want in sorted(lock.get("files", {}).items()):
        p = os.path.join(ROOT, f)
        got = sha256(p) if os.path.isfile(p) else None
        if got != want:
            bad.append("%s %s != %s" % (f, (got or "missing")[:12], want[:12]))
    bins = load_json(bins_path, {}) if bins_path else {}
    want_b = (lock.get("binaries") or {}).get(card)
    if want_b is None and not dry():
        bad.append("no frozen binaries for %s" % card)
    for role, v in (want_b or {}).items():
        got = (bins.get(role) or {}).get("sha256")
        if got != v:
            bad.append("binary %s %s != %s" % (role, (got or "missing")[:12], v[:12]))
    if bad:
        return False, "; ".join(bad), None
    return True, "PREREG %s: %d files and %d binaries match" % (h[:12], len(lock.get("files", {})), len(want_b or {})), \
        {"prereg_sha256": h, "files": len(lock.get("files", {})), "card": card}


# ----------------------------------------------------------------------------------------------- dry simulator
# V3_DRY=1 runs a block against a small two-stage thermal model on an accelerated clock (OH_DRY_SPEED, default 40), so
# the block logic (heating to a band, holding it, the chain rule, the caps, the guard, the checks, the follow-up) and
# the reducer run end to end with no device. Its numbers mean nothing about the cards.
DRY_CARDS = {
    "aifoundry3": {"P_idle": 25.7, "R": [0.55, 1.05], "tau": [6.0, 150.0], "rest": 56.0},
    "aifoundry1-c1": {"P_idle": 34.0, "R": [0.6, 1.1], "tau": [4.0, 100.0], "rest": 58.0},
}


def _dry_dir():
    d = os.environ.get("OH_DRY_DIR") or os.path.join(ROOT, "build", "claims-v3-dry", "oh-sim")
    os.makedirs(d, exist_ok=True)
    return d


def _dry_card(a):
    return a.get("card") or os.environ.get("OH_DRY_CARD") or "aifoundry3"


def _dry_load(card):
    check_card(card)
    st = load_json(os.path.join(_dry_dir(), "sim-%s.json" % card))
    cfg = dict(DRY_CARDS[card])
    rest = os.environ.get("OH_DRY_REST")
    if rest:
        cfg["rest"] = float(rest)
    if not st:
        T_amb = cfg["rest"] - sum(cfg["R"]) * cfg["P_idle"]
        st = {"t": vnow_ms(), "x": [cfg["P_idle"]] * 2, "T_amb": T_amb, "cfg": cfg, "hot": 0.0, "io": 0.0}
    return st


def _dry_save(card, st):
    p = os.path.join(_dry_dir(), "sim-%s.json" % card)
    json.dump(st, open(p + ".tmp", "w"))
    os.replace(p + ".tmp", p)


def _dry_launches(card):
    d = {}
    for l in load_jsonl(os.path.join(_dry_dir(), "launches-%s.jsonl" % card)):
        d[l["id"]] = l
    return list(d.values())


def _dry_power(st, t, launches):
    cfg = st["cfg"]
    P, conc = cfg["P_idle"], 0.0
    for l in launches:
        if l["t0"] <= t < l.get("t1", 0):
            w = 0.0256 * l["minions"]
            P += w
            conc += w * (3.0 if l["minions"] <= 32 else 1.5 if l["minions"] <= 128 else 0.1)
    # leakage: idle power grows with the die temperature (only so the dry idle tail has a slope)
    T = st.get("T", cfg["rest"])
    P += 0.35 * (T - cfg["rest"])
    return P, conc


def _dry_advance(st, t_to, launches, emit=None):
    cfg = st["cfg"]
    t = st["t"]
    launches = [l for l in launches if l.get("t1", 0) >= t - 1000]      # only the launches that can still matter
    rng = random.Random(int(t) % 100000)
    while t + 100 <= t_to:
        t += 100
        P, conc = _dry_power(st, t, launches)
        x = st["x"]
        a0 = 1 - math.exp(-0.1 / cfg["tau"][0])
        a1 = 1 - math.exp(-0.1 / cfg["tau"][1])
        x[0] += a0 * (P - x[0])
        x[1] += a1 * (P - x[1])
        T = st["T_amb"] + cfg["R"][0] * x[0] + cfg["R"][1] * x[1]
        st["hot"] += (1 - math.exp(-0.1 / 3.0)) * (conc * 0.35 - st["hot"])
        st["T"] = T
        if emit:
            n = rng.gauss(0, 0.15)
            m = int(math.floor(T + n))
            hi = int(math.floor(T + 1.6 + st["hot"] + float(os.environ.get("OH_DRY_DHOT", "0")) + n))
            lo = int(math.floor(T - 3.0 + n))
            iov = int(math.floor(T - 0.5 + n))
            emit(t, m, lo, hi, iov, P + rng.gauss(0, 0.15))
    st["t"] = t
    return st


def dry_sampler(a):
    card = _dry_card(a)
    secs = float(a.get("seconds", 10))
    every = int(a.get("every_ms", 100))
    reset = int(a.get("reset_ms", 0) or 0)
    stop = {"now": False}
    signal.signal(signal.SIGTERM, lambda *_: stop.update(now=True))
    signal.signal(signal.SIGINT, lambda *_: stop.update(now=True))
    st = _dry_load(card)
    t_begin = vnow_ms()
    if st["t"] < t_begin - 3.6e6:
        st["t"] = t_begin
    st = _dry_advance(st, t_begin, _dry_launches(card))
    win = {"t0": t_begin, "lo": None, "hi": None, "iohi": None, "last": 0}
    fh = open(a["out"], "a")

    def emit(t, m, lo, hi, iov, w):
        if t - win["last"] < every:
            return
        win["last"] = t
        sr = int(t - win["t0"]) if reset else -1
        if reset:
            win["lo"] = lo if win["lo"] is None else min(win["lo"], lo)
            win["hi"] = hi if win["hi"] is None else max(win["hi"], hi)
            win["iohi"] = iov if win["iohi"] is None else max(win["iohi"], iov)
            L, H, IO = win["lo"], win["hi"], win["iohi"]
        else:
            L, H, IO = lo, hi, iov
        fh.write(json.dumps({"t_ms": int(t), "took_ms": 20, "since_reset_ms": sr, "board_w": round(w, 2),
                             "temp_c": {"pmic": m, "ioshire": [iov, iov - 2, IO], "minshire": [m, L, H]},
                             "die_mv": {"minion": 522, "sram": 698, "noc": 484, "ddr": 766},
                             "mhz": {"minion": 600, "noc": 400, "ddr": 933}}, separators=(",", ":")) + "\n")
        fh.flush()
        if reset and sr >= reset:
            win.update(t0=t, lo=None, hi=None, iohi=None)

    lf = os.path.join(_dry_dir(), "launches-%s.jsonl" % card)
    known, pos = {}, 0
    while not stop["now"] and vnow_ms() - t_begin < secs * 1000.0:
        try:                                    # read the launch list incrementally (it grows by two lines a launch)
            with open(lf) as f:
                f.seek(pos)
                for line in f:
                    if line.endswith("\n"):
                        l = json.loads(line)
                        known[l["id"]] = l
                        pos += len(line.encode())
                    else:
                        break
        except FileNotFoundError:
            pass
        now = vnow_ms()
        cur = [l for l in known.values() if l.get("t1", 0) >= st["t"] - 1000]
        known = {l["id"]: l for l in cur}
        st = _dry_advance(st, now, cur, emit)
        _dry_save(card, st)
        time.sleep(0.02)
    fh.close()
    return 0


def dry_guard(a):
    secs = float(a.get("seconds", 10))
    every = int(a.get("every_ms", 1000))
    stop = {"now": False}
    signal.signal(signal.SIGTERM, lambda *_: stop.update(now=True))
    rest = float(os.environ.get("OH_DRY_REST_C0", "63"))
    ramp = float(os.environ.get("OH_DRY_C0_RAMP", "0"))
    t_begin, last = vnow_ms(), 0
    with open(a["out"], "a") as fh:
        while not stop["now"] and vnow_ms() - t_begin < secs * 1000.0:
            t = vnow_ms()
            if t - last >= every:
                last = t
                m = int(math.floor(rest + ramp * (t - t_begin) / 60000.0))
                fh.write(json.dumps({"t_ms": int(t), "took_ms": 20, "since_reset_ms": -1, "board_w": 18.0,
                                     "temp_c": {"pmic": m, "ioshire": [m, m - 2, m + 1], "minshire": [m, m - 3, m + 2]},
                                     "mhz": {"minion": 300, "noc": 400, "ddr": 933}}, separators=(",", ":")) + "\n")
                fh.flush()
            time.sleep(0.02)
    return 0


def dry_die(a):
    card = _dry_card(a)
    st = _dry_load(card)
    if st["t"] < vnow_ms() - 3.6e6:
        st["t"] = vnow_ms()
    st = _dry_advance(st, vnow_ms(), _dry_launches(card))
    _dry_save(card, st)
    print(int(math.floor(st.get("T", st["cfg"]["rest"]))))
    return 0


def _dry_register(card, minions, secs):
    lf = os.path.join(_dry_dir(), "launches-%s.jsonl" % card)
    t0 = vnow_ms() + 200
    lid = "%d-%d" % (int(t0), os.getpid())
    with open(lf, "a") as f:
        f.write(json.dumps({"id": lid, "t0": t0, "t1": t0 + 30 + secs * 1000 + 20, "minions": minions}) + "\n")
    return lf, lid, t0


def dry_heater(a):
    """A fake sparsity_host heater (fp32 randn, --seconds): registers its power with the model, sleeps its accelerated
    duration (honouring --stop-file between its 0.5 s inner launches) and prints SPARSITY lines on the virtual clock."""
    card = _dry_card(a)
    args = a["argv"]
    opt = lambda name, default: args[args.index(name) + 1] if name in args else default
    mask = int(opt("--shires", "0xffffffff"), 0)
    per = int(opt("--per-shire", "32"))
    secs = float(opt("--seconds", "0"))
    stopf = opt("--stop-file", "")
    minions = bin(mask).count("1") * per
    lf, lid, t0 = _dry_register(card, minions, secs)
    ghz = 0.59945
    line = lambda n, ts, te, it: "SPARSITY " + json.dumps(
        {"test": "fma", "type": "fp32", "pattern": "none", "values": "randn", "minions": minions, "shire_mask": hex(mask),
         "iters": it, "launch": n, "cycles_max": int(it * 546.001), "cycles_per_op": 546.001, "wall_s": (te - ts) / 1000.0,
         "t_start_ms": int(ts), "t_end_ms": int(te), "ghz": ghz, "tensor_errors": 0, "result": "unchecked", "ok": True},
        separators=(",", ":"))
    out, t = [], t0
    vsleep(0.2)
    out.append(line(-1, t, t + 30, 20000))
    t += 30
    stopped, k = False, 0
    while t < t0 + 30 + secs * 1000 - 1:
        if stopf and os.path.exists(stopf):
            stopped = True
            break
        vsleep(0.5)
        out.append(line(k, t, t + 500, 549000))
        t += 500
        k += 1
    with open(lf, "a") as f:
        f.write(json.dumps({"id": lid, "t0": t0, "t1": t, "minions": minions}) + "\n")
    for l in out:
        print(l)
    if stopped:
        print("stopping: %s exists" % stopf, file=sys.stderr)
    vsleep(0.3)
    return 0


def dry_kernel(a):
    """A fake battery kernel or memprobe program: a short launch in the model and a result line in the tool's format.
    Test hooks: OH_DRY_FAIL=<kernel name>:<C> reports a wrong result while the model's die reads >= C (the
    follow-up path: it repeats hot and passes cool); OH_DRY_VOID=<kernel name> makes that kernel's first launch in a
    block crash with no result (the void path; marker file in OH_DRY_DIR)."""
    card = _dry_card(a)
    name, tool = a["name"], a["tool"]
    args = a["argv"]
    opt = lambda k, d: args[args.index(k) + 1] if k in args else d
    vh = os.environ.get("OH_DRY_VOID", "")
    mk = os.path.join(_dry_dir(), "void-%s-%s" % (card, name))
    if vh == name and not os.path.exists(mk):
        open(mk, "w").close()
        vsleep(1.08)
        print("dry: host crash at 1.08 s (the g3log race)", file=sys.stderr)
        return 134
    st = _dry_load(card)
    st = _dry_advance(st, vnow_ms(), _dry_launches(card))
    T = st.get("T", st["cfg"]["rest"])
    wrong = False
    fh = os.environ.get("OH_DRY_FAIL", "")
    if fh and ":" in fh:
        fn, fc = fh.split(":", 1)
        wrong = fn == name and T >= float(fc)
    lf, lid, t0 = _dry_register(card, 1024, 0.05)
    vsleep(0.4)
    ts, te = int(t0), int(t0 + 50)
    rng = random.Random(int(t0))
    recs = []
    if tool == "SPARSITY" and opt("--test", "") == "fma":
        for sp in opt("--sweep", "0").split(","):
            recs.append("SPARSITY " + json.dumps({"test": "fma", "type": opt("--type", "fp32"), "pattern": opt("--pattern", ""),
                        "values": "int", "sparsity": float(sp), "minions": 1024, "iters": int(opt("--iters", "4000")),
                        "launch": -1, "cycles_max": 2184004, "cycles_per_op": 546.001, "wall_s": 0.004, "t_start_ms": ts,
                        "t_end_ms": te, "ghz": 0.5994, "tensor_errors": 0, "result": "wrong" if wrong else "both", "ok": True}))
    elif tool == "SPARSITY":
        for sp in opt("--sweep", "0").split(","):
            recs.append("SPARSITY " + json.dumps({"test": "gemv", "gemv": "dense", "timeouts": 0, "sparsity": float(sp),
                        "minions": 1024, "iters": 2000, "launch": -1, "cycles_per_layer_mean": 5000.0 + rng.random(),
                        "cycles_per_layer_max": 5200.0 + rng.random(), "wall_s": 0.02, "t_start_ms": ts, "t_end_ms": te,
                        "ghz": 0.5994, "wrong": 7 if wrong else 0, "tensor_errors": 0, "ok": True}))
    elif tool == "MMB":
        recs.append("MMBENCH " + json.dumps({"device": "silicon", "mode": opt("-m", "int8"), "minions": 1024, "iters": 100,
                    "launch": 0, "t_start_ms": ts, "t_end_ms": te, "cycles_max": 455318 + rng.randrange(900),
                    "check": "exact", "bad_minions": 3 if wrong else 0, "launch_errors": 0}))
    elif tool == "ONCHIP" and opt("--test", "") == "relay":
        recs.append("ONCHIP " + json.dumps({"test": "relay", "medium": opt("--medium", "dram"), "stages": int(opt("--stages", "4")),
                    "minions": 1024, "cycles_max": 52000000 + rng.randrange(90000), "bytes_per_cycle": 82.6,
                    "wrong_elements": 11 if wrong else 0, "t_start_ms": ts, "t_end_ms": te, "ok": not wrong}))
    elif tool == "ONCHIP":
        recs.append("ONCHIP " + json.dumps({"test": "probe", "method": 0, "shift": 1, "minions_wrote": 1024,
                    "self_readback_wrong": 0, "minions_read": 1024, "remote_blocks_wrong": 2 if wrong else 0,
                    "remote_words_wrong": 9 if wrong else 0, "wall_s": 0.01, "ok": not wrong}))
    elif tool == "MEMPROBE":
        prog = opt("--program", "")
        outd = opt("--out-dir", ".")
        nm = os.path.basename(prog)[:-4] if prog.endswith(".ops") else "prog"
        meta = load_json(os.path.join(os.path.dirname(prog), nm + ".json"), {"labels": []})
        nlab = len(meta.get("labels", []))
        vals, tcyc = [], 0
        period = 2325.4
        jit = "jit" in nm
        for i in range(nlab // 2):
            tcyc += 300 + (rng.randrange(3000) if jit else 0)
            lat = 300 if (tcyc % period) < 250 else 215
            vals += [tcyc % 2**32, lat + 5]
            tcyc += lat
        vals += [0] * (nlab - len(vals))
        os.makedirs(outd, exist_ok=True)
        with open(os.path.join(outd, nm + ".u32"), "wb") as f:
            f.write(struct.pack("<%dI" % len(vals), *vals))
        recs.append("MEMPROBE " + json.dumps({"test": "program", "name": nm, "hart": 0, "arena_base": "0x8040000000",
                                               "n_results": nlab, "t_start_ms": ts, "t_end_ms": te, "ok": True}))
    with open(lf, "a") as f:
        f.write(json.dumps({"id": lid, "t0": t0, "t1": t0 + 50, "minions": 1024}) + "\n")
    for r in recs:
        print(r)
    vsleep(0.2)
    return 0


# ----------------------------------------------------------------------------------------------- self-test
def selftest():
    P = params()
    caps = {k: float(v) for k, v in P["caps"].items()}
    ok = True

    def expect(cond, what):
        nonlocal ok
        print(("ok   " if cond else "FAIL ") + what)
        ok = ok and cond

    S = lambda m, hi, w: (1, m, m - 3, hi, w, 600, m, 100)
    st = {"hard": None, "soft": None, "target": None}
    ns, sess = watch_step(caps, st, S(80, 83, 60))
    expect(not ns and not sess and st["soft"] is None, "80/83/60 W: no stop")
    ns, sess = watch_step(caps, st, S(83, 86, 60))
    expect(ns and not sess and st["soft"] == "SOFT_HIGH", "high 86: soft stop of the heater, no session stop")
    ns, _ = watch_step(caps, st, S(83, 86, 60))
    expect(ns and st["soft"] == "SOFT_HIGH", "high still 86: soft holds")
    ns, _ = watch_step(caps, st, S(83, 85, 60))
    expect(st["soft"] is None and not ns, "high 85: released (1 C below the cap)")
    ns, _ = watch_step(caps, st, S(85, 85, 60))
    expect(ns and st["soft"] == "SOFT_MEAN", "mean 85: soft")
    st = {"hard": None, "soft": None, "target": None}
    watch_step(caps, st, S(70, 72, 78.5))
    expect(st["soft"] is None, "one board sample at 78.5 W: not yet")
    watch_step(caps, st, S(70, 72, 78.2))
    expect(st["soft"] == "SOFT_W", "two board samples >= 78 W: soft")
    watch_step(caps, st, S(70, 72, 76.5))
    expect(st["soft"] == "SOFT_W", "76.5 W: still soft (release at 76)")
    watch_step(caps, st, S(70, 72, 75.9))
    expect(st["soft"] is None, "75.9 W: released")
    st = {"hard": None, "soft": None, "target": None}
    ns, sess = watch_step(caps, st, S(84, 88, 70))
    expect(ns and sess and st["hard"] == "ABS88", "a sensor at 88: hard stop, session stop")
    watch_step(caps, st, S(70, 72, 50))
    expect(st["hard"] == "ABS88", "hard stop is sticky")
    st = {"hard": None, "soft": None, "target": None}
    ns, sess = watch_step(caps, st, S(88, 87, 70))
    expect(sess and st["hard"] == "ABS88", "mean at 88: hard stop")
    st = {"hard": None, "soft": None, "target": None}
    watch_step(caps, st, S(70, 72, 82.5))
    ns, sess = watch_step(caps, st, S(70, 72, 82.1))
    expect(sess and st["hard"] == "HARDW", "two samples >= 82 W: hard power stop")
    st = {"hard": None, "soft": None, "target": 62.0}
    ns, _ = watch_step(caps, st, S(61, 63, 40))
    expect(not ns, "target 62, mean 61: heat on")
    ns, _ = watch_step(caps, st, S(62, 64, 40))
    expect(ns, "target 62, mean 62: heater stop")
    # checks
    d = tempfile.mkdtemp()
    f = os.path.join(d, "k.out")
    open(f, "w").write('noise\nSPARSITY {"test":"fma","result":"both","tensor_errors":0,"ok":true}\n')
    expect(kcheck(f, "SPARSITY")[0] == "OK", "fma both: OK")
    open(f, "w").write('SPARSITY {"test":"fma","result":"unchecked","tensor_errors":0,"ok":true}\n')
    expect(kcheck(f, "SPARSITY")[0] == "UNCHECKED", "fma unchecked: UNCHECKED")
    open(f, "w").write('SPARSITY {"test":"fma","result":"both","tensor_errors":2,"ok":true}\n')
    expect(kcheck(f, "SPARSITY")[0] == "BAD", "tensor error: BAD")
    open(f, "w").write('SPARSITY {"test":"gemv","wrong":0,"timeouts":0,"tensor_errors":0,"ok":true}\n')
    expect(kcheck(f, "SPARSITY")[0] == "OK", "gemv wrong 0: OK")
    open(f, "w").write('MMBENCH {"check":"exact","bad_minions":0,"launch_errors":0}\n')
    expect(kcheck(f, "MMB")[0] == "OK", "mmbench exact: OK")
    open(f, "w").write('MMBENCH {"check":"exact","bad_minions":1,"launch_errors":0}\n')
    expect(kcheck(f, "MMB")[0] == "BAD", "mmbench bad minion: BAD")
    open(f, "w").write('ONCHIP {"test":"relay","wrong_elements":0,"ok":true}\n')
    expect(kcheck(f, "ONCHIP")[0] == "OK", "relay 0 wrong: OK")
    open(f, "w").write('ONCHIP {"test":"probe","minions_wrote":1024,"minions_read":1024,"self_readback_wrong":0,"remote_blocks_wrong":1,"ok":false}\n')
    expect(kcheck(f, "ONCHIP")[0] == "BAD", "probe remote wrong: BAD")
    open(f, "w").write("Segmentation fault\n")
    expect(kcheck(f, "ONCHIP")[0] == "NORESULT", "no result line: NORESULT")
    for c in ("aifoundry1-c0", "aifoundry2", "aifoundry1"):
        try:
            check_card(c)
            expect(False, "card %s refused" % c)
        except Refused:
            expect(True, "card %s refused" % c)
    for p in (301, 100, 202):
        try:
            plan(p, "aifoundry3")
            expect(False, "pass %d refused" % p)
        except (Refused, ValueError):
            expect(True, "pass %d refused" % p)
    try:
        plan(103, "aifoundry1-c1")
        expect(False, "card 1 pass 103 refused (2 OH-1 blocks)")
    except Refused:
        expect(True, "card 1 pass 103 refused (2 OH-1 blocks)")
    rows = P["oh1"]["williams_rows"]
    pairs = set()
    for r in rows:
        for a_, b_ in zip(r, r[1:]):
            pairs.add((a_, b_))
    expect(len(pairs) == 12 and all(sorted(r) == sorted(rows[0]) for r in rows), "the Williams square: each ordered pair once")
    print("selftest: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


# ----------------------------------------------------------------------------------------------- main
def _kv(argv):
    a, rest = {}, []
    i = 0
    while i < len(argv):
        if argv[i] == "--":
            rest = argv[i + 1:]
            break
        if argv[i].startswith("--") and i + 1 < len(argv):
            a[argv[i][2:].replace("-", "_")] = argv[i + 1]
            i += 2
        else:
            rest.append(argv[i])
            i += 1
    a["argv"] = rest
    return a


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    cmd, a = argv[0], _kv(argv[1:])
    if cmd == "selftest":
        return selftest()
    if cmd == "check-card":
        try:
            check_card(a["card"])
            if a.get("pass"):
                plan(a["pass"], a["card"])
        except (Refused, ValueError) as e:
            print("REFUSED: %s" % e)
            return 2
        print("ok")
        return 0
    if cmd == "plan":
        try:
            info, P = plan(a["pass"], a["card"])
        except (Refused, ValueError) as e:
            print("REFUSED: %s" % e, file=sys.stderr)
            return 2
        for k, v in info.items():
            print("SET INFO_%s=%s" % (k, sh(v)))
        for k, v in P["caps"].items():
            print("SET P_%s=%s" % (k, sh(v)))
        print("SET P_chain_cap_s=%s" % sh(P["chain"]["cap_s"]))
        print("SET P_chain_gap_s=%s" % sh(P["chain"]["gap_s"]))
        print("SET P_reset_ms=%s" % sh(P["reset_ms"]))
        H = P["heater"]
        print("SET P_heat_mask=%s" % sh(H["mask"]))
        print("SET P_heat_all32=%s" % sh(H["per_shire_all32"]))
        print("SET P_heat_all24=%s" % sh(H["per_shire_all24"]))
        print("SET P_heat_s=%s" % sh(H["seconds"]))
        print("SET P_all24_above_c=%s" % sh(H["all24_above_c"][a["card"]]))
        o1 = P["oh1"]
        for k in ("preheat_c", "preheat_per_shire", "condition_s", "launch_s", "tail_s"):
            print("SET P1_%s=%s" % (k, sh(o1[k])))
        for name, c in o1["conditions"].items():
            print("COND %s %s %s" % (name, c["mask"] or "-", c["per_shire"]))
        o2 = P["oh2"]
        for k in ("cool_wait_s", "band_heat_s", "hold_heat_s", "tail_s", "tail_battery_at_c", "followup_repeats"):
            print("SET P2_%s=%s" % (k, sh(o2[k])))
        for b in o2["bands"]:
            rest = (b.get("rest_max_c") or {}).get(a["card"], "-")
            print("BAND %s %s %s %s %s %s %s %s" % (b["name"], b["lo"] if b["lo"] is not None else "-",
                                                    b["hi"] if b["hi"] is not None else "-", b.get("target", "-"),
                                                    b["batteries"], "1" if b.get("refresh") else "0", rest,
                                                    b.get("rest_wait_s", 0)))
        r = o2["refresh"]
        print("SET P2_rjit=%s" % sh("--n %d --jitter %d --start %s --seed %d" % (r["jit"]["n"], r["jit"]["jitter"], r["jit"]["start"], r["jit"]["seed"])))
        print("SET P2_rlocked=%s" % sh("--n %d --start %s" % (r["locked"]["n"], r["locked"]["start"])))
        return 0
    if cmd == "watch":
        return watch(a)
    if cmd == "guardcheck":
        okg, why = guardcheck(a["guard"], float(a.get("gate", 85)), float(a.get("max_age", 10)))
        print(why)
        return 0 if okg else 1
    if cmd == "kcheck":
        status, n, why = kcheck(a["file"], a["tool"])
        print("%s %d %s" % (status, n, "; ".join(why).replace(" ", "_") or "-"))
        return 0
    if cmd == "envcheck":
        okv, bad = envcheck(a.get("card"))
        if not okv:
            print("%s set without V3_DRY=1 (honoured only in dry tests)" % " ".join(bad))
            return 1
        print(" ".join(bad) if bad else "-")
        return 0
    if cmd == "binhash":
        print(json.dumps(binhash(a["argv"]), sort_keys=True))
        return 0
    if cmd == "preregcheck":
        okp, why, rec = preregcheck(a["card"], a.get("bins"))
        print(why)
        if okp and a.get("record"):
            json.dump(rec, open(a["record"], "w"), indent=1)
        return 0 if okp else 1
    if cmd == "vnow":
        print(int(vnow_ms()))
        return 0
    if cmd == "dry-sampler":
        return dry_sampler(a)
    if cmd == "dry-guard":
        return dry_guard(a)
    if cmd == "dry-die":
        return dry_die(a)
    if cmd == "dry-heater":
        return dry_heater(a)
    if cmd == "dry-kernel":
        return dry_kernel(a)
    print("unknown command %s" % cmd, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
