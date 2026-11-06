# M11's HC1-B and I8P-B (read_hc1b_i8pb_v2.py)

Reader `5605aa5b6ce4` (v2, tools/claims-v3/m11/README-h2-reader.md.dated-note-1.md); M11's lists {'SHA256SUMS': 58, 'SHA256SUMS-m11': 6, 'SHA256SUMS-a1': 9}; seeds {'M11-HC1-B': 80519, 'M11-I8P-B': 80540}; 20000 draws.

| reading | label | verdict | d | 95% interval | n | scale |
|---|---|---|---:|---|---:|---:|
| HC1-B | blind | BETTER | -0.0158 | [-0.0279, -0.0019] | 31 | 1.02066 |
| I8P-B | blind | NOT RESOLVED | +0.0167 | [-0.0224, +0.0468] | 12 | 0.98752 |

HC1's not-wanted clauses on E172: {'HC1-B reads WORSE': False, "h1 over-corrects on E172's N1": False, 'met': False}

I8P's not-wanted clause on E172: {'I8P-B reads WORSE': False}

Precedence: HC1-B the registration precedes every first launch record; I8P-B the registration precedes every first launch record.

Files read: E171 committed at 91f8ae40; E172 committed at b3255af1.
