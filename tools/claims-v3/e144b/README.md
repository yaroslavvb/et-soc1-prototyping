# E144b (Q138): heat over minutes on aifoundry2, Q138(t)'s frozen governed holds

The registration is [`E144b.md`](E144b.md): Q138(t)'s two frozen holds on aifoundry2 card 0 under its own governor (G1, int8 −1s at
800 MHz; G2, fp32 random, governed), scored blind by Q138(t)'s own scorer against its frozen chain, plateau rules and trip rule, as committed
at amendment A1 (`c2f9920d`), with E133's harness. It answers items 9 and 8 of the kinds page's section 11
([§ 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)). E144's aifoundry3 arm is a separate lane.
The data and the results are in [`docs/reports/data/2026-11-02-e144-heat-minutes-aifoundry2/`](../../../docs/reports/data/2026-11-02-e144-heat-minutes-aifoundry2/README.md).

Every device command the run sends is a READ ([`E144b.md` § Device commands sent](E144b.md#device-commands-sent); the audit,
[`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt): GO).
