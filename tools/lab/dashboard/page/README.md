# The lab dashboard's page

The page half of the lab dashboard (`../DESIGN.md` §4): a render step that turns one `data.json` (§1) into a single
self-contained `index.html` in the report set's look. Nothing here reads a machine or a card, and nothing here holds
collected data. The committed fixture uses only made-up logins (`owner`, `user-a` to `user-e`).

| File | Role |
|---|---|
| `render.py` | `render.py <data.json> <out.html> [--fixture] [--now-ms MS]`: the shared template and chart toolkit (`docs/reports/sources/report.template.html`, `chartkit.js`, unchanged) around the three files below, with the data baked in |
| `body.html`, `script.js`, `meta.json` | the page source: its styles and skeleton, the code that fills it from `D`, and its title |
| `make_fixture.py` | writes `fixture.json`: a complete data file for a made-up afternoon: one machine DOWN (Tailscale offline) with no card-use logger, a full pool, a failed unit, a planned reboot; card use over 24 hours with several people on one card, about a hundred short runs, two open holds, a not-logged gap and a log that began yesterday, and the excluded card used once for 6 s |
| `fixture.json` | its output, for page work and `check_page.sh` |

## What render.py guarantees

- One file: no external script, style, font or image, and the page never calls `fetch()`.
- The data goes in as a JSON literal with every `<`, `>` and `&` written as a `\u` escape, so no string in it can
  end the script element; placeholders are substituted in one pass. The page script writes every data string as text,
  never as HTML, and escapes it inside tooltips.
- A last privacy check refuses (exit 3) a data file containing an e-mail address, an IPv4 address, a URL, a
  `*.ts.net` name or a Tailscale login address, printing only the JSON path. Template unit names such as
  `foo@1000.service` are not addresses. The collector's own check (§6) is the real one.
- `--fixture` moves every time in the data by one offset so that it is 4 minutes old at build time; `--now-ms` fixes
  "now" (tests of the stale state).
- The page carries a build stamp (`D._build`: render time, a hash of the page sources), shown under "This version".

## What the page reads

The schema of `../DESIGN.md` §1, read defensively: every field may be missing or `null` and shows as "—". Times are
taken from a `*_ms` twin when present (`generated_at` → `generated_ms`, `last_run` → `last_run_ms`, or `<key>_ms`),
else parsed from the ISO string. A few optional fields beyond §1 are used when present:

- `history.hosts.<h>.up`: `1` answered, `0` no answer, `"approval"` (or `2`) a pending Tailscale approval, `null`
  no run;
- `people[].hosts.<h>.status` and `.doing`: the person's status and categories on that machine;
- `usage` (§1.8): the "Card use, last 24 hours" section, the card tiles' lanes and the people's card use; without it the
  section says so and the 48-hour card rows are drawn for every card;
- `hosts.<h>.state`, `down_since_ms`, `last_answer_ms`, `tailscale_last_seen_ms`, `rebooted_at_ms`: the machine's own
  state (DOWN, UNREACHABLE, APPROVAL NEEDED) and its times; without `state`, `reachable` decides;
- `hosts.<h>.next_try_ms` (the next try after an approval failure), `people[].hosts.<h>.stale` (a count from old
  data), `collector.fixture` (shows the MADE-UP DATA pill).

Host and card lists come from the data; a card's colour and mark come from the toolkit's registry (`CK.card`).
A card whose holder is unknown, or whose machine did not answer, shows NO DATA rather than FREE.

## Behaviour on the page

- The light is the collector's `status.level` (HEALTHY, WARNINGS, NEEDS ATTENTION), or "STALE · was <level>" with a
  banner when the data is older than `collector.stale_after_min` (80); then every card reads NO DATA ("was free at
  HH:MM"), never FREE, and "next check" says the collector may be stopped. Ages tick every 30 s; the light (a live
  region) is rewritten only when its word changes, and a tab that crosses into STALE re-renders its cards.
- Card use is drawn in the lab's zone (`usage.tz`, America/Los_Angeles) with hour ticks; each login has one colour on
  the whole page (the six series tokens for the six logins with the most card time, in alphabetical order among them;
  the rest are "others"), and its name always travels with it (legend, bar labels, tooltips, tables). Bars are at
  least 2 px wide; spans outside the log's coverage are hatched with their reason.
- A machine that is not up: its panel, tiles and people are greyed and labelled "last known at HH:MM"; its cards read
  UNKNOWN, its people counts unknown. The 48-hour timeline tells down (Tailscale offline), no answer (ssh) and
  approval waits apart, and "alive (nodewatch only)" for slots the collector did not check but nodewatch's heartbeat
  covered; it draws card rows only for cards with no usage log.
- `#focus=<host>` opens a machine's panel and `#card=<card>` (or `#focus=<card>`) a card's tile with its details;
  clicks set the hash and send it to the viewer (`ss-hash`), so a selection survives the automatic refresh.
- The theme control (auto, light, dark) sets `data-theme` and remembers the choice in `localStorage`; `?theme=` also
  works. With no choice it sets nothing.
- Reload fallback (§4.4): only on `https://*.spacesheep.app`, never under `file://`; after the tab was hidden over
  2 minutes, after the machine slept, or when the data is stale; at most once in 5 minutes, and once in 30 when a
  reload brought back the same data. It loads `location.origin + '/' + location.hash`. No timer fires in the first
  6 seconds.

## Checking it

```bash
P=tools/lab/dashboard/page; T=docs/reports/data/2026-09-24-report-review/tools
python3 $P/make_fixture.py && python3 $P/render.py $P/fixture.json /tmp/lab.html --fixture
bash $T/check_page.sh /tmp/lab.html; DARK=1 bash $T/check_page.sh /tmp/lab.html; DARK=os bash $T/check_page.sh /tmp/lab.html
bash $T/shot.sh /tmp/lab.html /tmp/lab 1280; bash $T/shot.sh /tmp/lab.html /tmp/lab-phone 390
```

On 30 September 2026 the fixture page, and variants with a stale file, two card problems, a data file with only
`generated_at`, and one with every block `null`, passed `check_page.sh` at 1280 and 390 px in light, `DARK=1` and
`DARK=os` (no errors, empty fields or sideways overflow). The same day, after the card-use and machine-state changes,
the new fixture, pages from `collect.py --from-raw testdata` (and after `testdata/run2`) and a real collection passed
at 1280 and 390 px, light and `DARK=1`.
