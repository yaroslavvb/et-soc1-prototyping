import json, sys, os
os.chdir(sys.argv[1])
pct = lambda x, y: 100 * (x / y - 1)
for f in sys.argv[2:]:
    e = json.load(open(f + "/energy.json")); t = json.load(open(f + "/stub_truth.json"))
    b = e["board"]; c = b["catalogue"]; w = t["board_dyn_j_per_solve"]
    r = e["rails"]; tr = t["rails_dyn_j_per_solve"]
    print(f"{f:12s} reps {e['solves']:2d} head {pct(b['j_per_solve'], w):+5.2f} total {pct(b['j_per_solve_total'], t['board_total_j_per_solve']):+5.2f} "
          f"cat {pct(c['j_per_solve'], w):+5.2f} ({c['busy_readings_at_idle']}/{c['busy_readings']}, exp {c['busy_readings_at_idle_expected']:.1f}) "
          f"integ {pct(c['j_per_solve_integral'], w):+5.2f} ramp {pct(b['j_per_solve_sp_avg_ramp'], w):+5.2f} rails "
          + " ".join(f"{pct(r[k]['j_per_solve'], tr[k]):+5.2f}" for k in ("minion_w", "sram_w", "noc_w"))
          + f" unm {pct(r['unmetered']['j_per_solve'], t['unmetered_dyn_j_per_solve']):+6.2f} edges "
          f"{(e['window']['lo_ms'] / 1e3 - t['burst'][0]) * 1e3:+.1f}/{(e['window']['hi_ms'] / 1e3 - t['burst'][1]) * 1e3:+.1f} ms "
          f"pass {e['meter']['board_refresh_s']:.3f} ok {e['ok']}")
