# E160 (Q139): blind pool 6 under aifoundry2's own governor, in bursts, every launch's C checked

The registration is [`E160.md`](E160.md): M8's clock-and-voltage term, the burst clock it predicts, the board power at that clock, the die's rise and
the highest board sample (M8's new peak rule), scored blind on Q139(b)'s pool 6 ([`../kinds/blind6/`](../kinds/blind6/README.md)) against Q139(x)'s
frozen predictions (`d98d2e34`), on aifoundry2 card 0 under its own governor (65 W / 65 °C read, never set), in E143's 6 s bursts, three passes, with
Q139(k)'s check of C ([`../ccheck/`](../ccheck/README.md)) on every launch. The two tiles whose M8 95% upper peak exceeds 82 W are dropped (section 22
of the brief). It answers rank 2 of Q138's final critic and item 6 of the kinds page's section 11
([§ 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)), with rank 14's check of C and rank 5's aifoundry2
scale beside it. The data and the results will be in `docs/reports/data/2026-11-03-e160-blind6-aifoundry2/`.

Every device command the run sends is a READ ([`E160.md` § Device commands sent](E160.md#device-commands-sent); the audit,
[`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt): GO).
