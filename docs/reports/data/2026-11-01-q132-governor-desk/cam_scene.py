#!/usr/bin/env python3
"""Q132(g): the camera's scene mean at the start of each committed camera session on aifoundry2, beside the room readings at rest.
Pure Python: reads the .npz with zipfile and the .npy header by hand. POST HOC, desk only, no card.

    cam_scene.py <repo> <hist-dir> > cam-scene.txt
"""
import ast
import glob
import json
import os
import statistics as st
import struct
import sys
import time
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import die_lines as DL

os.environ["TZ"] = "America/Los_Angeles"
time.tzset()


def npz(path):
    out = {}
    z = zipfile.ZipFile(path)
    for n in z.namelist():
        b = z.read(n)
        if b[:6] != b"\x93NUMPY":
            continue
        major = b[6]
        hl = struct.unpack("<H", b[8:10])[0] if major == 1 else struct.unpack("<I", b[8:12])[0]
        start = 10 + hl if major == 1 else 12 + hl
        hdr = ast.literal_eval(b[start - hl:start].decode("latin-1").strip())
        out[n.replace(".npy", "")] = (hdr, b[start:])
    return out


def floats(entry):
    hdr, raw = entry
    d = hdr["descr"]
    fmt = {"<f8": "d", "<f4": "f", "<i4": "i", "<i8": "q"}.get(d)
    if not fmt or len(hdr["shape"]) != 1:
        return None
    n = hdr["shape"][0]
    return list(struct.unpack("<%d%s" % (n, fmt), raw[:n * struct.calcsize(fmt)]))


def main():
    repo, hist = sys.argv[1], sys.argv[2]
    data = os.path.join(repo, "docs/reports/data")
    H = DL.Hist(os.path.join(hist, "aifoundry2"))
    A3 = DL.Hist(os.path.join(hist, "aifoundry3"))
    rows = []
    for red in sorted(glob.glob(os.path.join(data, "*", "**", "red", "fpa.npz"), recursive=True)):
        meta_p = os.path.join(os.path.dirname(red), "meta.json")
        if not os.path.exists(meta_p):
            continue
        meta = json.load(open(meta_p))
        Z = npz(red)
        name = os.path.relpath(red, data).replace("/red/fpa.npz", "")
        t0 = meta.get("t_zero_epoch_s") or meta.get("first_frame_epoch_s")
        if not t0:
            print(name, "no epoch", list(meta.keys())[:10])
            continue
        if not rows:
            print("npz keys in", name, {k: (v[0]["descr"], v[0]["shape"]) for k, v in Z.items()})
        series = {}
        for k, e in Z.items():
            f = floats(e)
            if f:
                series[k] = f
        ts = series.get("t_s") or series.get("t") or series.get("bin_t_s")
        rows.append((t0, name, series, ts, meta))
    print("session                                                  start (PDT)        keys")
    for t0, name, series, ts, meta in sorted(rows):
        info = {}
        for k, v in series.items():
            if k in ("t_s", "t", "bin_t_s"):
                continue
            head = v[: min(len(v), 120)]
            good = [x for x in head if x == x]
            if good:
                info[k] = round(st.median(good), 2)
        ms = t0 * 1000
        p = H.proxy(ms - 15 * 60000, ms)
        q = A3.proxy(ms - 15 * 60000, ms)
        print(f"{name:55s} {DL.fmt(ms):17s} first-minute medians {info} | a2 nic {p['nic']} nvme {p['nvme']} idle {p['cards'].get(0)} | a3 nic {q['nic']} nvme {q['nvme']}")


if __name__ == "__main__":
    main()
