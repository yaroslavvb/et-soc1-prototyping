#!/usr/bin/env python3
"""dmcmd_audit: the preflight check of the device-management commands a runner's files can send (Q136(w), 2 Nov 2026).

A runner calls it on its own files (harness, sampler wrappers, helpers) before its first launch:

    python3 tools/claims-v3/dmcmd_audit.py --allow SET_STATS_RUN_CONTROL tools/claims-v3/e126/run_e126.py tools/claims-v3/lib.sh

It lists every place in those files that can send a command to a card's service processor, classifies each one READ
or WRITE from the audit table (tools/claims-v3/dmcmd_table.json: et-platform 836a4ab, BL2 0.22.0, classified from the
firmware source), and exits 3 (NO-GO) on any of:

  * a WRITE whose name is not in the caller's allow-list (--allow NAME, repeatable or comma-separated; names without
    the DM_CMD_ prefix; pseudo names SYSFS_WRITE, SETPCI_WRITE, MODULE_LOAD, HOST_REBOOT);
  * a command the table marks UNSUPPORTED or UNCLASSIFIED, a DM_CMD_ name the table does not know, or a command named
    at run time (DYNAMIC), unless allowed by name;
  * a read with a blocking side effect: a residency read of a raw state the firmware does not have (SP_ERROR_LOG: two
    SP Runtime Errors a read, E77 F1), or residency states the checker cannot see (RESIDENCY_STATES_UNRESOLVED);
  * with --deny-pmic-read, any read that reaches the PMIC (GET_ASIC_VOLTAGE, GET_MODULE_VOLTAGE).

Exit 0 = GO (nothing disallowed), 3 = NO-GO, 2 = usage error. --json prints the records; --markdown prints a "Device
commands sent" section for the run's README; --table prints the table.

What it finds, and what it cannot. It reads source text, line by line (shell continuation lines and Python/JS brackets
joined), skipping comments and Python docstrings. It finds DM_CMD_ names; dev_mngt_service's -o codes and -t trace
operations; ettelem subcommands (mapped through each variant's reviewed table, the variant taken from the binary's path
or from the variable that holds it, else the union of all variants); the statistics reset (--reset-ms,
--reset-once-file, or arguments forwarded with "$@" / *args, which might carry one); raw ioctl clients' numeric codes;
et-reset, sysfs and setpci writes, module loads and reboots. A file whose SHA-256 matches a reviewed source in the table
(the five ettelem variants, the raw clients) is taken from the table instead of being scanned. It cannot follow a
command assembled across functions or files, so a wrapper that forwards a command from a variable is listed as a
WRAPPER line for a person to check; the literal names at its call sites are what it classifies. It over-reports rather
than under-reports: a false WRITE is a NO-GO a person clears by reading the line, never by --allow.
"""
import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_TABLE = HERE / "dmcmd_table.json"
EXIT_GO, EXIT_USAGE, EXIT_NOGO = 0, 2, 3
SUBCOMMANDS = ("sample", "config", "temp", "loglevel", "sptrace", "residency", "uptime", "threshold", "profile")
CODE_EXT = {".sh": "sh", ".bash": "sh", ".py": "py", ".mjs": "js", ".js": "js", ".c": "c", ".cc": "c", ".cpp": "c",
            ".h": "c", ".hpp": "c"}
DOC_EXT = {".md", ".txt", ".rst", ".html", ".csv", ".jsonl", ".log", ".json", ".yaml", ".yml", ".toml"}
VARIANT_RE = re.compile(r"ettelem-(hp|dv2|e84|e77|e118)\b")
DM_TOKEN_RE = re.compile(r"\bDM_CMD_[A-Z0-9_]*")
FORWARD_RE = re.compile(r'"\$@"|"\$\{@\}"|\$\*|\$@|\*args|\*argv|\*rest|\*extra|\*a\b')
OTHER_HINT = re.compile(r"et-reset|/sys/|setpci|modprobe|rmmod|insmod|reboot|poweroff|shutdown|halt|systemctl|etcfg"
                        r"|--reset-ms|--reset-once-file")
NOT_WRAPPERS = {"print", "get", "pop", "setdefault", "join", "startswith", "endswith", "split", "replace", "find",
                "index", "count", "append", "extend", "format", "load", "loads", "dump", "dumps", "open", "Path",
                "add", "remove", "discard", "update", "getattr", "hasattr", "isinstance", "str", "int", "float",
                "len", "sorted", "list", "dict", "set", "tuple", "log", "note", "warn", "fail", "abort", "die",
                "error", "info", "debug", "write", "match", "search", "fullmatch", "sub", "compile", "exists",
                "mark", "echo", "printf", "jl", "load_jsonl", "read_jsonl"}


