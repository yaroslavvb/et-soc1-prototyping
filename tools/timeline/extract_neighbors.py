#!/usr/bin/env python3
"""Extract the neighbor sessions: other Claude Code sessions on the lab's machine whose work the page shows in a lane of
its own (on 30 September, the session that ran the link test that hung aifoundry1, then investigated it).

    TIMELINE_NEIGHBORS=97db24ee-042f-547a-86c0-e1444e260a06 tools/timeline/extract_neighbors.py

For each session id in $TIMELINE_NEIGHBORS (paths.py; none for no lane) it streams the session's transcript and its
subagents' (the same project folder as the main session) and writes $TIMELINE_DIR/neighbors.json:

  sessions[]  per neighbor: its busy intervals (its main agent's events under 3 min apart, joined across a tool call
              that took longer, as extract_agents.py counts them), its subagents' busy intervals (their union) and
              agent-hours, its tokens (usage per message id, counted once), the owner's messages to it (time, kind,
              length, a hand-written summary from NEIGHBOR_SUMMARIES and its words as prompt_privacy.redact() lets
              the page show them), its key events (EVENTS,
              written from its transcript, the hosts' boot records and docs/findings/14-card-behaviour.md, plus each
              deploy of a public page and each commit it made, found in its transcripts), and how many other deploys
  hosts[]     the hosts down (HOSTS): aifoundry1 hung by the link retrain, then the power cycle of all three machines

and $TIMELINE_DIR/work/neighbor_deploys.json: every deploy the neighbors made (time and space, private ones too), which
build_artifacts.py reads so that their versions in a page's history are not counted as this session's deploys. That file
names private spaces, so it stays in the working folder and is never copied to the data folder.

Privacy (the page is public, AGENT.md section 10): since 5 Oct 2026 the owner's messages carry their words, as
prompt_privacy.redact() lets the page show them (access details, addresses, other people's names and private links
removed, each marked); the extract carries no workflow or agent names of the neighbors (the first one's workflows served
the report for the lab lead and host fixes), no private page's name, slug or space, and no word about who holds which
privilege: the link test is "the owner's session ran the link test".

Since 5 Oct 2026 the neighbors are every other session on the machine in the page's span, on either of the owner's
Claude accounts (paths.PROJECTS), each in a lane named in NEIGHBOR_INFO; an id list joined with '+' is one lane for
several short sessions. A session whose transcript was rewritten shorter keeps the committed extract's earlier rows
(merge_prev). sanitize_extracts.py
and build_timeline_data.py scan it with the others. $TIMELINE_CUTOFF ends the transcripts there.
"""
import collections, glob, json, os, re, subprocess, sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402
import extract_agents as X  # noqa: E402  (its scan(), busy_intervals() and merge_waits(); it needs the privacy table)
import prompt_privacy as PP  # noqa: E402  (the owner's messages as the public page may show them)

CUT = datetime.fromisoformat(paths.CUTOFF.replace('Z', '+00:00')) if paths.CUTOFF else None
PDT = timezone(timedelta(hours=-7))
T = lambda s: datetime.fromisoformat(s.replace('Z', '+00:00'))
iso = lambda d: d.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
L = lambda s: datetime.fromisoformat(s).replace(tzinfo=PDT)   # a PDT wall time, as the tables below give it

