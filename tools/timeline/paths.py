"""Where the session-timeline scripts read and write: every path comes from the repository root or an environment
variable, so the scripts run from any checkout (tools/timeline/README.md lists the variables).

  TIMELINE_TRANSCRIPTS  the Claude Code project folder that holds the session's transcripts (default: the Claude Code
                        project folder of the checkout's parent directory, where the session ran)
  TIMELINE_SESSION      the session id (default ed6d06d5-de26-4323-94f1-0dc808eafbda)
  TIMELINE_DIR          the working folder the extraction scripts write their extracts to (default
                        ~/claude/work/et-soc1-timeline, which survives a reboot; until 30 Sep 2026 it was
                        $TMPDIR/et-soc1-timeline, which a boot clears); build_cards.py reads the lab machines' copied
                        queue logs from its hostlogs/<host>/ and build_artifacts.py keeps its work/ files there
  TIMELINE_PRIVATE      the local privacy table, never committed (default ~/.config/et-soc1-timeline/private.json);
                        extract_agents.py and build_artifacts.py stop without one unless it is set to none
  TIMELINE_CUTOFF       an ISO time: the snapshot; transcript lines after it are ignored
  TIMELINE_NEIGHBORS    comma-separated ids of other Claude Code sessions whose work the page shows in lanes of their own
                        (extract_neighbors.py; default 97db24ee-042f-547a-86c0-e1444e260a06, the session of 30 Sep that ran
                        the link test; none for no neighbor lane); an id joined to others with '+' (a+b+c) is one lane for
                        several short sessions
  TIMELINE_MORE_PROJECTS other project folders to find neighbor sessions in (default: the second account's folder of the
                        same name, ~/.claude-yv2/projects/<name>)
  TIMELINE_REPO         the repository (default: the checkout this file is in)
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.environ.get('TIMELINE_REPO') or os.path.join(HERE, '..', '..'))
DATA_DIR = os.path.join(REPO, 'docs', 'reports', 'data', '2026-09-27-session-timeline')

# Claude Code names a project folder after the directory's path, every character other than a letter or digit a '-'
PROJ = os.path.expanduser(os.environ.get('TIMELINE_TRANSCRIPTS') or
                          '~/.claude/projects/' + re.sub(r'[^A-Za-z0-9]', '-', os.path.dirname(REPO)))
SID = os.environ.get('TIMELINE_SESSION', 'ed6d06d5-de26-4323-94f1-0dc808eafbda')
PRE_SID = '2e4feded-6776-4133-ad4c-bb790798b64f'   # a 3-second session just before this one (counted, not drawn)
MAIN = os.path.join(PROJ, SID + '.jsonl')
PRE = os.path.join(PROJ, PRE_SID + '.jsonl')
SUB = os.path.join(PROJ, SID, 'subagents')
WFJSON = os.path.join(PROJ, SID, 'workflows')

# the owner's second claude.ai account keeps its sessions in its own config home, in a project folder of the same name:
# neighbor sessions are looked for there too (TIMELINE_MORE_PROJECTS, folders separated by ':')
MORE_PROJECTS = [os.path.expanduser(p) for p in
                 (os.environ.get('TIMELINE_MORE_PROJECTS') or '~/.claude-yv2/projects/' + os.path.basename(PROJ)).split(':') if p]
PROJECTS = [PROJ] + [p for p in MORE_PROJECTS if os.path.isdir(p) and p != PROJ]


def project_of(sid):
    """the project folder (PROJ first, then MORE_PROJECTS) that holds session sid's transcript, or None"""
    for p in PROJECTS:
        if os.path.exists(os.path.join(p, sid + '.jsonl')):
            return p
    return None


_NB = os.environ.get('TIMELINE_NEIGHBORS', '97db24ee-042f-547a-86c0-e1444e260a06')
NEIGHBORS = [] if _NB.strip().lower() in ('', 'none') else [x.strip() for x in _NB.split(',') if x.strip()]

TL = os.path.expanduser(os.environ.get('TIMELINE_DIR') or '~/claude/work/et-soc1-timeline')
PRIVATE_TABLE = os.path.expanduser(os.environ.get('TIMELINE_PRIVATE', '~/.config/et-soc1-timeline/private.json'))
CUTOFF = os.environ.get('TIMELINE_CUTOFF')


def private():
    """The local privacy table (people's names, the lab-lead report's identifiers, the sanitize rules and the extra
    forbidden patterns), or {} without one."""
    try:
        return json.load(open(PRIVATE_TABLE))
    except OSError:
        return {}


def ensure_tl():
    os.makedirs(TL, exist_ok=True)
    return TL