class Table:
    def __init__(self, path):
        self.path = Path(path)
        self.raw = json.loads(self.path.read_text())
        self.commands = self.raw["commands"]
        self.pseudo = self.raw.get("pseudo", {})
        self.by_id = {}
        for name, c in self.commands.items():
            self.by_id.setdefault(int(c["id"]), name)
        self.variants = self.raw["tools"]["variants"]
        self.raw_clients = self.raw["tools"].get("raw_clients", {})
        self.reviewed = {}
        for v, info in self.variants.items():
            self.reviewed[info["sha256"]] = ("variant", v, info)
        for path_, info in self.raw_clients.items():
            self.reviewed[info["sha256"]] = ("raw_client", path_, info)

    def entry(self, name):
        if name in self.commands:
            return self.commands[name]
        if name in self.pseudo:
            return self.pseudo[name]
        return None


_QUOTED = re.compile(r'"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'')
_QUOTE_CHAR = re.compile(r"[\"']")


def strip_quoted(s):
    """Blank out the inside of quoted strings (so a '#' inside quotes is not a comment); an unterminated quote
    blanks the rest of the line."""
    if '"' not in s and "'" not in s:
        return s
    parts, i = [], 0
    for m in _QUOTED.finditer(s):
        seg = s[i:m.start()]
        q = _QUOTE_CHAR.search(seg)
        if q:
            parts.append(seg[:q.start() + 1] + " " * (len(s) - i - q.start() - 1))
            return "".join(parts)
        g = m.group(0)
        parts.append(seg + g[0] + " " * (len(g) - 2) + g[-1])
        i = m.end()
    seg = s[i:]
    q = _QUOTE_CHAR.search(seg)
    if q:
        seg = seg[:q.start() + 1] + " " * (len(seg) - q.start() - 1)
    parts.append(seg)
    return "".join(parts)


def code_part(line, lang, state):
    """The code on one physical line, comments removed. state carries block comments and docstrings across lines."""
    if lang in ("c", "js"):
        out, i = [], 0
        while i < len(line):
            if state.get("block"):
                j = line.find("*/", i)
                if j < 0:
                    return "".join(out)
                state["block"] = False
                i = j + 2
                continue
            masked = strip_quoted(line[i:])
            k_line, k_block = masked.find("//"), masked.find("/*")
            cut = [k for k in (k_line, k_block) if k >= 0]
            if not cut:
                out.append(line[i:])
                break
            k = min(cut)
            out.append(line[i:i + k])
            if k == k_line:
                break
            state["block"] = True
            i = i + k + 2
        return "".join(out)
    if lang == "json":
        return line
    # sh / py
    if lang == "py":
        if state.get("doc"):
            q = state["doc"]
            j = line.find(q)
            if j < 0:
                return ""
            state["doc"] = None
            line = line[j + 3:]
        stripped = line.lstrip()
        m = re.match(r'^[rRbBuU]{0,2}("""|\'\'\')', stripped)
        if m:  # a docstring or bare string statement: documentation, not code
            q = m.group(1)
            rest = stripped[m.end():]
            j = rest.find(q)
            if j < 0:
                state["doc"] = q
                return ""
            line = rest[j + 3:]
    if line.lstrip().startswith("#"):
        return ""
    masked = strip_quoted(line)
    m = re.search(r"(^|\s)#", masked)
    return line[:m.start()] if m else line


def logical_lines(text, lang):
    """(first line number, joined code) for each logical line: shell backslash continuations and open brackets joined."""
    state, buf, start, depth = {}, [], None, 0
    for n, raw in enumerate(text.split("\n"), 1):  # "\n" only: splitlines() also breaks at \f and U+2028
        code = code_part(raw.rstrip("\r"), lang, state)
        if start is None:
            start = n
        buf.append(code)
        masked = strip_quoted(code)
        if lang in ("py", "js", "c", "json"):
            depth += masked.count("(") + masked.count("[") + masked.count("{") \
                - masked.count(")") - masked.count("]") - masked.count("}")
            if depth < 0:
                depth = 0
        cont = (lang == "sh" and code.rstrip().endswith("\\")) or (depth > 0 and len(buf) < 40)
        if cont:
            continue
        yield start, " ".join(b.rstrip("\\") for b in buf)
        buf, start, depth = [], None, 0
    if buf:
        yield start, " ".join(buf)


def lang_of(path, text):
    ext = path.suffix.lower()
    if ext in CODE_EXT:
        return CODE_EXT[ext]
    if ext in DOC_EXT:
        return None
    first = text.split("\n", 1)[0]
    if first.startswith("#!"):
        if "python" in first:
            return "py"
        if "node" in first:
            return "js"
        return "sh"
    return "sh" if ext == "" else None


def plain_tokens(s):
    """Tokens with quotes as separators too: a command inside a quoted string still splits into its words."""
    return [t.rstrip(";&|") for t in re.findall(r"[^\s,()\[\]'\"]+", s)]


def words(s):
    """Tokens of a command line, quotes removed (shell words or Python/JS string items)."""
    return [t.strip("\"'").rstrip(";&|") for t in re.findall(r'"[^"]*"|\'[^\']*\'|[^\s,()\[\]]+', s)]


class Audit:
    def __init__(self, table, files):
        self.t = table
        self.files = files
        self.records = []
        self.notes = []
        self.assign = {}  # variable name -> right-hand sides that name a device tool, from all scanned files
        self.file_assign = {}  # (file, name) -> the same, for the file that assigns it
        self.functions = set()  # shell function names defined in the scanned files

    def add(self, path, line, tool, command, detail="", conditional=False, tags=()):
        self.records.append({"file": str(path), "line": line, "tool": tool, "command": command, "detail": detail,
                             "conditional": conditional, "tags": list(tags)})

    # ---- variables that hold an ettelem binary or dev_mngt_service -------------------------------------------------
    def collect_assignments(self, texts):
        rx = re.compile(r"(?:^|[\s;])(?:export\s+|local\s+|readonly\s+)?(?:self\.)?([A-Za-z_][A-Za-z0-9_]*)\s*:?=\s*(.+)")
        for path, (lang, text, lines) in texts.items():
            if lang == "sh":
                self.functions |= set(re.findall(r"(?m)^\s*(?:function\s+)?([A-Za-z_][\w-]*)\s*\(\)", text))
            for _, code in lines:
                if "ettelem" not in code and "dev_mngt_service" not in code:
                    continue
                for m in rx.finditer(code):
                    name, rhs = m.group(1), m.group(2)
                    if "ettelem" in rhs or "dev_mngt_service" in rhs:
                        self.assign.setdefault(name, []).append(rhs)
                        self.file_assign.setdefault((str(path), name), []).append(rhs)
                for m in re.finditer(r"\$\{([A-Za-z_][A-Za-z0-9_]*):-([^}]*)\}", code):  # ${VAR:-default}
                    if "ettelem" in m.group(2) or "dev_mngt_service" in m.group(2):
                        self.assign.setdefault(m.group(1), []).append(m.group(2))
                        self.file_assign.setdefault((str(path), m.group(1)), []).append(m.group(2))

    def rhs_of(self, name):
        """What a variable can hold: the current file's assignments, else (for a tool-like name only) any file's."""
        own = self.file_assign.get((self.cur, name))
        if own:
            return own
        if name in self.assign and len(name) >= 3 and (name.isupper() or re.search(r"(?i)ett|dms|mngt|devm|tel", name)):
            return self.assign[name]
        return []

    def var_refs(self, code):
        names = set(re.findall(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)", code))
        names |= set(re.findall(r"(?:self\.)?\b([A-Za-z_][A-Za-z0-9_]*)\b", code))
        return [n for n in names if self.rhs_of(n)]

    def variants_for(self, code):
        """Which ettelem variants a line can run: from a path on the line, else from the variable it uses, else all."""
        found = set()
        sources = [code] + [rhs for n in self.var_refs(code) for rhs in self.rhs_of(n) if "ettelem" in rhs]
        for s in sources:
            for m in VARIANT_RE.finditer(s):
                v = m.group(1)
                found.add("ettelem-dv2" if v == "e84" else "ettelem-" + v)
            if re.search(r"(tools|build|live)/ettelem(-build)?/ettelem\b|build/ettelem/", s):
                found.add("ettelem")
        return sorted(found) if found else sorted(self.t.variants)

    def is_ettelem_line(self, code):
        if re.search(r"ettelem", code):
            return True
        return any("ettelem" in rhs for n in self.var_refs(code) for rhs in self.rhs_of(n))

    def is_dms_line(self, code):
        if "dev_mngt_service" in code:
            return True
        return any("dev_mngt_service" in rhs for n in self.var_refs(code) for rhs in self.rhs_of(n))

    # ---- the rules -------------------------------------------------------------------------------------------------
    def refers_ettelem(self, tok, file_refs_ettelem):
        """Does this word name an ettelem binary: a path or name with 'ettelem' in it, a variable that holds one,
        or (in a file that runs ettelem) any shell variable, whose binary is then unknown."""
        if "ettelem" in tok:
            return True
        m = re.fullmatch(r"\$\{?([A-Za-z_]\w*)\}?|(?:self\.)?([A-Za-z_]\w*)", tok)
        if not m:
            return False
        name = m.group(1) or m.group(2)
        if any("ettelem" in rhs for rhs in self.rhs_of(name)):
            return True
        return bool(file_refs_ettelem and m.group(1))

    def scan_ettelem(self, path, n, code, file_refs_ettelem):
        toks = plain_tokens(code)
        hit = None
        for i in range(len(toks) - 1):  # the subcommand is the word right after the binary
            if toks[i + 1] in SUBCOMMANDS and self.refers_ettelem(toks[i], file_refs_ettelem):
                hit = (i, toks[i + 1], True)
                break
        if hit is None:
            if not file_refs_ettelem:
                return False
            # a wrapper call such as self.tool("residency", ...) in a file that runs ettelem
            for m2 in re.finditer(r"(?<![\w.])(?:self\.)?([A-Za-z_]\w*)\(\s*[\"'](" + "|".join(SUBCOMMANDS) + r")[\"']",
                                  code):
                if m2.group(1) not in NOT_WRAPPERS:
                    j = next((k for k, t in enumerate(toks) if t == m2.group(2)), None)
                    if j is not None:
                        hit = (j - 1, m2.group(2), False)
                        break
            if hit is None:
                return False
        i0, sub, on_line = hit
        rest = toks[i0 + 2:]
        variants = self.variants_for(code)
        tool = "ettelem " + sub + ("" if on_line else " (wrapper call)")
        vtag = "/".join(variants)
        asked = []  # reset options asked for on the line, with a value that is not a literal 0
        for k, w in enumerate(rest):
            if w in ("--reset-ms", "--reset-once-file"):
                val = rest[k + 1] if k + 1 < len(rest) else ""
                if not (w == "--reset-ms" and val == "0"):
                    asked.append(w)
        forwarded = bool(FORWARD_RE.search(code))
        sends, reset_possible, refused = set(), False, []
        for v in variants:
            sc = self.t.variants[v]["subcommands"].get(sub)
            if sc is None:
                continue
            sends |= set(sc["sends"])
            if sub != "sample":
                continue
            ropts = sc.get("reset_options", [])
            if asked:
                if any(o in ropts for o in asked):
                    sends |= set(sc["reset_sends"])
                else:
                    refused.append(f"{v} refuses {', '.join(asked)}")
            elif forwarded and ropts:
                sends |= set(sc["reset_sends"])
                reset_possible = True
        for cmd in sorted(sends):
            tags, cond, detail = [], False, f"variant {vtag}"
            if cmd == "SET_STATS_RUN_CONTROL" and reset_possible:
                cond = True
                detail += "; forwarded arguments may carry --reset-ms"
            if cmd == "GET_MODULE_RESIDENCY_THROTTLE_STATES":
                states = []
                for w in rest:  # the integers right after the subcommand, nothing later on the line
                    if not re.fullmatch(r"-?\d+", w):
                        break
                    states.append(w)
                valid = set(self.t.commands[cmd]["valid_args"])
                if not states:
                    tags.append("RESIDENCY_STATES_UNRESOLVED")
                    detail += "; states not literal on the line"
                else:
                    bad = [x for x in states if int(x) not in valid]
                    detail += "; raw states " + " ".join(states)
                    if bad:
                        tags.append("SP_ERROR_LOG")
                        detail += " (raw " + " ".join(bad) + " is no state at BL2 0.22.0: 2 SP Runtime Errors each)"
            self.add(path, n, tool, cmd, detail, cond, tags)
        if refused:
            self.notes.append(f"{path}:{n}: " + "; ".join(refused) + " (no reset sent by those)")
        if not sends:
            self.notes.append(f"{path}:{n}: ettelem {sub}: no variant in {vtag} sends anything for it")
        return True

    def dms_token(self, w):
        if "dev_mngt_service" in w:
            return True
        names = re.findall(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)", w) or ([w] if re.fullmatch(r"(?:self\.)?[A-Za-z_]\w*", w) else [])
        return any("dev_mngt_service" in rhs for nm in names for rhs in self.rhs_of(nm.split(".")[-1]))

    def scan_dms(self, path, n, code):
        allw = words(code)
        found = False
        ws, on = [], False
        for w in allw:  # the words of each dev_mngt_service command on the line, nothing else
            if self.dms_token(w):
                on = True
                ws.append("\0")
                continue
            if on and w in ("", "|", "&&", "||", ";"):
                on = False
                ws.append("\0")
            elif on:
                ws.append(w)
        for k, w in enumerate(ws):
            val = None
            if w in ("-o", "--code") and k + 1 < len(ws):
                val = ws[k + 1]
            elif w.startswith("--code="):
                val = w.split("=", 1)[1]
            elif re.fullmatch(r"-o\d+", w):
                val = w[2:]
            if val is not None:
                found = True
                if re.fullmatch(r"\d+", val):
                    name = self.t.by_id.get(int(val))
                    if name:
                        self.add(path, n, "dev_mngt_service -o", name, f"code {val}")
                    else:
                        self.add(path, n, "dev_mngt_service -o", f"CODE_{val}", f"code {val} is in no table entry")
                else:
                    self.add(path, n, "dev_mngt_service -o", "DYNAMIC", f"code from '{val}'")
            tval = None
            if w in ("-t", "--trace") and k + 1 < len(ws):
                tval = ws[k + 1]
            elif w.startswith("--trace="):
                tval = w.split("=", 1)[1]
            if tval is not None:
                found = True
                m = re.fullmatch(r"(SPST|MMST|SP|MM|CM):([a-z_,]+)", tval)
                if not m:
                    self.add(path, n, "dev_mngt_service -t", "DYNAMIC", f"trace operation from '{tval}'")
                    continue
                ttype, ops = m.group(1), m.group(2).split(",")
                for op in ops:
                    if op == "extract":
                        self.add(path, n, "dev_mngt_service -t", "TRACE_EXTRACT", tval)
                    elif op in ("enable", "disable", "reset", "to_uart", "to_memory"):
                        if ttype == "SP":
                            self.add(path, n, "dev_mngt_service -t", "SET_DM_TRACE_RUN_CONTROL", tval)
                        elif ttype in ("SPST", "MMST"):
                            self.add(path, n, "dev_mngt_service -t", "SET_STATS_RUN_CONTROL", tval)
            if w in ("-m", "--command") and k + 1 < len(ws) and not ws[k + 1].startswith("DM_CMD_"):
                found = True
                self.add(path, n, "dev_mngt_service -m", "WRAPPER",
                         f"command from '{ws[k + 1]}': classified at the call sites that name it")
            if w.startswith("--command=") and not w.split("=", 1)[1].startswith("DM_CMD_"):
                found = True
                self.add(path, n, "dev_mngt_service -m", "WRAPPER", f"command from '{w}'")
        return found

    def scan_other(self, path, n, code, lang, handled_ettelem):
        if not OTHER_HINT.search(code):
            return
        masked = strip_quoted(code)  # quoted text blanked: a word inside a message is not a command
        short = code.strip()[:120]
        # the lab's management reset, as a command (shell) or a list element (Python)
        cmdpos = r"(^\s*|[;&|(]\s*|`\s*|\bsudo\s+|\btimeout\s+(-\S+\s+)*\S+\s+|\bexec\s+|\bnice\s+(-n\s*\S+\s+)?)"
        pylist = r"(?<![\w\])])\[\s*[\"']"
        if (lang == "sh" and re.search(cmdpos + r"(/usr/local/bin/)?et-reset(\s|$)", masked) and "--dry-run" not in code) or \
                (lang == "py" and re.search(pylist + r"(sudo[\"']\s*,\s*[\"'])?(/usr/local/bin/)?et-reset[\"']", code)
                 and "--dry-run" not in code):
            self.add(path, n, "et-reset", "RESET_ETSOC", "the lab's management reset")
        sys_w = False
        if lang == "sh":
            sys_w = bool(re.search(r"(>>?|\btee\s+(-a\s+)?)\s*[\"']?/sys/", code))
        elif lang == "py":
            sys_w = bool(re.search(r"open\(\s*[\"']/sys/[^\"']*[\"']\s*,\s*[\"'][wa+]", code)) or \
                ("/sys/" in code and re.search(r"\.write_(text|bytes)\(", code) is not None)
        if sys_w:
            self.add(path, n, "sysfs", "SYSFS_WRITE", short)
        if re.search(r"\bsetpci\b[^|;&]*\s[\w.+:-]+=\S", code):
            self.add(path, n, "setpci", "SETPCI_WRITE", short)
        if (lang == "sh" and re.search(cmdpos + r"(modprobe|rmmod|insmod)\b", masked)) or \
                (lang == "py" and re.search(pylist + r"(sudo[\"']\s*,\s*[\"'])?(modprobe|rmmod|insmod)[\"']", code)):
            self.add(path, n, "kernel module", "MODULE_LOAD", short)
        hb = re.search(cmdpos + r"(reboot|poweroff|shutdown|halt)(\s|$)", masked) if lang == "sh" else None
        if (hb and hb.group(hb.lastindex - 1) not in self.functions) or \
                (lang == "py" and (re.search(pylist + r"(sudo[\"']\s*,\s*[\"'])?(reboot|poweroff|shutdown|halt)[\"']", code)
                                   or re.search(r"os\.system\(\s*[\"'](sudo\s+)?(reboot|poweroff|shutdown|halt)\b", code))) or \
                re.search(r"systemctl\s+(--?[\w-]+\s+)*[\"']?(reboot|poweroff|halt|kexec)\b"
                          r"|[\"']systemctl[\"']\s*,\s*([\"']--?[\w-]+[\"']\s*,\s*)*[\"'](reboot|poweroff|halt|kexec)", code):
            self.add(path, n, "host", "HOST_REBOOT", short)
        if (lang == "sh" and re.search(r"(^|[\s;&|(/])etcfg(\s|$)", masked)) or \
                (lang == "py" and re.search(r"[\"'][^\"']*/etcfg[\"']", code)):
            self.add(path, n, "etcfg", "ETCFG", "a read-only driver ioctl")
        # a reset option passed on to a sampler wrapper (start_sampler ... --reset-ms R) on a line that is not itself
        # an ettelem call: the wrapper forwards it, so the reset is sent
        if not handled_ettelem and not (lang == "sh" and re.match(r"\s*(grep|egrep|rg|sed|awk|echo|printf)\b", code)):
            # in shell a quoted option is a value (a grep pattern, a message), not an option passed on
            ws = words(masked) if lang == "sh" else words(code)
            for k, w in enumerate(ws):
                if w in ("--reset-ms", "--reset-once-file"):
                    val = ws[k + 1] if k + 1 < len(ws) else ""
                    if not (w == "--reset-ms" and val == "0"):
                        self.add(path, n, "reset option passed on", "SET_STATS_RUN_CONTROL",
                                 f"{w} {val}: a sampler wrapper forwards it", True)
                        break

    def scan_raw_client(self, path, text, lines):
        if "PUSH_SQ" not in text:
            return
        consts = []
        for n, code in lines:
            m = re.match(r"\s*([A-Z_][A-Z0-9_]*(?:\s*,\s*[A-Z_][A-Z0-9_]*)*)\s*=\s*([0-9][0-9,\s]*)$", code)
            if not m:
                continue
            names = [x.strip() for x in m.group(1).split(",")]
            vals = [x.strip() for x in m.group(2).split(",") if x.strip()]
            if len(names) != len(vals):
                continue
            for name, val in zip(names, vals):
                base = re.sub(r"^(DM_CMD_|CMD_)", "", name)
                if name.startswith("CMD_") or base in self.t.commands:
                    consts.append((n, name, int(val)))
        if not consts:
            self.add(path, 1, "raw ioctl client", "DYNAMIC", "pushes management messages with PUSH_SQ; no command constants found")
            return
        for n, name, val in consts:
            cmd = self.t.by_id.get(val, f"CODE_{val}")
            self.add(path, n, "raw ioctl client", cmd, f"{name} = {val}")

    def scan_file(self, path, lang, text, lines):
        self.cur = str(path)
        sha = hashlib.sha256(text.encode()).hexdigest()
        if sha in self.t.reviewed:
            kind, key, info = self.t.reviewed[sha]
            if kind == "variant":
                for sub, sc in info["subcommands"].items():
                    for cmd in sc["sends"] + sc.get("reset_sends", []):
                        self.add(path, 0, f"{key} {sub} (reviewed source)", cmd, f"lines {sc.get('lines', '?')}",
                                 cmd in sc.get("reset_sends", []))
            else:
                for cmd in info["sends"]:
                    self.add(path, 0, "raw ioctl client (reviewed source)", cmd, f"lines {info.get('lines', '?')}")
            self.notes.append(f"{path}: reviewed source (sha256 {sha[:12]}), taken from the table")
            return
        file_refs_ettelem = bool(re.search(r"ettelem", text))
        self.scan_raw_client(path, text, lines)
        for n, code in lines:
            if not code.strip():
                continue
            for m in DM_TOKEN_RE.finditer(code):
                tok, nxt = m.group(0), code[m.end():m.end() + 1]
                name = tok[len("DM_CMD_"):]
                if not name or tok.endswith("_") or nxt in ("{", "$", "%"):
                    self.add(path, n, "name", "DYNAMIC", "a command name built at run time: '"
                             + code[m.start():m.end() + 16].strip() + "'")
                else:
                    self.add(path, n, "name", name)
            if self.is_dms_line(code):
                self.scan_dms(path, n, code)
            handled = False
            if file_refs_ettelem or self.is_ettelem_line(code):
                handled = self.scan_ettelem(path, n, code, file_refs_ettelem)
            self.scan_other(path, n, code, lang, handled)

    def run(self):
        texts = {}
        own = {HERE / "dmcmd_audit.py", HERE / "test_dmcmd_audit.py"}
        for p in self.files:
            if p.resolve() in own:  # the audit's own code and fixtures name every command; they send none
                self.notes.append(f"{p}: the audit's own code, not scanned")
                continue
            try:
                text = p.read_text(errors="replace")
            except OSError as e:
                self.notes.append(f"{p}: unreadable ({e})")
                continue
            lang = lang_of(p, text)
            if lang is None:
                self.notes.append(f"{p}: not code (documentation), not scanned")
                continue
            texts[p] = (lang, text, list(logical_lines(text, lang)))
        self.cur = None
        self.collect_assignments(texts)
        for p, (lang, text, lines) in texts.items():
            self.scan_file(p, lang, text, lines)
        self.dedupe()
        return self

    def dedupe(self):
        seen, out = set(), []
        for r in self.records:
            k = (r["file"], r["line"], r["command"], r["tool"], tuple(r["tags"]))
            if k in seen:
                continue
            seen.add(k)
            out.append(r)
        # a line that names DM_CMD_X and is also matched as an ettelem/dev_mngt_service send keeps both: they agree
        self.records = out

    # ---- the verdict -------------------------------------------------------------------------------------------------
    def judge(self, allow, deny_pmic_read, excepts=None):
        """excepts: {(file, line): {name: reason}}, reviewed exceptions for code a run never executes as written."""
        excepts = excepts or {}
        nogo = []
        for r in self.records:
            cmd = r["command"]
            if cmd == "WRAPPER":
                r.update(cls="WRAPPER", pmic="-", verdict="CHECK (a person reads the wrapper)")
                continue
            e = self.t.entry(cmd)
            if e is None:
                r.update(cls="UNCLASSIFIED", pmic="unknown")
            else:
                r.update(cls=e["class"], pmic=e.get("pmic", "none"))
            reasons = []
            if r["cls"] == "WRITE" and cmd not in allow:
                reasons.append("WRITE not in the allow-list")
            if r["cls"] in ("UNSUPPORTED", "UNCLASSIFIED") and cmd not in allow:
                reasons.append(r["cls"])
            if r["cls"] == "READ" and deny_pmic_read and r["pmic"] == "read" and cmd not in allow:
                reasons.append("PMIC read denied (--deny-pmic-read)")
            for tag in r["tags"]:
                if tag not in allow:
                    reasons.append(tag)
            waived = excepts.get((os.path.normpath(r["file"]), r["line"]), {})
            kept = [x for x in reasons if not ((cmd in waived and x.startswith(("WRITE", "UNSUPPORTED", "UNCLASSIFIED",
                                                                                     "PMIC read"))) or x in waived)]
            if kept != reasons:
                r["excepted"] = {k: v for k, v in waived.items()}
                reasons = kept
            if reasons:
                r["verdict"] = "NO-GO: " + ", ".join(reasons)
                nogo.append(r)
            elif r.get("excepted"):
                r["verdict"] = "EXCEPTED: " + "; ".join(f"{k}: {v}" for k, v in r["excepted"].items())
            elif r["cls"] == "WRITE":
                r["verdict"] = "ALLOWED WRITE"
            else:
                r["verdict"] = "ok"
        return nogo


def expand(paths):
    out = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            for q in sorted(p.rglob("*")):
                if q.is_file() and "__pycache__" not in q.parts and (q.suffix.lower() in CODE_EXT or q.suffix == ""):
                    out.append(q)
        elif p.is_file():
            out.append(p)
        else:
            raise FileNotFoundError(str(p))
    return out


def shown(path):
    """A path as a reader of a public record should see it: relative to the working directory when under it."""
    rel = os.path.relpath(str(path))
    return path.name if rel.startswith("..") else rel


def summarize(records):
    summ = {}
    for r in records:
        s = summ.setdefault(r["command"], {"class": r["cls"], "pmic": r["pmic"], "sites": 0, "verdicts": set()})
        s["sites"] += 1
        s["verdicts"].add(r["verdict"].split(":")[0])
    return summ


def markdown(audit, nogo, allow, args):
    lines = ["## Device commands sent", "",
             f"Checked with `tools/claims-v3/dmcmd_audit.py` against `{audit.t.path.name}` (et-platform "
             f"`{audit.t.raw['source']['commit'][:7]}`, BL2 {audit.t.raw['source']['bl2_version'].split()[0]}); "
             f"allow-list: {', '.join(sorted(allow)) or 'none'}{'; PMIC reads denied' if args.deny_pmic_read else ''}. "
             f"Verdict: **{'NO-GO' if nogo else 'GO'}**.", "",
             "| Command | Class | PMIC | Sites | Verdict |", "|---|---|---|---|---|"]
    for cmd, s in sorted(summarize(audit.records).items(), key=lambda kv: (kv[1]["class"] != "WRITE", kv[0])):
        lines.append(f"| `{cmd}` | {s['class']} | {s['pmic']} | {s['sites']} | {', '.join(sorted(s['verdicts']))} |")
    lines.append("")
    for r in nogo:
        lines.append(f"- NO-GO `{r['file']}:{r['line']}` {r['tool']} `{r['command']}`: {r['verdict'][7:]} ({r['detail']})")
    for r in audit.records:
        if r.get("excepted") and r["verdict"].startswith("EXCEPTED"):
            lines.append(f"- Excepted after review `{r['file']}:{r['line']}` `{r['command']}`: {r['verdict'][10:]}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="the runner's files or directories")
    ap.add_argument("--table", default=str(DEFAULT_TABLE), help="the audit table (default: beside this script)")
    ap.add_argument("--allow", action="append", default=[], help="allowed WRITE or tag names (repeatable, comma-separated)")
    ap.add_argument("--deny-pmic-read", action="store_true", help="treat PMIC register reads as NO-GO too")
    ap.add_argument("--except", dest="excepts", action="append", default=[], metavar="FILE:LINE:NAME=REASON",
                    help="a reviewed exception: waive NAME (a command or a tag) on that one line, for code the run never "
                         "executes as written (patched at run time, unreachable); the reason is printed with the verdict")
    ap.add_argument("--json", action="store_true", help="print the records and the verdict as JSON")
    ap.add_argument("--markdown", action="store_true", help="print a 'Device commands sent' section for a README")
    ap.add_argument("--table-only", "--table-summary", dest="table_only", action="store_true", help="print the table and exit")
    ap.add_argument("-q", "--quiet", action="store_true", help="print only the verdict and the NO-GO lines")
    args = ap.parse_args(argv)
    try:
        table = Table(args.table)
    except (OSError, ValueError, KeyError) as e:
        print(f"dmcmd_audit: cannot read the table {args.table}: {e}", file=sys.stderr)
        return EXIT_USAGE
    if args.table_only:
        for name, c in sorted(table.commands.items(), key=lambda kv: kv[1]["id"]):
            print(f"{c['id']:>3} {name:<42} {c['class']:<12} pmic={c.get('pmic', 'none'):<7} {c['handler'][:90]}")
        return EXIT_GO
    if not args.files:
        ap.print_usage(sys.stderr)
        return EXIT_USAGE
    allow = set()
    for a in args.allow:
        for x in a.split(","):
            x = x.strip()
            if x:
                allow.add(x[len("DM_CMD_"):] if x.startswith("DM_CMD_") else x)
    unknown = [a for a in allow if a not in table.commands and a not in table.pseudo and
               a not in ("SP_ERROR_LOG", "RESIDENCY_STATES_UNRESOLVED")]
    if unknown:
        print(f"dmcmd_audit: --allow names not in the table: {', '.join(sorted(unknown))}", file=sys.stderr)
        return EXIT_USAGE
    excepts = {}
    for e in args.excepts:
        m = re.fullmatch(r"(.+):(\d+):([A-Z0-9_]+)=(.+)", e)
        if not m:
            print(f"dmcmd_audit: --except wants FILE:LINE:NAME=REASON, got '{e}'", file=sys.stderr)
            return EXIT_USAGE
        name = m.group(3)[len("DM_CMD_"):] if m.group(3).startswith("DM_CMD_") else m.group(3)
        excepts.setdefault((os.path.normpath(m.group(1)), int(m.group(2))), {})[name] = m.group(4).strip()
    try:
        files = expand(args.files)
    except FileNotFoundError as e:
        print(f"dmcmd_audit: no such file: {e}", file=sys.stderr)
        return EXIT_USAGE
    audit = Audit(table, files).run()
    nogo = audit.judge(allow, args.deny_pmic_read, excepts)
    verdict = "NO-GO" if nogo else "GO"
    if args.json:
        summ = {k: {**v, "verdicts": sorted(v["verdicts"])} for k, v in summarize(audit.records).items()}
        print(json.dumps({"verdict": verdict, "allow": sorted(allow), "deny_pmic_read": args.deny_pmic_read,
                          "excepts": [f"{f}:{l}:{k}={v}" for (f, l), d in sorted(excepts.items()) for k, v in d.items()],
                          "table": shown(table.path), "table_commit": table.raw["source"]["commit"],
                          "files": [str(f) for f in files], "summary": summ, "records": audit.records,
                          "notes": audit.notes}, indent=1))
    elif args.markdown:
        print(markdown(audit, nogo, allow, args))
    else:
        if not args.quiet:
            for r in audit.records:
                cond = " (conditional)" if r["conditional"] else ""
                print(f"{r['file']}:{r['line']}: {r['tool']}: {r['command']} [{r['cls']}, pmic {r['pmic']}]{cond}"
                      f" {r['verdict']}{' - ' + r['detail'] if r['detail'] else ''}")
            for note in audit.notes:
                print("note: " + note)
            print("summary:")
            for cmd, s in sorted(summarize(audit.records).items()):
                print(f"  {cmd:<42} {s['class']:<12} pmic {s['pmic']:<7} {s['sites']:>3} site(s)  "
                      f"{', '.join(sorted(s['verdicts']))}")
        for r in nogo:
            print(f"NO-GO {r['file']}:{r['line']}: {r['tool']}: {r['command']}: {r['verdict'][7:]}", file=sys.stderr)
        print(f"dmcmd_audit: {verdict} ({len(audit.records)} send site(s), {len(nogo)} disallowed; "
              f"allow-list: {', '.join(sorted(allow)) or 'none'})", file=sys.stderr)
    return EXIT_NOGO if nogo else EXIT_GO


if __name__ == "__main__":
    sys.exit(main())
