# E113 (Q133): the one registered item list, sourced by setup_e113.sh, session_e113.sh and queue_e113.sh.
# anchor_pi runs first and last in every pass (hl/run_hl.py), so a pass is 24 runs after two unrecorded burn-in runs.
E113_ITEMS=anchor_pi,aq_h0,alq_h1,alq_h2,alq_h3,alq_h4,alq_h6,alq_h8,alq_h12,alq_h16,alq_h23,als_h2,als_h3,als_h4,als_h6,als_h8,als_h12,als_h16,lq_h0,lq_h8,ls_h8,nrd_a,nrd_b
E113_SMOKE_ITEMS=anchor_pi,als_h8,alq_h8
E113_PASSES="1131 1132 1133 1134 1135 1136 1137"
