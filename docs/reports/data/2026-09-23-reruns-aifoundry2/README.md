# The first rerun attempt, aifoundry2, 23 September 2026 (12:51–13:10) — superseded

Relay and hot-line passes on a die at 65 °C, the governor's threshold: the minion clock went to 700–800 MHz
inside 5–25% of the samples of most bursts (see `mhz.minion` in the telemetry) and `analyze_reruns.py` drops
those bursts. Passes 1 (hot line) and 3 (relay) also have no telemetry because the sampler failed to start,
the race that `start_sampler` in the runners now retries around. Use `../2026-09-23-reruns-aifoundry2-warm/`.