# The owner's messages to a neighbor: (first 8 characters of the session id, the UTC second it was sent) -> (a summary of
# at most 12 words, third person, never quoting; category). A message missing here is left off the page and printed.
NEIGHBOR_SUMMARIES = {
    ('97db24ee', '2026-09-30T21:04:45'): ("Checks that the new session responds.", 'status'),
    ('97db24ee', '2026-09-30T21:04:49'): ("Picks the session's model.", 'status'),
    ('97db24ee', '2026-09-30T21:11:16'): ("Asks to tidy the lab lead's report and fix the open problems.", 'request'),
    ('97db24ee', '2026-09-30T21:31:46'): ("Asks for commands the owner can run for the host fixes.", 'request'),
    ('97db24ee', '2026-09-30T21:41:21'): ("Reports the fixes ran, aifoundry1's still running; asks to verify them.", 'request'),
    ('97db24ee', '2026-09-30T21:47:16'): ("Reports aifoundry1 seems dead, with the last commands it ran.", 'status'),
    ('97db24ee', '2026-09-30T22:18:15'): None,   # four messages delivered in one second after the restart: by length below
    ('97db24ee', '2026-09-30T22:27:58'): ("Asks to retitle the lab lead's report and hide solved issues.", 'request'),
    ('97db24ee', '2026-09-30T22:29:20'): ("Asks for sortable columns in the report's problem table.", 'request'),
    ('97db24ee', '2026-09-30T22:32:54'): ("Asks to fix what it can and detail steps for the Nekko team.", 'request'),
    ('97db24ee', '2026-09-30T22:55:40'): ("Asks for public lab pages, and one way on the new-user page.", 'request'),
    # 2 October, the lab day (the same session, resumed; its transcript now starts at 10:05 PDT)
    ('97db24ee', '2026-10-02T17:07:11'): ("Asks to show each machine's disk use beside its memory.", 'request'),
    ('97db24ee', '2026-10-02T17:10:51'): ("Asks to sample card temperature live, once a second.", 'request'),
    ('97db24ee', '2026-10-02T17:15:20'): ("Approves the first option, without disturbing anyone using a card.", 'approval/answer'),
    ('97db24ee', '2026-10-02T17:17:34'): ("Suggests updating only every 10 seconds, since it is heavy.", 'correction'),
    ('97db24ee', '2026-10-02T17:18:01'): ("Takes it back: once a second if the read is light.", 'correction'),
    ('97db24ee', '2026-10-02T17:21:52'): ("Asks for a more visual, sci-fi style dashboard.", 'request'),
    ('97db24ee', '2026-10-02T17:25:57'): ("Asks for fixed-size process lists so the cards stop resizing.", 'request'),
    ('97db24ee', '2026-10-02T17:30:27'): ("Plans a reboot of aifoundry2; asks for robust collectors and history graphs.", 'request'),
    ('97db24ee', '2026-10-02T17:38:04'): ("Asks for the status.", 'status'),
    ('97db24ee', '2026-10-02T17:38:55'): ("Make the collectors survive a reboot, then reboot and recover the card.", 'request'),
    ('97db24ee', '2026-10-02T17:51:18'): None,   # two messages in one second: by length below
    ('97db24ee', '2026-10-02T17:55:17'): ("Tells the session to continue.", 'status'),
    ('97db24ee', '2026-10-02T19:13:05'): ("Link the history page from the dashboard and its temperature charts.", 'request'),
    ('97db24ee', '2026-10-02T19:13:53'): ("Explain aifoundry2's accelerating temperature; add suggestions to the lab lead's report.", 'request'),
    ('97db24ee', '2026-10-02T20:05:46'): ("Reports a fixed fan on aifoundry1's card; asks to try it.", 'request'),
    ('97db24ee', '2026-10-02T20:10:55'): ("Asks to check the new-user instructions before three people use them.", 'request'),
    ('97db24ee', '2026-10-02T20:27:47'): ("Card 0 is in service again: update the instructions.", 'request'),
    ('97db24ee', '2026-10-02T21:34:04'): ("Switches the session's model.", 'status'),
    ('97db24ee', '2026-10-02T21:35:39'): ("Make the dashboard the lab's starting point, with report links; trim it.", 'request'),
    ('97db24ee', '2026-10-02T21:42:49'): ("Asks what the dashboard's unseen card use is.", 'question'),
    ('97db24ee', '2026-10-02T21:48:04'): ("Add the interactive chip diagram to the dashboard's quick links.", 'request'),
    ('97db24ee', '2026-10-02T21:48:23'): ("Remove the theme selector from the dashboard.", 'request'),
    ('97db24ee', '2026-10-02T21:55:18'): ("Shares the new users' first steps; checks the instructions fit them.", 'request'),
    ('97db24ee', '2026-10-02T22:22:08'): ("Cut the dashboard's explanatory text; keep it concise.", 'request'),
    ('97db24ee', '2026-10-02T22:22:18'): ("Clarifies that this is for the dashboard.", 'correction'),
    ('97db24ee', '2026-10-02T22:23:46'): ("The reports link should reuse the existing reports page.", 'correction'),
    ('97db24ee', '2026-10-02T22:23:59'): ("The dashboard should stay minimal, without the reports.", 'correction'),
    ('97db24ee', '2026-10-02T22:27:14'): ("Switches the session's model back.", 'status'),
    ('97db24ee', '2026-10-02T22:27:19'): ("Redo the new-user instructions as clear steps, ending with Claude running.", 'request'),
    ('97db24ee', '2026-10-02T22:29:10'): ("Wants instructions that work out of the box, saying where agents run.", 'correction'),
    ('97db24ee', '2026-10-02T22:35:36'): ("aifoundry3's card still shows as held; asks for real-time readings.", 'request'),
    ('97db24ee', '2026-10-02T22:36:05'): ("Asks for a live-link report of the day's work.", 'request'),
    ('97db24ee', '2026-10-02T22:38:36'): ("Report the live link's slowness to the spacesheep team.", 'request'),
    ('97db24ee', '2026-10-02T22:47:03'): ("Stream card use live; track down the unseen card use.", 'request'),
    ('97db24ee', '2026-10-02T22:49:01'): ("History page: the hover box must not cover the graph.", 'request'),
    # 4 October: the audit session (the second account)
    ('93af8ad7', '2026-10-04T18:11:29'): ("Check the lab lead's report: what is fixed; fix the rest.", 'request'),
    ('93af8ad7', '2026-10-04T18:43:38'): ("Tells the session how it may make the machine fixes.", 'approval/answer'),
    ('93af8ad7', '2026-10-04T19:32:39'): ("Approves publishing every edit and making all the fixes.", 'approval/answer'),
    ('93af8ad7', '2026-10-04T20:38:09'): ("Commit and push everything; file the drafted issue publicly.", 'approval/answer'),
    ('93af8ad7', '2026-10-04T20:40:32'): ("Asks for the rest of request U28 too.", 'request'),
    ('93af8ad7', '2026-10-04T22:13:34'): ("Reports card 0 fixed; asks to remove its exclusions.", 'request'),
    ('93af8ad7', '2026-10-04T23:01:13'): ("Copy the two-account Claude setup to aifoundry1 and aifoundry3.", 'request'),
    ('93af8ad7', '2026-10-04T23:18:11'): ("The chips are end-of-life: file the race report publicly.", 'approval/answer'),
    ('93af8ad7', '2026-10-04T23:42:00'): ("Has authorized on aifoundry2; tells it to continue.", 'status'),
    # 4-5 October: the Antigravity session
    ('c42b457d', '2026-10-04T23:02:32'): ("Install the Antigravity CLI here, reachable remotely, later several accounts.", 'request'),
    ('c42b457d', '2026-10-04T23:22:10'): ("Simplifies: one Antigravity account per machine for now.", 'correction'),
    ('c42b457d', '2026-10-04T23:37:55'): ("Signed in, but the machine is missing from the dashboard.", 'status'),
    ('c42b457d', '2026-10-04T23:51:05'): ("Asks how to turn on turbo mode, which the dashboard refuses.", 'question'),
    ('c42b457d', '2026-10-04T23:53:07'): ("Asks for a script that makes the edit, with steps.", 'request'),
    ('c42b457d', '2026-10-05T00:02:40'): ("Asks for the steps for aifoundry1 and aifoundry3, in turbo mode.", 'request'),
    ('c42b457d', '2026-10-05T00:05:46'): ("Still asked for permission on aifoundry2.", 'status'),
    ('c42b457d', '2026-10-05T01:05:52'): ("Working, but aifoundry1's mode is not turbo; asks how.", 'question'),
    ('c42b457d', '2026-10-05T01:07:46'): ("Maybe turbo already: it asked only to publish a page.", 'correction'),
    # 5 October: this session
    ('1f1f61cb', '2026-10-05T03:54:56'): ("Asks why two app settings are missing on the second account.", 'question'),
    ('1f1f61cb', '2026-10-05T04:02:23'): ("Checkpoint the machine's agent setup and lessons to GitHub, with a page.", 'request'),
    ('1f1f61cb', '2026-10-05T17:50:06'): ("Refresh this timeline: two weeks, every session, the prompts on hover.", 'request'),
    # the short sessions, on either account
    ('d1dcf7d2', '2026-09-30T19:22:08'): ("Exits a first test session.", 'status'),
    ('8ca68501', '2026-09-30T19:25:40'): ("Asks which machine this is and the account's e-mail.", 'question'),
    ('8ca68501', '2026-10-04T18:03:22'): ("Tests the connection.", 'status'),
    ('a4bad5b7', '2026-09-30T19:48:36'): ("Asks whether anybody is using the cards right now.", 'question'),
    ('a679cf50', '2026-10-04T23:39:39'): ("Asks to sign in to GitHub on this machine.", 'request'),
    ('afaecf2a', '2026-10-05T04:34:54'): ("Asks why a session has trouble reconnecting.", 'question'),
}
# messages sent in the same second, told apart by their length in characters
NEIGHBOR_SUMMARIES_BY_LEN = {
    ('97db24ee', '2026-09-30T22:18:15', 1418): ("Sends the report that aifoundry1 is down again, after the restart.", 'status'),
    ('97db24ee', '2026-09-30T22:18:15', 169): ("Says the lab lead power-cycled; asks to troubleshoot and record the lesson.", 'request'),
    ('97db24ee', '2026-09-30T22:18:15', 47): ("Corrects which machine was power-cycled.", 'correction'),
    ('97db24ee', '2026-09-30T22:18:15', 183): ("If it stays down, asks for a report of likely causes.", 'request'),
    ('97db24ee', '2026-10-02T17:51:18', 133): ("Recalls an earlier card recovery; asks what was done, since this failed.", 'question'),
    ('97db24ee', '2026-10-02T17:51:18', 11): ("Asks whether the card is back.", 'status'),
}

