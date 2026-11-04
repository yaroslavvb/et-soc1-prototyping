# E161 (Q139): heat over minutes from the bits under aifoundry2's own governor, Q139(e)'s frozen holds

The registration is [`E161.md`](E161.md): Q139(e)'s two frozen governed holds on aifoundry2 card 0 (G1Q, `int8.b_line_zero_ff`, predicted
to stay at 800 MHz; G2Q, `fp32.real_smol_softmax_v_causal`, predicted to trip and settle at 681.6 MHz), each die trajectory, plateau and
sustained clock predicted from the tile's bits alone (M8's power through Q138(t)'s frozen chain and the governor's trip rule and cap), with
Q138(t)'s chain on the measured board trace as the registered comparison arm. E144b's harness, with E160's pool-6 tile check and Q139(k)'s
C log on every launch. It answers items 9, 8 and 6 of the kinds page's section 11
([§ 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)) and Q138's final critic, rank 4 (its aifoundry2
half; E154 is the aifoundry3 half). The data and the results go in
[`docs/reports/data/2026-11-03-e161-heat-e2e-aifoundry2/`](../../../docs/reports/data/2026-11-03-e161-heat-e2e-aifoundry2/README.md).

Every device command the run sends is a READ ([`E161.md` § Device commands sent](E161.md#device-commands-sent); the audit,
[`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt): GO).
