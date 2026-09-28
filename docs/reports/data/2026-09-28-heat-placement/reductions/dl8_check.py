#!/usr/bin/env python3
"""D-L8 (DESIGN2 §5.3) on R2's one L8 block at S_L8 = 64 (owner-side decision, 27 Sep): the P1-style check that
decides the rest of R2. Reads the block with reduce.py's own loader (params and edges from its plan.json/runs).

    python3 dl8_check.py <card data dir, e.g. dev/aifoundry3> [pass, default 2301]

Rule (reduce.py p1's D-L8 at the top of the range, applied to the whole L8 block as the scouting block at 64):
  - any kept measured run censored at C_L (150 s) at S_L8 = 64 -> DROP L8 and G8 (params-r2 'types' [S, L16];
    R2 continues with 2204-2206, three more L16 blocks; MEM, EDGE, PLACE8-t, LIN, GRAD reported, not tested);
  - none censored -> KEEP L8 and G8 at 64 (R2 continues with 2302-2303, 2401-2403); CEN8's median is reported.
The block must be ok, ran at edge 64, and have no void block; otherwise: NO DECISION (exit 2)."""
import os, sys, json
HP = os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5, "tools", "claims-v3", "hp")   # the repository's copy (was the heat worktree's absolute path)
sys.path.insert(0, HP)
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(HP))))
import reduce as R  # noqa: E402

data = sys.argv[1]
pss = int(sys.argv[2]) if len(sys.argv) > 2 else 2301
blk = next((b for b in R.load_blocks(data, "aifoundry3") if b["pass"] == pss), None)
if blk is None:
    print("p%d: no finished ok block under %s: NO DECISION" % (pss, data)); sys.exit(2)
R.require_records([blk], "D-L8 check")
edge = blk.get("edge") if "edge" in blk else R.params_edge(blk)
print("p%d: round %s, type %s, recorded edge S_L8 = %s, block void %s" % (pss, blk["round"], blk["type"], edge, blk["void"] or "none"))
if blk["type"] != "L8" or edge != 64 or blk["void"]:
    print("NO DECISION: not an L8 block at 64, or the block is void"); sys.exit(2)
kept = R.kept_runs(blk)
rows = []
for slot, x in sorted(kept.items()):
    o = x["obs"]
    rows.append((x["rec"]["name"], o["t66_s"], o["censored"], o.get("sw_W"), o.get("tau_c_s")))
    print("  %-9s t66 %-8s censored %-5s sw_W %-6s tau_c %s" % rows[-1])
voided = [x["rec"]["name"] for x in blk["runs"] if x["rec"].get("role") == "meas" and x["obs"]["void"]]
if voided:
    print("  void attempts (re-run once at the block's end): %s" % voided)
missing = sorted(set(R.H.BLOCK_SETS["L8"]) - {r[0] for r in rows})
cen8 = [r[1] for r in rows if r[0] == "CEN8" and r[1] is not None and not r[2]]
censored = [r[0] for r in rows if r[2]]
print("  CEN8 median t66 (uncensored): %s; censored runs: %s; missing placements: %s" % (
    R.median(cen8) if cen8 else None, censored or "none", missing or "none"))
if censored:
    print("D-L8: censored at S_L8 = 64 -> DROP L8 and G8. params-r2 types -> [\"S\", \"L16\"]; R2 continues with "
          "hp 2204, 2205, 2206 (three more L16 blocks, DESIGN2 §5.2); params-r3 types [\"S\", \"L16\"].")
    print(json.dumps({"decision": "drop", "types": ["S", "L16"], "next": [2204, 2205, 2206]}))
elif missing:
    print("NO DECISION: placements missing from the block (void twice): %s" % missing); sys.exit(2)
else:
    print("D-L8: no censored run at S_L8 = 64 -> KEEP L8 and G8 at 64; R2 continues with hp 2302, 2303, 2401, 2402, 2403.")
    print(json.dumps({"decision": "keep", "types": ["S", "L16", "L8", "G8"], "next": [2302, 2303, 2401, 2402, 2403]}))