# What the page calls each neighbor: (its lane's label, its name in sentences, a line about it). A key joined with '+' is
# one lane for several short sessions.
NEIGHBOR_INFO = {
    '97db24ee': ('maintenance', 'the maintenance session',
                 'a second Claude Code session on aifoundry2: the link test of 30 September, then the lab day of 2 October'),
    '93af8ad7': ('audit', 'the audit session',
                 'a session on the owner’s second Claude account, 4 October: the report for the lab lead checked and its '
                 'fixes made, the driver race filed upstream, the two-account setup prepared for the other machines'),
    'c42b457d': ('Antigravity', 'the Antigravity session',
                 'a session on the second account, 4 October: the Antigravity CLI installed with remote control, one '
                 'Google account per machine, and turbo mode found'),
    '1f1f61cb': ('this session', 'this session',
                 'a session on the second account, from 4 October: the machine’s agent setup checkpointed, then this '
                 'page refreshed'),
    'short': ('short ones', 'the short sessions',
              'short sessions on either account: tests, a question about the cards, a GitHub sign-in, a reconnection check'),
}

# Key events of a neighbor, from its transcript and 14-card-behaviour.md (PDT wall times; end None for an instant).
# Kinds: test, hang, power (drawn red), back, probe, page, commit, fix.
EVENTS = {
    '97db24ee': [
        ('2026-09-30T14:41:21', None, 'test', 'The link test on aifoundry1 card 0',
         'The owner’s session ran the link test from the lab report (U25): two readings of card 0’s corrected link errors '
         'at 16 GT/s, a minute apart, then a retrain of the link at 8 GT/s, with the card idle and locked. The plan said a '
         'failed retrain would drop only card 0.'),
        ('2026-09-30T14:41:21', '2026-09-30T15:06:35', 'hang', 'aifoundry1 hung',
         'At the retrain the whole host stopped: no more output, no network. The neighbor’s read-only check found it gone '
         'at 14:42, watched for it from 14:45 and confirmed it dead at 14:48; the owner reported it at 14:47.'),
        ('2026-09-30T15:06:35', '2026-09-30T15:07:35', 'power', 'The power cycle',
         'The lab lead switched all three machines off and on at about 15:07 (boots at 15:07:10–15:07:35). The reboot of '
         'aifoundry2 stopped both sessions there until 15:18 and 15:22 and cleared its /tmp: about 19 GB of working files, '
         'this timeline’s working folder among them.'),
        ('2026-09-30T15:18:15', '2026-09-30T15:21:01', 'probe', 'The investigation',
         'Back at 15:18, the neighbor reads the three hosts’ boot records, card 0’s link counters (16 GT/s x8 again, no '
         'corrected errors where there had been about one a second for twelve days) and the crash store (empty: a hard hang, '
         'not a panic), and what the power cycle cleared.'),
        ('2026-09-30T15:57:25', '2026-09-30T16:03:46', 'fix', 'The dashboard kept public',
         'At the owner’s word that the AI Foundry pages are public, the neighbor changed the lab dashboard’s updater, which '
         'had set the page private again on each run: it now keeps it public. The 16:02 run confirmed it.'),
        # 2 October (PDT): the lab day, from its transcript, the commits and 14-card-behaviour.md
        ('2026-10-02T10:01:00', None, 'fix', 'The live dashboard',
         'Each machine now streams a reading every second to the dashboard: CPU per thread, load, memory, the cards’ links '
         'and locks, and a live view of the busiest programs; from 10:22 each card’s die temperature too.'),
        ('2026-10-02T10:43:00', None, 'fix', 'The lab history page',
         'Each machine keeps a 5-second record of its readings for nine days; a job every 5 minutes gathers them into '
         'hour, day and week graphs.'),
        ('2026-10-02T10:46:45', '2026-10-02T10:53:25', 'reboot', 'aifoundry2 rebooted to bring its card back',
         'Its card had fallen off the bus while idle; a plain reboot at 10:47 left it off, and the full reset at 10:53 '
         'brought it back.'),
        ('2026-10-02T12:02:01', None, 'down', 'aifoundry2’s card out of service',
         'Idle after the reset, the card heated from 45 °C to a 138 °C mean and 134 W and fell off the bus: the air that '
         'cools it is too warm. Nobody uses it until the fan settings are fixed on site.'),
        ('2026-10-02T13:26:00', None, 'card', 'aifoundry1’s card 0 back in service',
         'With its broken fan replaced, card 0 idles at 49 °C (65 °C before) and stays at 52–53 °C under eight minutes of '
         'matrix bursts, cooler than card 1.'),
        ('2026-10-02T15:36:00', None, 'fix', 'The new-user instructions, ninth edition',
         'Three steps, each saying where it runs, for the three new lab users of that afternoon.'),
        ('2026-10-02T15:58:00', None, 'fix', 'Card use in real time',
         'The dashboard’s card-use lane now shows who holds each card, each second; the day’s unseen card opens were the '
         'lab’s own monitor and tests.'),
    ],
    '93af8ad7': [
        ('2026-10-04T12:33:00', None, 'fix', 'The report for the lab lead re-checked',
         'Items that a rebuild on 2 October had dropped are restored, with new problems and requests, among them the '
         'cards’ per-sensor temperatures; four more updates follow that afternoon.'),
        ('2026-10-04T13:39:00', None, 'fix', 'A gentler live monitor',
         'The live monitor no longer makes an elevated read every second, and its card reader waits for a card’s lock; the '
         'dashboard’s “hottest sensor” is now named for what it is, the firmware’s peak since the card started.'),
        ('2026-10-04T13:43:00', None, 'fix', 'A card-open logger on aifoundry1',
         'A lab request done: a small service logs every open of a card, so that unseen card use can be traced.'),
        ('2026-10-04T15:15:00', None, 'card', 'Card 0 counted again',
         'With card 0 fixed, aifoundry1’s card-usage logger stops skipping it.'),
        ('2026-10-04T16:04:00', None, 'setup', 'The two-account setup for the other machines',
         'A checked script gives aifoundry1 and aifoundry3 the same two-account Claude setup as aifoundry2; the owner runs it.'),
        ('2026-10-04T16:42:00', None, 'fix', 'The driver race filed upstream',
         'The race in the card driver’s queue counters, found on 30 September, is filed publicly as issue 136 of '
         'aifoundry-org/et-platform: the chips are end-of-life, so nothing needs holding back.'),
    ],
    'c42b457d': [
        ('2026-10-04T16:25:00', None, 'setup', 'Antigravity on aifoundry2',
         'The Antigravity CLI installed and signed in to one Google account, its remote-control daemon kept up in tmux by a '
         'per-minute watchdog, so that the account’s dashboard reaches the machine.'),
        ('2026-10-04T17:13:00', None, 'setup', 'A setup script for the other machines',
         'One script gives aifoundry1 and aifoundry3 the same Antigravity setup; each machine signs in to its own account.'),
        ('2026-10-04T18:08:00', None, 'fix', 'Turbo mode, from the settings files',
         'The dashboard cannot switch the agents to turbo. The settings are in two files, found from the program’s own '
         'message definitions, and a small tool sets both.'),
    ],
    '1f1f61cb': [
        ('2026-10-04T21:17:00', None, 'setup', 'The agent setup checkpointed',
         'The machine’s agent setup, its scripts, settings and lessons, put in a private repository with a rebuild guide, '
         'so that the machine can be rebuilt if it is wiped.'),
    ],
}
# The hosts down: (host, its cards on the page, start, end, kind, title, text). The boot times are each host's own
# record (uptime -s, last -x), read on 30 Sep at 15:55; the power went off after 15:06:33, the last line either session
# on aifoundry2 wrote before its boot.
HOSTS = [
    ('aifoundry1', ['aifoundry1-c0', 'aifoundry1-c1'], '2026-09-30T14:41:21', '2026-09-30T15:06:35', 'hang', 'aifoundry1 hung',
     'The retrain of card 0’s link at 14:41:21 stopped the whole host, both cards with it, until the power cycle.'),
    ('aifoundry1', ['aifoundry1-c0', 'aifoundry1-c1'], '2026-09-30T15:06:35', '2026-09-30T15:07:35', 'power', 'aifoundry1 power-cycled',
     'The lab lead switched the machine off and on; it booted at 15:07:35, and card 0’s link trained at 16 GT/s again.'),
    ('aifoundry2', ['aifoundry2'], '2026-09-30T15:06:35', '2026-09-30T15:07:11', 'power', 'aifoundry2 power-cycled',
     'Switched off and on with the others; it booted at 15:07:11. The sessions on it stopped until 15:08–15:22, and its '
     '/tmp was cleared.'),
    ('aifoundry3', ['aifoundry3'], '2026-09-30T15:06:35', '2026-09-30T15:07:10', 'power', 'aifoundry3 power-cycled',
     'Switched off and on with the others; it booted at 15:07:10.'),
    # 1-2 October: aifoundry2's card off the bus, its reboots, and aifoundry1 off for card 0's new fan (14-card-behaviour.md;
    # each host's journal: journalctl --list-boots, read on 5 Oct). An end of None is the snapshot.
    ('aifoundry2', ['aifoundry2'], '2026-10-01T09:42:00', '2026-10-02T06:45:42', 'hang', 'aifoundry2’s card off the bus',
     'Idle, the card stopped answering on PCIe at 09:42 on 1 October: its cooling follows the host’s fans, which slow '
     'down when the host idles. It stayed down until a full-reset reboot.'),
    ('aifoundry2', ['aifoundry2'], '2026-10-02T06:45:42', '2026-10-02T06:46:18', 'power', 'aifoundry2: a full-reset reboot',
     'A cold reboot, which power-cycles the card’s slot, brought the card back at 06:46.'),
    ('aifoundry2', ['aifoundry2'], '2026-10-02T07:42:00', '2026-10-02T10:53:25', 'hang', 'aifoundry2’s card off the bus again',
     'Idle, 57 minutes after the reset, the card heated to 126 °C and 103 W and fell off the bus at 07:42; a plain reboot '
     'at 10:47 left it off, the full reset at 10:53 brought it back.'),
    ('aifoundry2', ['aifoundry2'], '2026-10-02T10:46:45', '2026-10-02T10:47:15', 'power', 'aifoundry2: a plain reboot',
     'A plain reboot keeps the card’s slot powered: the card stayed off the bus.'),
    ('aifoundry2', ['aifoundry2'], '2026-10-02T10:52:48', '2026-10-02T10:53:25', 'power', 'aifoundry2: a full-reset reboot',
     'The full reset brought the card back at 16 GT/s x8.'),
    ('aifoundry2', ['aifoundry2'], '2026-10-02T12:02:01', None, 'hang', 'aifoundry2’s card out of service',
     'Idle after the reset, the card heated from 45 °C to a 138 °C mean and 134 W and fell off the bus at 12:02. It is '
     'out of service until the fan settings are fixed on site: the air that reaches it is too warm.'),
    ('aifoundry1', ['aifoundry1-c0', 'aifoundry1-c1'], '2026-10-02T12:55:14', '2026-10-02T12:59:24', 'power',
     'aifoundry1 off: card 0’s fan replaced',
     'The machine was off while card 0’s broken fan was replaced; afterwards card 0 idles at 49 °C (65 °C before).'),
]

