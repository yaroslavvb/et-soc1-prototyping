# E143 (Q138): blind pool 5 under aifoundry2's own governor, in bursts

The registration is [`E143.md`](E143.md): M7's clock-and-voltage term, the burst clock it predicts, the board power at that clock and the
die's rise, scored blind on Q138(b)'s 36 tiles ([`../kinds/blind5/`](../kinds/blind5/README.md)) against Q138(x)'s frozen predictions
(`dac39d97`), on aifoundry2 card 0 under its own governor (65 W / 65 °C read, never set), in E80's 6 s bursts, three passes. It answers
item 6 of the kinds page's section 11 ([§ 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)).
The data and the results are in [`docs/reports/data/2026-11-02-e143-blind5-aifoundry2/`](../../../docs/reports/data/2026-11-02-e143-blind5-aifoundry2/README.md).

Every device command the run sends is a READ ([`E143.md` § Device commands sent](E143.md#device-commands-sent); the audit,
[`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt): GO).
