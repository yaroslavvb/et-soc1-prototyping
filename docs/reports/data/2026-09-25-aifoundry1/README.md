# aifoundry1: what is broken (25 September 2026)

The evidence behind [`../../2026-09-25-aifoundry1-troubleshooting.html`](../../2026-09-25-aifoundry1-troubleshooting.html)
(published at <https://spacesheep.dev/@yaroslavvb/aifoundry1-troubleshooting>, with the fix log at <https://spacesheep.dev/@yaroslavvb/aifoundry1-fix>), written for Roman
Shaposhnik's question "Can someone try to see exactly what is broken on 1?".

- `facts.md`: the read-only facts gathered on aifoundry1, 2 and 3 (sysfs, modinfo, lspci, dpkg, file hashes,
  /proc/interrupts, the logs of our 22 September attempts), with the side-by-side table and the source locations.
- `collect.sh`: the read-only collection script (no device is opened; no root).
- `answer-for-roman.txt`: the short answer.

How it was found: a workflow of AI agents (one fact-gatherer, three analysts with different lenses, a skeptic for each,
a writer and a checker); every statement in the report was re-checked against fresh read-only output. No card was
opened: another user was logged in on aifoundry1, and our own experiment queues held the cards on aifoundry2 and 3.
Raw per-host outputs were not committed (they list other users' processes).