MIRROR = os.path.join(paths.REPO, 'docs', 'reports', 'MIRROR.md')
UUID = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'


def mirror_pages():
    """uuid -> (slug, title, public?) of every page MIRROR.md lists"""
    out, txt = {}, open(MIRROR, encoding='utf-8').read()
    a, b = txt.find('<!-- mirror:begin -->'), txt.find('<!-- mirror:end -->')
    for line in txt[a:b].splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 3:
            continue
        m, u = re.match(r'\[(.*?)\]\(https://spacesheep\.dev/@yaroslavvb/([\w.-]+)\)', cells[0]), re.search(UUID, cells[1])
        if m and u:
            out[u.group(0)] = (m.group(2), m.group(1), bool(re.match(r'public\b', cells[2])))
    return out


def text_of(c):
    if isinstance(c, str):
        return c
    return '\n'.join(x.get('text', '') for x in c or [] if isinstance(x, dict) and x.get('type') == 'text')


def before_cut(ts):
    return ts and (CUT is None or T(ts) <= CUT)


def slash_text(s):
    name = re.search(r'<command-name>(.*?)</command-name>', s or '', re.S)
    args = re.search(r'<command-args>(.*?)</command-args>', s or '', re.S)
    return ((name.group(1).strip() if name else '') + (' ' + args.group(1).strip() if args and args.group(1).strip() else '')).strip()


