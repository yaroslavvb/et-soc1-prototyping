#!/usr/bin/env python3
"""E164 (Q141(b)): write harness-e164.json, the sha256 of every file E164's box session runs or reads - E78's card code (unchanged, and
checked equal to E157's registered pins), E164's card files, blind pool 7's and the eleven pool-6 tiles with their manifests, and the
four binaries on aifoundry1 (E157's pins: the binaries E142, E155, E156 and E157 ran on this card, read on the box on Tue 3 Nov 2026;
the box step re-reads them before any device opens). check_e164.py, run_e164.py, reduce_e164.py and smoke_gate_e164.py read it.
Standard library only. Run it after the kit's last edit and before its commit.

    python3 -B tools/claims-v3/e164/make_harness_e164.py
SPDX-License-Identifier: Apache-2.0
"""
import glob
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P7 = "tools/claims-v3/kinds/blind7"
P6 = "tools/claims-v3/kinds/blind6"
CARD_CODE = ["tools/claims-v3/lib.sh", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/run_e78.py",
             "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/kinds.json", "tools/claims-v3/e128/ettelem_guard.sh",
             "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json", "workloads/sparsity/host/main.cpp",
             "tools/claims-v3/ccheck/sparsity_ccheck.sh", "tools/claims-v3/ccheck/patch_host_ccheck.py",
             "tools/claims-v3/ccheck/build_host_ccheck.sh", "tools/claims-v3/ccheck/ccheck.py", "tools/claims-v3/ccheck/pick6.py",
             "rtl-sim/fma_toggle_v2/accum.c"]
E164_FILES = ["e164_common.py", "run_e164.py", "block_e164.sh", "queue_e164.sh", "session_e164.sh", "check_e164.py",
              "preflight_e164.sh", "smoke_gate_e164.py", "reduce_e164.py", "predictions-e164.json"]
P6_TILES = ("fp32/fp32.real_qwen_softmax_v.bin", "fp32/fp32.real_smol_softmax_v_causal.bin", "fp16/fp16.real_qwen_qk.bin",
            "fp16/fp16.e5m2grid_wide.bin", "int8/int8.powerlaw_df4_pc.bin", "int8/int8.bheld_bit1.bin", "int8/int8.bheld_bit4.bin",
            "int8/int8.real_qwen_w8a8_gate.bin", "fp32/fp32.anchor6_randn.bin", "fp16/fp16.anchor6_randn.bin", "int8/int8.anchor6_full.bin")
E157_REG = "tools/claims-v3/e157/predictions-e157.json"     # lab 01676499: its harness pins the binaries and E78's card code


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def main():
    e157 = json.load(open(os.path.join(ROOT, E157_REG)))["harness"]
    card = {rel: sha(rel) for rel in CARD_CODE}
    diff = [rel for rel in CARD_CODE if e157["card_code_unchanged_sha256"].get(rel) != card[rel]]
    if diff:
        raise SystemExit(f"E78's card code differs from E157's registered pins: {diff} - review before porting")
    pool = {f"{P7}/{f}": sha(f"{P7}/{f}") for f in ("blind7.json", "MANIFEST", "SHA256SUMS", "predictions-blind7-aifoundry1c1.json")}
    pool.update({os.path.relpath(p, ROOT): hashlib.sha256(open(p, "rb").read()).hexdigest()
                 for p in sorted(glob.glob(os.path.join(ROOT, P7, "tiles", "*", "*.bin")))})
    pool.update({f"{P6}/{f}": sha(f"{P6}/{f}") for f in ("blind6.json", "SHA256SUMS")})
    pool.update({f"{P6}/tiles/{t}": sha(f"{P6}/tiles/{t}") for t in P6_TILES})
    assert sum(1 for k in pool if k.endswith(".bin")) == 72
    for t in P6_TILES:      # the pool-6 tiles equal E157's registered bytes
        assert e157["pool_sha256"][f"{P6}/tiles/{t}"] == pool[f"{P6}/tiles/{t}"], t
    out = {"_note": "E164 (Q141(b)): the sha256 of every file E164's box session runs or reads (make_harness_e164.py); check_e164.py "
                    "refuses on any difference, and the binaries are re-read on the box before any device opens",
           "card_code_unchanged_sha256": card,
           "card_code_equal_to_E157_pins": True,
           "e164_card_files_sha256": {f"tools/claims-v3/e164/{f}": sha(f"tools/claims-v3/e164/{f}") for f in E164_FILES},
           "pool_sha256": pool,
           "box_binaries_sha256": dict(e157["box_binaries_sha256"]),
           "patched_main_cpp_sha256": e157["patched_main_cpp_sha256"],
           "binaries_note": "E157's pins (predictions-e157.json > harness, lab 01676499): build/sparsity/host/sparsity_host, "
                            "build/ettelem/ettelem, build/sparsity/kernel/sparsity.elf and Q139(k)'s patched C-logging host "
                            "build/ccheck/b/host/sparsity_host (built on aifoundry1 by build_host_ccheck.sh on Tue 3 Nov 2026 at 06:37 PST "
                            "from main.cpp 0f53a7d5..., its patched source 5bd029ca...); E164 syncs no compiled source, so nothing is "
                            "rebuilt; a missing or different binary stops the session, and a rebuild needs a dated amendment re-pinning "
                            "it before the claim"}
    json.dump(out, open(os.path.join(HERE, "harness-e164.json"), "w"), indent=1)
    print(f"wrote harness-e164.json: {len(card)} card-code files (equal to E157's pins), {len(out['e164_card_files_sha256'])} E164 card "
          f"files, {len(pool)} pool files (72 tiles), {len(out['box_binaries_sha256'])} binaries")


if __name__ == "__main__":
    main()
