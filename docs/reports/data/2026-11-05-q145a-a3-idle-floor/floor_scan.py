#!/usr/bin/env python3
"""heat-q145a, Part 2: aifoundry3's idle floor across every committed aifoundry3 pass (post hoc, descriptive; committed files only).

Per pass directory that holds a telemetry file under an aifoundry3 path: its first and last sample time, the first sample's board W,
firmware die reading (temp_c.minshire[0]) and, where the sampler carried the 34 raw codes (pvt, status 0, no fault), the 34-sensor mean
by E97's code_to_c (as smoke_gate_e176.py has it); the mean over the first 3 s too; the minion clock. Passes are grouped into sessions by
a gap of more than 20 minutes between one pass's last sample and the next pass's first; a session's floor is its first pass's first
sample, and its rest is the gap since the previous committed session's last sample on this card. The M11-family sessions' R0 'room' and
start-gate marks are read too.

    python3 -B floor_scan.py <lab repo top> <out.json>
"""
import datetime as dt
import gzip
import json
import os
import sys

G_TS, H_TS, CAL5 = 57400, 249400, 4096


def code_to_c(n):
    return (G_TS + H_TS * n / CAL5 - H_TS / 2) / 1000.0


def m34(s):
    pv = s.get("pvt") or {}
    cs = pv.get("c") or []
    if pv.get("st") == 0 and not pv.get("f") and len(cs) == 34:
        return sum(code_to_c(x) for x in cs) / 34.0
    return None


def scan_tel(path):
    op = gzip.open if path.endswith(".gz") else open
    first, last, early = None, None, []
    n = 0
    try:
        with op(path, "rt", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not (line.startswith("{") and line.endswith("}")):
                    continue
                try:
                    s = json.loads(line)
                except ValueError:
                    continue
                if "t_ms" not in s or "board_w" not in s:
                    continue
                n += 1
                if first is None:
                    first = s
                if s["t_ms"] - first["t_ms"] < 3000:
                    early.append(s)
                last = s
    except (OSError, EOFError) as e:
        return {"error": str(e)}
    if first is None:
        return None
    def fw(s):
        try:
            return float(s["temp_c"]["minshire"][0])
        except (KeyError, IndexError, TypeError, ValueError):
            return None
    em = [m34(s) for s in early if m34(s) is not None]
    return {"t_first": first["t_ms"], "t_last": last["t_ms"], "n": n, "board_w": first["board_w"], "fw_c": fw(first),
            "m34_c": m34(first), "m34_first3s_c": (sum(em) / len(em)) if em else None,
            "board_first3s_w": sum(s["board_w"] for s in early) / len(early),
            "mhz": (first.get("mhz") or {}).get("minion"), "minion_mv": (first.get("die_mv") or {}).get("minion"),
            "has_pvt": first.get("pvt") is not None}


def marks_room(d):
    p = os.path.join(d, "marks.jsonl")
    out = []
    if not os.path.exists(p):
        return out
    for line in open(p, errors="replace"):
        if not line.startswith("{"):
            continue
        try:
            m = json.loads(line)
        except ValueError:
            continue
        if m.get("kind") in ("room", "start_gate", "rest_die") or (m.get("kind") == "rest" and "idle_c" in m):
            out.append({k: m[k] for k in m if k in ("kind", "name", "t_start_ms", "t_end_ms", "room_c", "room", "idle_c", "gate", "ok",
                                                    "line_c", "decision", "why", "mean34_c", "fw_c", "value_c", "pass", "rc", "level")})
    return out


def main():
    top, outp = sys.argv[1], sys.argv[2]
    D = os.path.join(top, "docs/reports/data")
    passes = []
    for dirpath, dirnames, filenames in os.walk(D):
        if "/aifoundry3" not in dirpath and "-aifoundry3" not in dirpath:
            continue
        tf = [f for f in filenames if f in ("telemetry.jsonl.gz", "telemetry.jsonl")]
        if not tf:
            continue
        rel = os.path.relpath(dirpath, D)
        if "aifoundry1" in rel or "aifoundry2" in rel.split("/")[-1]:
            continue
        r = scan_tel(os.path.join(dirpath, tf[0]))
        if not r or "error" in r:
            continue
        r["dir"] = rel
        r["exp_dir"] = rel.split("/")[0]
        r["marks"] = marks_room(dirpath)
        passes.append(r)
    passes.sort(key=lambda r: r["t_first"])
    # drop duplicates (the same pass committed twice) by first-sample time
    seen, uniq = set(), []
    for r in passes:
        if r["t_first"] in seen:
            continue
        seen.add(r["t_first"])
        uniq.append(r)
    sessions, cur = [], None
    for r in uniq:
        if cur is None or r["t_first"] - cur["t_last"] > 20 * 60 * 1000:
            cur = {"passes": [], "t_first": r["t_first"], "t_last": r["t_last"]}
            sessions.append(cur)
        cur["passes"].append(r)
        cur["t_last"] = max(cur["t_last"], r["t_last"])
    tz = dt.timezone(dt.timedelta(hours=-8))
    out = []
    prev_last = None
    for s in sessions:
        f = s["passes"][0]
        loc = dt.datetime.fromtimestamp(f["t_first"] / 1000, tz)
        rec = {"start_pst": loc.strftime("%a %d %b %H:%M:%S"), "hour_pst": loc.hour + loc.minute / 60.0,
               "first_dir": f["dir"], "exps": sorted(set(p["exp_dir"] for p in s["passes"])), "n_passes": len(s["passes"]),
               "dur_min": (s["t_last"] - s["t_first"]) / 60000.0,
               "rest_h": None if prev_last is None else (s["t_first"] - prev_last) / 3.6e6,
               "floor_board_w": f["board_w"], "floor_board_3s_w": f["board_first3s_w"], "floor_fw_c": f["fw_c"], "floor_m34_c": f["m34_c"],
               "floor_m34_3s_c": f["m34_first3s_c"], "mhz": f["mhz"], "minion_mv": f["minion_mv"],
               "rooms": [m for p in s["passes"] for m in p["marks"] if m.get("kind") in ("room", "start_gate")][:6],
               "t_first": s["t_first"], "t_last": s["t_last"]}
        out.append(rec)
        prev_last = s["t_last"]
    json.dump({"passes": len(uniq), "sessions": out}, open(outp, "w"), indent=1)
    for r in out:
        print(f"{r['start_pst']} h{r['hour_pst']:5.2f} rest {r['rest_h'] if r['rest_h'] is None else round(r['rest_h'], 2)} h, "
              f"{r['n_passes']:3d} passes {r['dur_min']:6.1f} min, board {r['floor_board_w']:.2f} W, fw {r['floor_fw_c']}, "
              f"m34 {None if r['floor_m34_c'] is None else round(r['floor_m34_c'], 3)}, {r['mhz']} MHz {r['minion_mv']} mV, {','.join(x[:24] for x in r['exps'])}")


if __name__ == "__main__":
    main()