def owner_messages(path, sid8):
    """the owner's inputs to a session: prompts, messages sent while it worked, slash commands, each with its words as the
    public page may show them (prompt_privacy.redact)"""
    enq, out = {}, []
    for line in open(path, encoding='utf-8', errors='replace'):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        ts, t = e.get('timestamp'), e.get('type')
        if not before_cut(ts):
            continue
        if t == 'queue-operation' and e.get('operation') == 'enqueue' and isinstance(e.get('content'), str):
            enq[e['content'][:200]] = ts
        elif t == 'user' and (e.get('origin') or {}).get('kind') == 'human':
            s = text_of((e.get('message') or {}).get('content'))
            sent = enq.get(s[:200]) if e.get('promptSource') == 'queued' else None
            out.append((sent or ts, 'prompt', len(s), s))
        elif t == 'user' and text_of((e.get('message') or {}).get('content')).startswith('<command-name>'):
            out.append((ts, 'slash-command', 0, slash_text(text_of(e['message']['content']))))
        elif t == 'system' and e.get('subtype') == 'local_command' and (e.get('content') or '').startswith('<command-name>'):
            out.append((ts, 'slash-command', 0, slash_text(e.get('content'))))
        elif t == 'attachment' and (e.get('attachment') or {}).get('type') == 'queued_command':
            a = e['attachment']
            if (a.get('origin') or {}).get('kind') == 'human':
                p = text_of(a.get('prompt'))
                out.append((a.get('timestamp') or ts, 'midturn', len(p), p))
    msgs, unsummarised = [], []
    for ts, kind, n, raw in sorted(out):
        key = T(ts).astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
        sm = NEIGHBOR_SUMMARIES.get((sid8, key)) or NEIGHBOR_SUMMARIES_BY_LEN.get((sid8, key, n))
        if not sm:
            unsummarised.append(f'{key} ({kind}, {n} characters)')
            continue
        shown_text, removed = PP.redact(raw)
        msgs.append({'ts': iso(T(ts)), 'kind': kind, 'chars': n, 'summary': sm[0], 'category': sm[1],
                     'text': shown_text, 'removed': sorted(set(removed)), 'session': sid8})
    return msgs, unsummarised


