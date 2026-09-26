"""The cards of the version-3 campaign: the default card list of every reduce.py's all_cards outcome.

Amendment A2 added aifoundry1's two cards to the registered pair (aifoundry2, aifoundry3); amendment A4 excluded
aifoundry1's card 0 for safety before any campaign data from it (it overheats under load). An expected card with no
data makes all_cards INSUFFICIENT; --cards (or --expect) on each reducer overrides this list.
(docs/reports/data/2026-09-25-claims-v3/AMENDMENTS.md)
"""
CAMPAIGN = ("aifoundry2", "aifoundry3", "aifoundry1-c1")
EXCLUDED = {"aifoundry1-c0": "amendment A4: overheats under load; its smoke data are kept as a record of the fault"}
