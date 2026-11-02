# E125 (Q134): the one registered item list, sourced by setup_e125.sh, session_e125.sh and queue_e125.sh.
# E113's 23 items unchanged, plus lq_h2 and lq_h4 (the B side's low rungs at k = 2 and 4, run in the same passes, for N1).
# anchor_pi runs first and last in every pass (hl/run_hl.py), so a pass is 26 runs after two unrecorded burn-in runs.
E125_ITEMS=anchor_pi,aq_h0,alq_h1,alq_h2,alq_h3,alq_h4,alq_h6,alq_h8,alq_h12,alq_h16,alq_h23,als_h2,als_h3,als_h4,als_h6,als_h8,als_h12,als_h16,lq_h0,lq_h2,lq_h4,lq_h8,ls_h8,nrd_a,nrd_b
E125_SMOKE_ITEMS=anchor_pi,als_h8,alq_h8
E125_PASSES="12501 12502 12503 12504 12505 12506 12507 12508"
E125_SMOKE_PASS=12500