def deploys_and_commits(files, mirror):
    """every spacesheep deploy (its time, and the space from the CLI's output or the command) and every commit a session
    made (the '[branch sha]' line git prints), from its transcripts"""
    deps, shas = [], set()
    slug_uuid = {v[0]: u for u, v in mirror.items()}
    for f in files:
        pend = {}
        for line in open(f, encoding='utf-8', errors='replace'):
            if 'tool_use' not in line and 'tool_result' not in line:
                continue
            try:
                e = json.loads(line)
            except ValueError:
                continue
            ts = e.get('timestamp')
            if not before_cut(ts):
                continue
            for c in (e.get('message') or {}).get('content') or []:
                if not isinstance(c, dict):
                    continue
                if c.get('type') == 'tool_use' and c.get('name') == 'Bash':
                    cmd = (c.get('input') or {}).get('command') or ''
                    if re.search(r'spacesheep(?:\.js)?\S*\s+deploy\b', cmd) or 'git commit' in cmd:
                        pend[c.get('id')] = (ts, cmd)
                elif c.get('type') == 'tool_result' and c.get('tool_use_id') in pend:
                    ts0, cmd = pend.pop(c['tool_use_id'])
                    res = text_of(c.get('content')) if not isinstance(c.get('content'), str) else c['content']
                    if 'git commit' in cmd:   # '[main abc1234] ...', or a log line after a quiet commit; kept if made then
                        for sha in set(re.findall(r'^\[[\w./-]+ ([0-9a-f]{7,})\]', res, re.M) + re.findall(r'^([0-9a-f]{7,12}) ', res, re.M)):
                            shas.add((sha, ts0, ts))
                    if not re.search(r'spacesheep(?:\.js)?\S*\s+deploy\b', cmd):
                        continue
                    for kind, slug in re.findall(r'✓ (Created|Updated) https://spacesheep\.dev/@yaroslavvb/([\w.-]+)', res):
                        deps.append({'ts': ts0, 'uuid': slug_uuid.get(slug), 'slug': slug, 'created': kind == 'Created'})
                    if not re.search(r'✓ (Created|Updated)', res):
                        m = re.search(r'--space[ =]"?(' + UUID + ')', cmd)
                        if m:
                            deps.append({'ts': ts0, 'uuid': m.group(1), 'slug': (mirror.get(m.group(1)) or (None,))[0],
                                         'created': False, 'unconfirmed': True})
    return deps, shas


def commit_rows(shas):
    """the commits a session made: a sha its commit command printed, whose commit time falls within that command"""
    rows = {}
    for sha, t0, t1 in sorted(shas):
        r = subprocess.run(['git', '-C', paths.REPO, 'log', '-1', '--format=%H%x1f%aI%x1f%cI%x1f%s', sha], capture_output=True, text=True)
        if r.returncode != 0 or not r.stdout.strip():
            continue
        h, d, cd, s = r.stdout.strip().split('\x1f', 3)
        if T(t0) - timedelta(seconds=60) <= datetime.fromisoformat(cd) <= T(t1) + timedelta(seconds=60):
            rows[h[:7]] = {'sha': h[:7], 'ts': iso(datetime.fromisoformat(d)), 'subject': s}
    return sorted(rows.values(), key=lambda c: c['ts'])


def scrub(s):
    """the privacy table's name redactions, then its sanitize rules (as build_artifacts.py and sanitize_extracts.py)"""
    P = paths.private()
    for a, b in P.get('artifact_name_redactions', []) + P.get('sanitize', []):
        s = re.sub(a, b, s)
    return s


def shown(d, mirror):
    """a deploy the page may name: of a page MIRROR.md lists as public, other than the report for the lab lead (which the
    page never names) and the spaces it never lists"""
    if d['uuid'] not in mirror or not mirror[d['uuid']][2]:
        return False
    slug, pre = mirror[d['uuid']][0], paths.private().get('lab_report_slug_prefix')
    return not (pre and slug.startswith(pre)) and slug not in ('aifoundry-lab-accounts',)


