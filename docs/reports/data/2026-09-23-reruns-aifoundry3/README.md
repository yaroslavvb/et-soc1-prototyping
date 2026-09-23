# Reruns for the confidence bars, aifoundry3, 23 September 2026 (12:51–13:45)

Five passes of the relay (`relay-pass*`) and the hot line (`hotline-pass*`) — passes 1 and 2 respectively
have no telemetry (the sampler start race) and pass 3 of the hot line was cut short when the driver script was
overwritten while running; the analysis keeps only complete passes with telemetry — plus three passes of the
rings and levels sampled by ettelem (`rl-pass*`, run_rings_levels_power.sh). `rings-pass*` and `levels-pass*`
are the older run_energy.py measurements, kept and not pooled. aifoundry3's firmware pins 600 MHz, so no
preheat was needed. Pooled with aifoundry2's warm passes by `tools/ettelem/analyze_reruns.py`.
