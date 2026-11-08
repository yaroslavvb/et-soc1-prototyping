#!/usr/bin/env python3
# E186 kit note 1 (Q158, fix-e186): the history check v2 (verify-e186's fault 4). It is rb/check_history_e186.py, loaded by its path and
# run UNCHANGED (its tree, m1 and paths modes, its anchor, its rules, its exit codes), with its perimeter widened by the lists of the
# session scale's route, which score_e178.session_scale reads through pool 8's predictor (predict_pool8_a2.check_lists, predict_pool8's
# check_inputs and frozen(), and pool8_pred's freeze list): a committed change to M10's m10.json, m10-s7.json, predict_m10*.py or
# fit_m10.py, to pool 8's registered inputs, to the predictor, or to pool 8's frozen predictions, made together with its list line, passed
# step 2 and v1's history check and was found only at scoring, after card time (the verifier's case on m10.json). v2 adds to v1's LISTS:
#   tools/claims-v3/m10/POOL8-SHA256SUMS                                     (209; pool 8's registered inputs, read by check_inputs)
#   docs/reports/data/2026-11-05-q142p-pool8-predictor/SHA256SUMS            (16; the predictor's own list, read by check_lists)
#   docs/reports/data/2026-11-05-q142p-pool8-predictor/SHA256SUMS-a2         (9; its A2 list, read by check_lists)
#   docs/reports/data/2026-11-04-q142m-m10/SHA256SUMS                        (68, beside; M10's list, read by check_inputs)
#   docs/reports/data/2026-11-04-q142m-m10/SHA256SUMS-a2                     (10, beside; M10's A2 list, read by check_inputs)
#   docs/reports/data/2026-11-05-q142x-pool8-freeze/SHA256SUMS               (160; pool 8's freeze, read by score_e178.pool8_pred)
# and kit note 1's two lists (SHA256SUMS-e186-a1, SHA256SUMS-e186-note1; their files are under tools/claims-v3/e186/, already in v1's
# perimeter). So each list and every file it names joins E186's paths: no change but an addition since E186's registration (a41408d9),
# no added file there that shadows a module, nothing uncommitted. Step 2 v2 (rb/s03_desk_e186_v2.sh) also holds the six lists at their
# counts and their own bytes; step 11 v2 (rb/s22_collect_e186_v2.sh) runs this file's tree mode before any scoring.
#
#   /usr/bin/python3 -I -B tools/claims-v3/e186/rb/check_history_e186_v2.py tree [--anchor REV]
#   /usr/bin/python3 -I -B tools/claims-v3/e186/rb/check_history_e186_v2.py paths [--anchor REV]
#   /usr/bin/python3 -I -B tools/claims-v3/e186/rb/check_history_e186_v2.py m1 --data DIR [--anchor REV]    (v1's m1 mode, unchanged)
#
# Run from the lab's top. It prints one line first, "HISTORY-V2: ..." (the lists added, each with its entry count), then v1's own lines
# (HISTORY OK or HISTORY REFUSED; M1-READ or its others). Exit codes are v1's. Python's own modules only; v1 is loaded by its path, never
# from sys.path, so -I keeps its meaning.
# SPDX-License-Identifier: Apache-2.0
import importlib.util
import os
import sys

V1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "check_history_e186.py")
SCALE_ROUTE_LISTS = [
    ("tools/claims-v3/m10/POOL8-SHA256SUMS", "top"),
    ("docs/reports/data/2026-11-05-q142p-pool8-predictor/SHA256SUMS", "top"),
    ("docs/reports/data/2026-11-05-q142p-pool8-predictor/SHA256SUMS-a2", "top"),
    ("docs/reports/data/2026-11-04-q142m-m10/SHA256SUMS", "beside"),
    ("docs/reports/data/2026-11-04-q142m-m10/SHA256SUMS-a2", "beside"),
    ("docs/reports/data/2026-11-05-q142x-pool8-freeze/SHA256SUMS", "top"),
]
NOTE1_LISTS = [
    ("tools/claims-v3/e186/SHA256SUMS-e186-a1", "top"),
    ("tools/claims-v3/e186/SHA256SUMS-e186-note1", "top"),
]


def load_v1():
    spec = importlib.util.spec_from_file_location("check_history_e186", V1)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    h = load_v1()
    have = {rel for rel, _ in h.LISTS}
    h.LISTS = list(h.LISTS) + [x for x in SCALE_ROUTE_LISTS + NOTE1_LISTS if x[0] not in have]
    counts = []
    for rel, base in SCALE_ROUTE_LISTS + NOTE1_LISTS:
        ent = h.read_list(rel, base) if os.path.isfile(rel) else None
        counts.append(f"{rel} {len(ent) if ent is not None else 'UNREADABLE'}")
    if len(sys.argv) > 1 and sys.argv[1] == "tree":
        print(f"HISTORY-V2: v1's perimeter with the scale route's {len(SCALE_ROUTE_LISTS)} lists and kit note 1's {len(NOTE1_LISTS)} added: "
              + ", ".join(counts))
    return h.main()


if __name__ == "__main__":
    sys.exit(main())