def one(sid, mirror):
    sid8 = sid[:8]
    proj = paths.project_of(sid)
    if not proj:
        print(f'{sid8}: no transcript in {paths.PROJECTS}; left out', file=sys.stderr)
        return None, []
    main = os.path.join(proj, sid + '.jsonl')
    ms = X.scan(main)
    times = [t for t in ms['times'] if CUT is None or t <= CUT]
    waits = [w for w in ms['long_tool_waits'] if before_cut(w[1])]
    busy = X.merge_waits(X.busy_intervals(times), waits)
    # its subagents: every agent transcript once (a workflow's copy before a top-level one of the same agent)
    files = {}
    for f in sorted(glob.glob(os.path.join(proj, sid, 'subagents', '**', 'agent-*.jsonl'), recursive=True),
                    key=lambda f: ('/workflows/' not in f, f)):
        files.setdefault(os.path.basename(f), f)
    sub, agent_s, msgs_usage, sub_ts = [], 0.0, {}, {}
    for mid, rec in ms['msgs'].items():
        if rec['ts'] and before_cut(iso(rec['ts'])):
            msgs_usage[mid] = dict(rec['usage'])
    workflows = set()
    for f in files.values():
        sc = X.scan(f)
        ts_ = [t for t in sc['times'] if CUT is None or t <= CUT]
        if not ts_:
            continue
        if '/workflows/' in f:
            workflows.add(f.split('/workflows/')[1].split('/')[0])
        b = X.busy_intervals(ts_)
        sub += b
        agent_s += sum((y - x).total_seconds() for x, y in b)
        for mid, rec in sc['msgs'].items():
            if rec['ts'] and before_cut(iso(rec['ts'])):
                if mid not in ms['msgs']:
                    sub_ts[mid] = rec['ts']
                u = msgs_usage.setdefault(mid, {})
                for k, v in rec['usage'].items():
                    u[k] = max(u.get(k, 0), v)
    sub.sort()
    su = []
    for a, b in sub:
        if su and a <= su[-1][1]:
            su[-1][1] = max(su[-1][1], b)
        else:
            su.append([a, b])
    tok = collections.Counter()
    for u in msgs_usage.values():
        for k in ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens'):
            tok[k] += int(u.get(k) or 0)
    owner, unsum = owner_messages(main, sid8)
    deps, shas = deploys_and_commits([main] + list(files.values()), mirror)
    commits = [c for c in commit_rows(shas) if before_cut(c['ts'])]
    events = [{'t': iso(L(a)), 'e': iso(L(b)) if b else None, 'kind': k, 'title': ti, 'text': tx}
              for a, b, k, ti, tx in EVENTS.get(sid8, []) if before_cut(iso(L(a)))]
    public = [d for d in deps if shown(d, mirror)]
    for d in deps:
        d['public'] = d in public
    for d in public:   # a deploy of a public page: an event of its own
        slug, title = mirror[d['uuid']][:2]
        events.append({'t': iso(T(d['ts'])), 'e': None, 'kind': 'page', 'title': ('Published: ' if d['created'] else 'Updated: ') + title,
                       'text': f'A deploy of the public page {title} (spacesheep.dev/@yaroslavvb/{slug}).'})
    for c in commits:
        events.append({'t': c['ts'], 'e': None, 'kind': 'commit', 'title': 'A commit: ' + c['sha'], 'text': scrub(c['subject'])})
    events.sort(key=lambda e: e['t'])
    lane, name, title = NEIGHBOR_INFO.get(sid8, ('neighbor', 'a neighbor session', 'another Claude Code session on aifoundry2'))
    row = {
        'id': sid8, 'lane': lane, 'name': name, 'title': title,
        'first': iso(times[0]) if times else None, 'last': iso(times[-1]) if times else None,
        'busy': [[iso(a), iso(b)] for a, b in busy], 'busy_h': round(sum((b - a).total_seconds() for a, b in busy) / 3600, 2),
        'sub': [[iso(a), iso(b)] for a, b in su], 'agents': len(files), 'workflow_runs': len(workflows),
        'agent_h': round(agent_s / 3600, 2),
        'tokens': {'input': tok['input_tokens'], 'cache_creation': tok['cache_creation_input_tokens'],
                   'cache_read': tok['cache_read_input_tokens'], 'output': tok['output_tokens'], 'total': sum(tok.values())},
        'messages': owner, 'unsummarised': unsum, 'events': events,
        'deploys': {'public': len(public), 'other': len(deps) - len(public)},
        'commits': [c['sha'] for c in commits],
    }
    prev = PREV.get(sid8)
    if prev and prev.get('first') and times and T(prev['first']) < times[0] - timedelta(minutes=5):
        row, deps = merge_prev(row, deps, prev, times[0], msgs_usage, sub_ts)
    return row, deps


# A transcript can be rewritten shorter: 97db24ee's, resumed on 2 October, now starts at 10:05 PDT that day, and its
# 30 September part (the link test, the hang, the power cycle) is only in the committed extract. For such a session the
# committed extract's rows before the transcript's first line are kept: its busy intervals, the owner's messages
# (summaries only: their words are no longer on the machine), its page and commit events, its deploys and commits. The
# subagents' transcripts were not rewritten, so their intervals and agent-hours come from the new scan alone, and their
# tokens before the cut are subtracted from the committed total, which already holds them.
PREV = {}
try:
    for _s in json.load(open(os.path.join(paths.DATA_DIR, 'neighbors.json'), encoding='utf-8')).get('sessions', []):
        PREV[_s['id']] = _s
except (OSError, ValueError):
    pass
PREV_WORK = os.path.expanduser(os.environ.get('TIMELINE_PREV_WORK') or '~/claude/work/et-soc1-timeline/work')


def merge_prev(row, deps, prev, first, msgs_usage, sub_ts):
    cut = iso(first)
    old = lambda ts: ts and T(ts) < first
    row = dict(row)
    row['first'] = prev['first']
    row['busy'] = [b for b in prev['busy'] if T(b[1]) <= first] + row['busy']
    row['busy_h'] = round(sum((T(b) - T(a)).total_seconds() for a, b in row['busy']) / 3600, 2)
    before = collections.Counter()
    for mid, ts in sub_ts.items():
        if ts < first:
            for k in ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens'):
                before[k] += int(msgs_usage.get(mid, {}).get(k) or 0)
    tk = dict(row['tokens'])
    for k, kk in (('input', 'input_tokens'), ('cache_creation', 'cache_creation_input_tokens'),
                  ('cache_read', 'cache_read_input_tokens'), ('output', 'output_tokens')):
        tk[k] = tk[k] + int(prev['tokens'].get(k, 0)) - before[kk]
    tk['total'] = sum(tk[k] for k in ('input', 'cache_creation', 'cache_read', 'output'))
    row['tokens'] = tk
    row['messages'] = [dict(m, text=None, removed=[], session=row['id'], lost=True)
                       for m in prev.get('messages', []) if old(m['ts'])] + row['messages']
    kept = [e for e in prev.get('events', []) if e['kind'] in ('page', 'commit') and old(e['t'])]
    seen = {(e['t'], e['title']) for e in row['events']}
    row['events'] = sorted(row['events'] + [e for e in kept if (e['t'], e['title']) not in seen], key=lambda e: e['t'])
    new = [d for d in deps if not old(d['ts'])]
    row['deploys'] = {'public': prev['deploys']['public'] + sum(1 for d in new if d.get('public')),
                      'other': prev['deploys']['other'] + sum(1 for d in new if not d.get('public'))}
    row['commits'] = sorted(set(prev.get('commits', [])) | set(row['commits']))
    row['merged_before'] = cut
    try:
        olds = [d for d in json.load(open(os.path.join(PREV_WORK, 'neighbor_deploys.json'))) if d.get('session') == row['id']
                and old(d['ts'])]
    except (OSError, ValueError):
        olds = []
    return row, [dict(d, session=None) for d in olds] + new


def group(rows):
    """one lane for several short sessions: their intervals, messages and events together"""
    lane, name, title = NEIGHBOR_INFO['short']
    tok = collections.Counter()
    for r in rows:
        tok.update(r['tokens'])
    busy = sorted(b for r in rows for b in r['busy'])
    return {'id': 'short', 'ids': [r['id'] for r in rows], 'lane': lane, 'name': name, 'title': title,
            'first': min(r['first'] for r in rows if r['first']), 'last': max(r['last'] for r in rows if r['last']),
            'busy': busy, 'busy_h': round(sum(r['busy_h'] for r in rows), 2),
            'sub': sorted(b for r in rows for b in r['sub']), 'agents': sum(r['agents'] for r in rows),
            'workflow_runs': sum(r['workflow_runs'] for r in rows), 'agent_h': round(sum(r['agent_h'] for r in rows), 2),
            'tokens': dict(tok), 'messages': sorted((m for r in rows for m in r['messages']), key=lambda m: m['ts']),
            'unsummarised': [u for r in rows for u in r['unsummarised']],
            'events': sorted((e for r in rows for e in r['events']), key=lambda e: e['t']),
            'deploys': {'public': sum(r['deploys']['public'] for r in rows), 'other': sum(r['deploys']['other'] for r in rows)},
            'commits': sorted({c for r in rows for c in r['commits']})}


def main():
    mirror = mirror_pages()
    sessions, all_deps = [], []
    for sid in paths.NEIGHBORS:
        parts = [p for p in sid.split('+') if p]
        rows = []
        for p in parts:
            row, deps = one(p, mirror)
            if row:
                rows.append(row)
                all_deps += [dict(d, session=d.get('session') or p[:8]) for d in deps]
        if len(parts) > 1 and rows:
            sessions.append(group(rows))
        elif rows:
            sessions.append(rows[0])
    end = CUT or datetime.now(timezone.utc)
    hosts = [{'host': h, 'cards': cards, 's': iso(L(a)), 'e': iso(min(L(b), end) if b else end), 'kind': k, 'title': ti,
              'text': tx}
             for h, cards, a, b, k, ti, tx in HOSTS if before_cut(iso(L(a)))] if sessions else []
    out = {'generated': iso(datetime.now(timezone.utc)), 'cutoff': paths.CUTOFF,
           'rule': ' '.join(__doc__.split('\n\n')[1].split()),
           'sessions': sessions, 'hosts': hosts}
    tl = paths.ensure_tl()
    json.dump(out, open(os.path.join(tl, 'neighbors.json'), 'w'), indent=1, ensure_ascii=False)
    os.makedirs(os.path.join(tl, 'work'), exist_ok=True)
    json.dump(all_deps, open(os.path.join(tl, 'work', 'neighbor_deploys.json'), 'w'), indent=1)
    for s in sessions:
        print(s['id'], s['first'], s['last'], 'busy', s['busy_h'], 'h in', len(s['busy']), 'intervals; subagents', s['agents'],
              'in', s['workflow_runs'], 'workflows,', s['agent_h'], 'agent-h; tokens', s['tokens']['total'])
        print('  messages', len(s['messages']), 'unsummarised', s['unsummarised'])
        print('  deploys', s['deploys'], 'commits', s['commits'])
        for e in s['events']:
            print('  ', e['t'], e['kind'], e['title'])
    print('hosts', [(h['host'], h['kind'], h['s'], h['e']) for h in hosts])
    print('neighbor deploys (work/neighbor_deploys.json):', len(all_deps))


if __name__ == '__main__':
    main()
