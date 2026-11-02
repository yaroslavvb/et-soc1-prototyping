#!/usr/bin/env python3
"""dmcmd_audit: the preflight check of the device-management commands a runner's files can send (Q136(w), 2 Nov 2026).

A runner calls it on its own files (harness, sampler wrappers, helpers) before its first launch:

    python3 tools/claims-v3/dmcmd_audit.py --allow STATS_RESET tools/claims-v3/eNNN/ tools/claims-v3/lib.sh

It lists every place in those files that can send a command to a card's service processor, classifies each one READ
or WRITE from the audit table (tools/claims-v3/dmcmd_table.json: et-platform 836a4ab, BL2 0.22.0, classified from the
firmware source), and exits 3 (NO-GO) on any of:

  * a WRITE whose name is not in the caller's allow-list (--allow NAME, repeatable or comma-separated; names without
    the DM_CMD_ prefix; pseudo names SYSFS_WRITE, SETPCI_WRITE, MODULE_LOAD, HOST_REBOOT). DM_CMD_SET_STATS_RUN_CONTROL
    is named by its form, because its forms write different things: STATS_RESET is the statistics reset the owner
    ruled on (31 Oct 2026: type 1, control 2, as every reviewed ettelem variant's --reset-ms and --reset-once-file send
    it); SPST_TRACE_CONTROL, SPST_RESET and MMST_CONTROL are dev_mngt_service -t SPST:/MMST: control operations; a bare
    SET_STATS_RUN_CONTROL is a send whose form the checker cannot see (a DM_CMD_ name, -o 62, a raw client's 62), never
    allowed. --allow SET_STATS_RUN_CONTROL is read as STATS_RESET (and says so);
  * a command the table marks UNSUPPORTED or UNCLASSIFIED, a DM_CMD_ name the table does not know, or a command named
    at run time (DYNAMIC), unless allowed by name;
  * an ettelem call whose meaning is not in the table: a binary outside every reviewed build directory
    (UNREVIEWED_VARIANT), a binary the checker cannot resolve to one (VARIANT_UNRESOLVED: a variable set outside the
    scanned files, a program that is not among them), or a subcommand the matched variant does not have
    (UNKNOWN_SUBCOMMAND). These are never cleared by --allow: --variant-source KEY=SOURCE names the source file a
    binary was built from (KEY: its build directory or program name, or 'unresolved' for every binary the checker
    cannot resolve), and is taken only when the SOURCE's SHA-256 equals a reviewed variant's; else a person reads the
    line and records a reviewed --except;
  * a read with a blocking side effect: a residency read of a raw state the firmware does not have (SP_ERROR_LOG: two
    SP Runtime Errors a read, E77 F1), or residency states the checker cannot see (RESIDENCY_STATES_UNRESOLVED);
  * with --deny-pmic-read, any read that reaches the PMIC (GET_ASIC_VOLTAGE, GET_MODULE_VOLTAGE).

Exit 0 = GO (nothing disallowed), 3 = NO-GO, 2 = usage error. --json prints the records; --markdown prints a "Device
commands sent" section for the run's README; --table-only prints the table.

What it finds, and what it cannot. It reads source text, line by line (shell continuation lines and Python/JS brackets
joined), skipping comments and Python docstrings. It finds DM_CMD_ names; dev_mngt_service's -o codes and -t trace
operations; every ettelem call on a line, its binary resolved through the table's reviewed build directories (from
the path on the line, the variable that holds it, a file the script sources, or the binaries the file names) and its
subcommand looked up in that variant's reviewed table; the statistics reset (--reset-ms, --reset-once-file, or
arguments forwarded with "$@" / *args, which might carry one); wrappers that forward their arguments to ettelem (a
shell function or a Python def), whose call sites in the same file are classified through them; raw ioctl clients'
numeric codes; et-reset, sysfs and setpci writes, module loads and reboots. A file whose SHA-256 matches a reviewed
source in the table (the five ettelem variants, the raw clients) is taken from the table instead of being scanned, and
a call through a program that is among the scanned files (a guard script, say) is classified at that program's own
lines. It cannot follow a command assembled across files, a wrapper defined in one file and called from another, or a
binary chosen at run time: a forwarded subcommand is listed as a WRAPPER line for a person to read, and an unresolved
binary is NO-GO. It errs toward NO-GO: a false NO-GO is cleared by reading the line (--except with the reason, or
--variant-source), never by widening --allow.
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
BASE_SUBCOMMANDS = ("sample", "config", "temp", "loglevel", "sptrace", "residency", "uptime", "threshold", "profile")
CODE_EXT = {".sh": "sh", ".bash": "sh", ".py": "py", ".mjs": "js", ".js": "js", ".c": "c", ".cc": "c", ".cpp": "c",
            ".h": "c", ".hpp": "c"}
DOC_EXT = {".md", ".txt", ".rst", ".html", ".csv", ".jsonl", ".log", ".json", ".yaml", ".yml", ".toml"}
DM_TOKEN_RE = re.compile(r"\bDM_CMD_[A-Z0-9_]*")
FORWARD_RE = re.compile(r'"\$@"|"\$\{@\}"|\$\*|\$@|\*args|\*argv|\*rest|\*extra|\*a\b')
# a word that passes a caller's arguments on: "$@", "$*", "${@:2}", *args, *a ...
FORWARD_TOK = re.compile(r"\$@|\$\{@(:\d+)?\}|\$\*|\$\{\*\}|\*[A-Za-z_][\w.]*(\[[^\]]*\])?")
BIN_DIR_RE = re.compile(r"([\w.-]+)/ettelem(?![\w./-])")  # a path to a binary named ettelem; group 1 = its directory
SUBWORD_RE = re.compile(r"[a-z][a-z0-9_-]{0,23}")  # what a subcommand looks like
NOT_A_PROGRAM = re.compile(r"\.(cpp|cc|c|h|hpp|o|a|so|md|json|jsonl|txt|log|err|out|bin|csv|sha256|raw|tgz|gz|html|py)$")
OTHER_HINT = re.compile(r"et-reset|/sys/|setpci|modprobe|rmmod|insmod|reboot|poweroff|shutdown|halt|systemctl|etcfg"
                        r"|--reset-ms|--reset-once-file")
NOT_WRAPPERS = {"print", "get", "pop", "setdefault", "join", "startswith", "endswith", "split", "replace", "find",
                "index", "count", "append", "extend", "format", "load", "loads", "dump", "dumps", "open", "Path",
                "add", "remove", "discard", "update", "getattr", "hasattr", "isinstance", "str", "int", "float",
                "len", "sorted", "list", "dict", "set", "tuple", "log", "note", "warn", "fail", "abort", "die",
                "error", "info", "debug", "write", "match", "search", "fullmatch", "sub", "compile", "exists",
                "mark", "echo", "printf", "jl", "load_jsonl", "read_jsonl"}
# the word before a binary's path when the line handles the file rather than running it
NONEXEC = {"ls", "test", "[", "[[", "-x", "-f", "-e", "-s", "-L", "-r", "-w", "-d", "-n", "-z", "!", "sha256sum",
           "shasum", "md5sum", "file", "stat", "cp", "mv", "rm", "ln", "rsync", "scp", "cmake", "make", "chmod", "chown",
           "strings", "grep", "egrep", "fgrep", "readlink", "realpath", "basename", "dirname", "cat", "head", "tail",
           "ldd", "nm", "objdump", "du", "touch", "which", "type", "install", "tar", "mkdir", "open", "isfile",
           "exists", "isdir", "islink", "access", "getsize", "getmtime", "lstat", "sha256", "sha256_of",
           "sha256_file", "file_sha256", "sha", "hash_file", "read_bytes", "read_text", "-B", "-S", "--build", "-o",
           "--output", "echo", "printf", "print", "log", "die", "fail", "warn", "note", "info", "abspath", "relpath",
           "expanduser", "-v", "command", "hash", "unlink", "copy", "copy2", "copyfile", "move", "which_", "=="}
CMD_START = {";", "&&", "||", "|", "then", "do", "else", "elif", "if", "while", "until", "{", "!", "exec", "time",
             "sudo", "nohup", "setsid", "env", "nice", "ionice", "stdbuf", "timeout", "flock", "$(", "$"}
PY_KEYWORDS = {"in", "and", "or", "if", "else", "for", "not", "is", "None", "True", "False", "lambda", "return"}
FORM_ALIAS = {"SET_STATS_RUN_CONTROL": "STATS_RESET"}
NEVER_ALLOW = ("UNREVIEWED_VARIANT", "VARIANT_UNRESOLVED", "UNKNOWN_SUBCOMMAND")
TAG_NAMES = ("SP_ERROR_LOG", "RESIDENCY_STATES_UNRESOLVED")


class Table:
    def __init__(self, path):
        self.path = Path(path)
        self.raw = json.loads(self.path.read_text())
        self.commands = self.raw["commands"]
        self.forms = self.raw.get("forms", {})
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
        self.dir_variant = {}  # the name of a reviewed build directory -> the variant built into it
        for v, info in self.variants.items():
            for bd in info.get("build_dirs", []):
                self.dir_variant[bd.rstrip("/").split("/")[-1]] = v
        self.src_variant = {info["sha256"]: v for v, info in self.variants.items()}
        self.subcommands = set(BASE_SUBCOMMANDS) | {s for i in self.variants.values() for s in i["subcommands"]}

    def entry(self, name):
        for d in (self.commands, self.forms, self.pseudo):
            if name in d:
                return d[name]
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


def functions_at(text, lang):
    """For each physical line (1-based), the shell function or Python def it sits in, or None."""
    lines = text.split("\n")
    at = [None] * (len(lines) + 2)
    if lang == "sh":
        cur = None
        for n, raw in enumerate(lines, 1):
            m = re.match(r"\s*(?:function\s+)?([A-Za-z_][\w-]*)\s*\(\)\s*\{?(.*)$", raw)
            if m:
                cur = m.group(1)
                at[n] = cur
                if re.search(r"\}\s*(#.*)?$", m.group(2)) and m.group(2).count("{") <= m.group(2).count("}"):
                    cur = None  # a one-line function
                continue
            at[n] = cur
            if cur and re.match(r"\}\s*(#.*)?$", raw):
                cur = None
    elif lang == "py":
        stack = []
        for n, raw in enumerate(lines, 1):
            if raw.strip() and not raw.lstrip().startswith("#"):
                ind = len(raw) - len(raw.lstrip())
                while stack and ind <= stack[-1][0] and not raw.lstrip().startswith((")", "]", "}")):
                    stack.pop()
                m = re.match(r"(\s*)(?:async\s+)?def\s+(\w+)\s*\(", raw)
                if m:
                    stack.append((len(m.group(1)), m.group(2)))
            at[n] = stack[-1][1] if stack else None
    return at


def plain_tokens(s):
    """Tokens with quotes as separators too: a command inside a quoted string still splits into its words."""
    return [t.rstrip(";&|") for t in re.findall(r"[^\s,()\[\]'\"]+", s)]


_QTOK = re.compile(r'"((?:\\.|[^"\\\n])*)"|\'((?:\\.|[^\'\\\n])*)\'|([^\s,()\[\]\'"]+)')


def qtokens(s):
    """plain_tokens' words, each with how it was quoted: '' (bare), 'w' (a whole quoted string), 'p' (a word inside a
    longer quoted string, such as a message or a command line kept in a variable); and the last character before it
    that is not a space (for a Python list element, '[' or ',')."""
    out = []
    for m in _QTOK.finditer(s):
        before = s[:m.start()].rstrip()
        pre = before[-1] if before else ""
        if m.group(3) is not None:
            t = m.group(3).rstrip(";&|")
            out.append((t if t else m.group(3), "", pre))
            continue
        inner = m.group(1) if m.group(1) is not None else m.group(2)
        parts = re.findall(r"[^\s,()\[\]'\"]+", inner)
        if len(parts) == 1 and parts[0] == inner.strip():
            out.append((parts[0].rstrip(";&|") or parts[0], "w", pre))
        else:
            out.extend(((p.rstrip(";&|") or p), "p", "") for p in parts)
    return out


def words(s):
    """Tokens of a command line, quotes removed (shell words or Python/JS string items)."""
    return [t.strip("\"'").rstrip(";&|") for t in re.findall(r'"[^"]*"|\'[^\']*\'|[^\s,()\[\]]+', s)]


def source_key(key):
    """A --variant-source key, reduced to what binary paths are matched by: the build directory's name, or a
    program's name, or 'unresolved'."""
    k = key.strip().rstrip("/")
    if k == "unresolved":
        return k
    if k.endswith("/ettelem"):
        k = k[: -len("/ettelem")]
    return k.split("/")[-1]


class Res:
    """What an ettelem call's binary resolves to."""

    def __init__(self):
        self.variants = set()     # reviewed variants it may be
        self.unreviewed = []      # binary paths or programs in no reviewed build directory
        self.unresolved = False   # the checker cannot see which binary it is
        self.program = None       # a scanned program it calls (its own lines are classified)
        self.how = ""


class Audit:
    def __init__(self, table, files, bindings=None):
        self.t = table
        self.files = files
        self.records = []
        self.notes = []
        self.assign = {}  # variable name -> right-hand sides that name a device tool, from all scanned files
        self.file_assign = {}  # (file, name) -> the same, for the file that assigns it
        self.functions = set()  # shell function names defined in the scanned files
        self.bindings = bindings or {}  # --variant-source: key -> variant (None when its source matched no variant)
        self.sources = {}  # file -> the scanned files it sources (shell), in order
        self.programs = {}  # name of a scanned file -> its path
        self.file_dirs = {}  # file -> the build directories of the ettelem binaries its code names
        self.wrappers = {}  # (file, function) or (program name, None) -> (binary token, its quoting, the line)
        self.wrapper_calls = {}  # (file, function) -> number of call sites classified through it
        self.cur = None

    def add(self, path, line, tool, command, detail="", conditional=False, tags=()):
        self.records.append({"file": str(path), "line": line, "tool": tool, "command": command, "detail": detail,
                             "conditional": conditional, "tags": list(tags)})

    # ---- variables that hold an ettelem binary or dev_mngt_service -------------------------------------------------
    def collect_assignments(self, texts):
        rx = re.compile(r"(?:^|[\s;(])(?:export\s+|local\s+|readonly\s+|declare\s+(?:-\w+\s+)*)?"
                        r"(?:[A-Za-z_]\w*\.)?([A-Za-z_][A-Za-z0-9_]*)\s*:?=(?!=)\s*(.+)")
        for path, (lang, text, lines) in texts.items():
            if lang == "sh":
                self.functions |= set(re.findall(r"(?m)^\s*(?:function\s+)?([A-Za-z_][\w-]*)\s*\(\)", text))
            for _, code in lines:
                for m in BIN_DIR_RE.finditer(code):
                    self.file_dirs.setdefault(str(path), set()).add(m.group(1))
                if "ettelem" not in code and "dev_mngt_service" not in code:
                    continue
                for m in rx.finditer(code):
                    name, rhs = m.group(1), m.group(2)
                    if lang == "sh":  # VAR=value cmd ...: the value ends at the first unquoted space
                        mv = re.match(r"(?:\"[^\"]*\"|'[^']*'|\$\{[^}]*\}|\$\([^)]*\)|[^\s;&|])+", rhs)
                        rhs = mv.group(0) if mv else rhs
                    if "ettelem" in rhs or "dev_mngt_service" in rhs:
                        self.assign.setdefault(name, []).append(rhs)
                        self.file_assign.setdefault((str(path), name), []).append(rhs)
                for m in re.finditer(r"\$\{([A-Za-z_][A-Za-z0-9_]*):-([^}]*)\}", code):  # ${VAR:-default}
                    if "ettelem" in m.group(2) or "dev_mngt_service" in m.group(2):
                        self.assign.setdefault(m.group(1), []).append(m.group(2))
                        self.file_assign.setdefault((str(path), m.group(1)), []).append(m.group(2))

    def collect_sources(self, texts):
        """Which scanned files each shell file sources (. FILE / source FILE), so its variables resolve from there."""
        norm = {os.path.normpath(str(p)): str(p) for p in texts}
        by_name = {}
        for p in texts:
            by_name.setdefault(Path(p).name, []).append(str(p))
        for path, (lang, text, lines) in texts.items():
            if lang != "sh":
                continue
            here = os.path.dirname(str(path))
            for _, code in lines:
                m = re.match(r"\s*(?:\.|source)\s+(.+?)\s*(?:;|&&|\|\||$)", code)
                if not m:
                    continue
                arg = m.group(1).replace('"', "").replace("'", "").strip()
                arg = re.sub(r"^\$\(dirname\s+\$\{?(BASH_SOURCE(\[0\])?|0)\}?\)", here or ".", arg)
                cands = [arg]
                mv = re.match(r"\$\{?[A-Za-z_]\w*\}?/(.+)", arg)
                if mv:
                    cands = [mv.group(1), os.path.join(here, mv.group(1))]
                hit = None
                for c in cands:
                    c = os.path.normpath(c)
                    if c in norm:
                        hit = norm[c]
                        break
                if hit is None:
                    same = [q for q in by_name.get(os.path.basename(arg), []) if os.path.dirname(q) == here]
                    allq = by_name.get(os.path.basename(arg), [])
                    hit = same[0] if same else (allq[0] if len(allq) == 1 else None)
                if hit and hit != str(path):
                    self.sources.setdefault(str(path), []).append(hit)

    def rhs_of(self, name):
        """What a variable can hold: the current file's assignments, else those of the last file it sources that
        assigns it, else (for a tool-like name only) any file's."""
        own = self.file_assign.get((self.cur, name))
        if own:
            return own
        seen, todo, found = set(), list(self.sources.get(self.cur, [])), None
        while todo:
            f = todo.pop(0)
            if f in seen:
                continue
            seen.add(f)
            if (f, name) in self.file_assign:
                found = self.file_assign[(f, name)]
            todo.extend(self.sources.get(f, []))
        if found:
            return found
        if name in self.assign and len(name) >= 3 and (name.isupper() or re.search(r"(?i)ett|dms|mngt|devm|tel", name)):
            return self.assign[name]
        return []

    def var_refs(self, code):
        names = set(re.findall(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)", code))
        names |= set(re.findall(r"(?:[A-Za-z_]\w*\.)?\b([A-Za-z_][A-Za-z0-9_]*)\b", code))
        return [n for n in names if self.rhs_of(n)]

    def is_ettelem_line(self, code):
        if re.search(r"ettelem", code):
            return True
        return any("ettelem" in rhs for n in self.var_refs(code) for rhs in self.rhs_of(n))

    def is_dms_line(self, code):
        if "dev_mngt_service" in code:
            return True
        return any("dev_mngt_service" in rhs for n in self.var_refs(code) for rhs in self.rhs_of(n))

    # ---- which binary an ettelem call runs ---------------------------------------------------------------------------
    def binary_kind(self, tok, file_refs_ettelem, lang="sh", q=""):
        """'path' (a path to a binary named ettelem), 'bare' (the word ettelem), 'name' (a reviewed build directory's
        name), 'var' (a variable that holds an ettelem binary), 'program' (a program with ettelem in its name, such
        as a guard script), 'anyvar' (a shell variable in a file that runs ettelem: the binary unknown), or None."""
        placeholder = re.fullmatch(r"\{([^{}!:]+)(![rsa])?(:[^{}]*)?\}", tok)  # an f-string's {self.ettelem!r}
        t = placeholder.group(1).strip() if placeholder else tok.strip("{}").lstrip("`")
        if placeholder:
            q = ""  # an expression, though it sits inside a string
        if t == "ettelem":
            return "bare"
        if t.endswith("/ettelem"):
            return "path"
        if t in self.t.dir_variant:
            return "name"
        if t.endswith("/") or t.rsplit("/", 1)[-1] in self.t.dir_variant:
            return None  # a build directory, not a binary
        m = re.fullmatch(r"\$\{?([A-Za-z_]\w*)(?::?[-=+?][^}]*)?\}?|(?:[A-Za-z_]\w*\.)?([A-Za-z_]\w*)", t)
        if m and m.group(2) and (lang == "sh" or q):
            m = None  # a bare word in shell, or a quoted string in Python, is a literal, not a variable
        if m:
            name = m.group(1) or m.group(2)
            if re.search(r"(?i)ettelem", name) or re.fullmatch(r"(?i)(\w+_)?ett(_\w+)?", name) or \
                    any(self.names_binary(rhs) for rhs in self.rhs_of(name)):
                return "var"
            if m.group(1) and "ettelem" in t:
                return "var"
            if file_refs_ettelem and m.group(1):
                return "anyvar"
            return None
        base = t.rsplit("/", 1)[-1]
        if "ettelem" in base and not NOT_A_PROGRAM.search(base) and not base.startswith(("$", "-")) and \
                ("/" in t or base.endswith(".sh")):
            return "program"  # a script or binary with ettelem in its name, run by path (a guard, a stub)
        return None

    def names_binary(self, s):
        """Does this text name an ettelem binary (a path ending in /ettelem) or a program with ettelem in its name?
        (A regex or a message that only contains the word does not.)"""
        if BIN_DIR_RE.search(s):
            return True
        for p in re.findall(r"[\w.${}~:/-]*ettelem[\w.-]*", s):
            base = p.rsplit("/", 1)[-1]
            if base != "ettelem" and not NOT_A_PROGRAM.search(base) and not base.startswith("$") and "/" in p:
                return True
        return False

    def resolve(self, tok, kind, path):
        r = Res()
        placeholder = re.fullmatch(r"\{([^{}!:]+)(![rsa])?(:[^{}]*)?\}", tok)
        t = placeholder.group(1).strip() if placeholder else tok.strip("{}").lstrip("`")
        if kind == "name":
            r.variants.add(self.t.dir_variant[t])
            r.how = f"the build directory named {t}"
            return r
        srcs = []
        if kind == "path":
            srcs = [t]
        elif kind == "var":
            m = re.fullmatch(r"\$\{?([A-Za-z_]\w*)(?::?[-=+?][^}]*)?\}?|(?:[A-Za-z_]\w*\.)?([A-Za-z_]\w*)", t)
            name = (m.group(1) or m.group(2)) if m else t
            srcs = list(self.rhs_of(name))
            if t.startswith("$"):  # ${X:-default}: the default is a value too; the variable's own name is not
                srcs.append(re.sub(r"^\$\{?[A-Za-z_]\w*", "", t))
        elif kind == "program":
            srcs = [t]
        dirs, progs = [], []
        for s in srcs:
            for m in BIN_DIR_RE.finditer(s):
                if m.group(1) not in dirs:
                    dirs.append(m.group(1))
            for p in re.findall(r"[\w.${}~:/-]*ettelem[\w.-]*", s):
                base = p.rsplit("/", 1)[-1]
                if base != "ettelem" and not NOT_A_PROGRAM.search(base) and not base.startswith("$") \
                        and base not in self.t.dir_variant and base not in progs and not p.endswith("/"):
                    progs.append(base)
        if kind == "bare":
            dirs = sorted(self.file_dirs.get(str(path), set()))
            r.how = "the word ettelem: the binaries its file names" if dirs else "the word ettelem"
        for d in dirs:
            if d in self.bindings:
                if self.bindings[d]:
                    r.variants.add(self.bindings[d])
                else:
                    r.unreviewed.append(d + "/ettelem (its --variant-source matches no reviewed variant)")
            elif d in self.t.dir_variant:
                r.variants.add(self.t.dir_variant[d])
            else:
                r.unreviewed.append(d + "/ettelem")
        for p in progs:
            if p in self.bindings:
                if self.bindings[p]:
                    r.variants.add(self.bindings[p])
                else:
                    r.unreviewed.append(p + " (its --variant-source matches no reviewed variant)")
            elif p in self.programs:
                if (p, None) in self.wrappers:  # a scanned program that forwards its arguments to ettelem
                    btok, bkind, _ = self.wrappers[(p, None)]
                    sub = self.resolve(btok, bkind, self.programs[p])
                    r.variants |= sub.variants
                    r.unreviewed += sub.unreviewed
                    r.unresolved = r.unresolved or sub.unresolved
                else:
                    r.program = self.programs[p]
            else:
                r.unresolved = True
                r.how = f"the program {p}, not among the scanned files"
        if not dirs and not progs:
            r.unresolved = True
            r.how = r.how or f"'{tok}': no binary path the checker can see"
        if r.unresolved and "unresolved" in self.bindings:
            v = self.bindings["unresolved"]
            if v:
                r.variants.add(v)
                r.unresolved = False
                r.how += f" (--variant-source unresolved: {v})"
        return r

    def nonexec(self, toks, i, lang=""):
        """Is the binary at toks[i] handled as a file (tested, hashed, copied, printed) rather than run?"""
        if i == 0:
            return False
        if lang == "sh":  # the shell command it is a word of: sha256sum A B $ETT ..., echo "... $ETT ...", [ -x $ETT ]
            k = i - 1
            while k >= 0 and toks[k][0] not in (";", "do", "then", "else", "&&", "||", "|", "{", "(", "!", "if",
                                                    "while", "until") and not toks[k][0].endswith(";"):
                k -= 1
            j = k + 1
            while j < i and re.fullmatch(r"[A-Za-z_]\w*=\S*", toks[j][0]):
                j += 1  # VAR=value prefixes
            if j < i and toks[j][0] in NONEXEC:
                return True
        prev = toks[i - 1][0]
        if prev in NONEXEC:
            return True
        # a Python call such as os.path.isfile(ETT): its last dotted name; never a path's extension
        return bool(re.fullmatch(r"[A-Za-z_]\w*(\.[A-Za-z_]\w*)+", prev)) and prev.rsplit(".", 1)[-1] in NONEXEC

    def at_command_start(self, toks, i):
        if i == 0:
            return True
        prev = toks[i - 1][0]
        if prev in CMD_START or prev.endswith((";", "&&", "||", "|")) or re.fullmatch(r"-\S+|\d+[smh]?", prev) or \
                re.fullmatch(r"[A-Za-z_]\w*=\S+", prev):  # timeout 10 ..., nice -n 10 ..., LD_LIBRARY_PATH=... cmd
            return True
        return False

    def word_list(self, toks, i):
        """Is toks[i] a word of a for/select/case list (for b in "$HEATER" "$ETTELEM"; do ...)?"""
        k = i - 1
        while k >= 0 and toks[k][0] not in (";", "do", "then", "else", "&&", "||", "|", "{", "(") and \
                not toks[k][0].endswith(";"):
            k -= 1
        first = toks[k + 1][0] if k + 1 < len(toks) else ""
        return first in ("for", "select", "case") and k + 1 < i

    # ---- the rules -------------------------------------------------------------------------------------------------
    def scan_ettelem(self, path, n, code, lang, file_refs_ettelem):
        toks = qtokens(code)
        hits = []
        for i in range(len(toks) - 1):
            tok, q, pre = toks[i]
            kind = self.binary_kind(tok, file_refs_ettelem, lang, q)
            if kind is None or self.nonexec(toks, i, lang):
                continue
            if lang == "sh" and self.word_list(toks, i):
                continue  # for b in "$HEATER" "$ETTELEM" ...: a list of words, not a command
            nxt, nq, npre = toks[i + 1]
            nxt = nxt.rstrip("`")  # `ettelem config` (a shell command substitution, or Markdown in a message)
            if lang == "py" and i + 2 < len(toks) and toks[i + 2][0] == ":" and nq == "w":
                continue  # {"ettelem": ETT, "config": ...}: a dict key, not a subcommand
            # a command word: not inside a message (a word of a longer quoted string), unless it starts a command
            # there (a command line kept in a string, a script a Python string writes out)
            cmdword = q != "p" or self.at_command_start(toks, i)
            if kind in ("bare", "name") or (kind == "anyvar" and not cmdword):
                weak = True  # the word ettelem or a build's name, as prose usually is: no binary in view
            else:
                weak = not cmdword
            if lang == "sh" and kind == "bare" and q == "" and self.at_command_start(toks, i):
                weak = False  # an ettelem on the PATH, run as a command
            if nxt in self.t.subcommands:
                hits.append((i, nxt, "known", kind, weak))
                continue
            # past the reviewed subcommands, only a call the checker can see as one
            if weak or q == "p" or kind == "anyvar" or lang not in ("sh", "py"):
                continue
            if lang == "py":
                if pre not in ("[", "(", ","):
                    continue  # a list or tuple element is how a Python runner passes a binary to subprocess
                if nq == "" and nxt.startswith("*"):
                    hits.append((i, nxt, "forward", kind, weak))
                elif nq == "" and pre == "[" and re.fullmatch(r"[A-Za-z_][\w.]*", nxt) and nxt not in PY_KEYWORDS:
                    hits.append((i, nxt, "forward", kind, weak))
                elif nq == "w" and npre == "," and SUBWORD_RE.fullmatch(nxt):
                    hits.append((i, nxt, "unknown", kind, weak))
            else:
                if i > 0 and toks[i - 1][0] in ("in", "for", "case", "==", "!=", "=", "-eq", "-ne"):
                    continue  # a word list, not a command
                if FORWARD_TOK.fullmatch(nxt) or nxt.startswith("$"):
                    hits.append((i, nxt, "forward", kind, weak))
                elif SUBWORD_RE.fullmatch(nxt) and nq != "p":
                    hits.append((i, nxt, "unknown", kind, weak))
        if not hits:
            return self.scan_wrapper_calls(path, n, code, lang, toks, file_refs_ettelem)
        for i, sub, how, kind, weak in hits:
            res = self.resolve(toks[i][0], kind, path)
            if weak:  # prose: list what a reviewed build would send, but do not judge an unseen binary by it
                if res.unresolved or res.unreviewed or not (res.variants or res.program):
                    res.variants = set(res.variants) or set(self.t.variants)
                res.unresolved, res.unreviewed = False, []
            if how == "forward":
                where = self.func_at[n] if self.func_at[n] else Path(path).name
                self.add(path, n, "ettelem (arguments forwarded)", "WRAPPER",
                         f"the subcommand comes from '{sub}': classified at the call sites of {where}")
                self.flag_binary(path, n, "ettelem (arguments forwarded)", res, toks[i][0], sub)
                continue
            self.classify(path, n, "ettelem " + sub, sub, [t for t, _, _ in toks[i + 2:]], code, res, toks[i][0], weak)
        return True

    def flag_binary(self, path, n, tool, res, btok, sub):
        if res.unreviewed:
            self.add(path, n, tool, "UNREVIEWED_VARIANT", f"{', '.join(res.unreviewed)} ('{sub}'): in no reviewed build "
                     "directory, so what it sends is not in the table")
        if res.unresolved:
            self.add(path, n, tool, "VARIANT_UNRESOLVED", f"binary from '{btok}' ({res.how}): which build runs is not "
                     "visible; its sends are listed as the reviewed variants'")

    def classify(self, path, n, tool, sub, rest, code, res, btok, weak=False):
        if res.program and not res.variants and not res.unreviewed and not res.unresolved:
            self.notes.append(f"{path}:{n}: '{sub}' goes through {res.program}, which is scanned: its own lines are "
                              "what it sends")
            return
        self.flag_binary(path, n, tool, res, btok, sub)
        variants = sorted(self.t.variants) if res.unresolved else sorted(res.variants)
        if not variants:
            return
        vtag = "/".join(variants)
        asked = []  # reset options asked for on the line, with a value that is not a literal 0
        for k, w in enumerate(rest):
            if w in ("--reset-ms", "--reset-once-file"):
                val = rest[k + 1] if k + 1 < len(rest) else ""
                if not (w == "--reset-ms" and val == "0"):
                    asked.append(w)
        forwarded = bool(FORWARD_RE.search(code))
        sends, reset_possible, refused, missing = set(), False, [], []
        for v in variants:
            sc = self.t.variants[v]["subcommands"].get(sub)
            if sc is None:
                missing.append(v)
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
        if missing and not weak and (not res.unresolved or len(missing) == len(variants)):
            self.add(path, n, tool, "UNKNOWN_SUBCOMMAND",
                     f"no subcommand '{sub}' in {', '.join(missing)}: what that binary does with it is not in the table")
        for cmd in sorted(sends):
            tags, cond, detail = [], False, f"variant {vtag}"
            if cmd == "STATS_RESET" and reset_possible:
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

    def scan_wrapper_calls(self, path, n, code, lang, toks, file_refs_ettelem):
        """Calls of a wrapper that forwards its arguments to ettelem: self.tool("residency", ...) in Python, or a shell
        function called with the subcommand among its words."""
        found = False
        if lang == "py":
            for m in re.finditer(r"(?<![\w.])(?:self\.)?([A-Za-z_]\w*)\(\s*[\"']([^\"'\n]*)[\"']", code):
                name, sub = m.group(1), m.group(2)
                known = (path_key := (str(path), name)) in self.wrappers
                if name in NOT_WRAPPERS or not (known or (file_refs_ettelem and sub in self.t.subcommands)):
                    continue
                if not known and sub not in self.t.subcommands:
                    continue
                j = next((k for k, (t, _, _) in enumerate(toks) if t == sub), None)
                rest = [t for t, _, _ in toks[j + 1:]] if j is not None else []
                res = self.wrapper_res(path_key, path)
                if not known:  # a call that only looks like a wrapper's: what it would send, without judging a binary
                    res.variants = set(res.variants) or set(self.t.variants)
                    res.unresolved, res.unreviewed = False, []
                tool = f"ettelem {sub} (wrapper call {name})" if SUBWORD_RE.fullmatch(sub or "-") else \
                    f"ettelem (wrapper call {name})"
                if not SUBWORD_RE.fullmatch(sub or "-"):
                    self.add(path, n, tool, "UNKNOWN_SUBCOMMAND", f"'{sub}' is no subcommand")
                else:
                    self.classify(path, n, tool, sub, rest, code, res, name, weak=not known)
                self.wrapper_calls[path_key] = self.wrapper_calls.get(path_key, 0) + 1
                found = True
        elif lang == "sh":
            for k, (t, q, _) in enumerate(toks):
                key = (str(path), t)
                if q or key not in self.wrappers or not self.at_command_start(toks, k):
                    continue
                if k > 0 and toks[k - 1][0] in ("function",):
                    continue
                args = []
                for t2, _, _ in toks[k + 1:]:
                    if t2 in (";", "&&", "||", "|") or t2.startswith((">", "<", "2>", "&>")):
                        break
                    args.append(t2)
                subs = [a for a in args if a in self.t.subcommands]
                res = self.wrapper_res(key, path)
                if subs:
                    sub = subs[0]
                    rest = []
                    for idx, a in enumerate(args):  # every literal integer after any occurrence of the subcommand
                        if a == sub:
                            for b in args[idx + 1:]:
                                if not re.fullmatch(r"-?\d+", b):
                                    break
                                rest.append(b)
                    if "--reset-ms" in args or "--reset-once-file" in args:
                        rest += [a for a in args if a.startswith("--reset")] + ["1"]
                    self.classify(path, n, f"ettelem {sub} (wrapper call {t})", sub, rest, code, res, t)
                else:
                    bare = [a for a in args if SUBWORD_RE.fullmatch(a)]
                    if not bare:
                        continue
                    self.flag_binary(path, n, f"ettelem (wrapper call {t})", res, t, bare[0])
                    self.add(path, n, f"ettelem (wrapper call {t})", "UNKNOWN_SUBCOMMAND",
                             f"no reviewed subcommand among its words ({' '.join(args[:6])})")
                self.wrapper_calls[key] = self.wrapper_calls.get(key, 0) + 1
                found = True
        return found

    def wrapper_res(self, key, path):
        if key in self.wrappers:
            btok, bkind, _ = self.wrappers[key]
            return self.resolve(btok, bkind, path)
        r = Res()  # a call that looks like a wrapper's in a file that runs ettelem: the binaries its file names
        dirs = sorted(self.file_dirs.get(str(path), set()))
        if not dirs:
            r.unresolved = True
            r.how = f"the wrapper {key[1]}, defined outside the scanned files"
            if "unresolved" in self.bindings and self.bindings["unresolved"]:
                r.variants.add(self.bindings["unresolved"])
                r.unresolved = False
            return r
        for d in dirs:
            v = self.bindings.get(d) or self.t.dir_variant.get(d)
            if v:
                r.variants.add(v)
            else:
                r.unreviewed.append(d + "/ettelem")
        return r

    def collect_wrappers(self, texts):
        """Functions (and scanned programs) that pass their own arguments to an ettelem binary as its subcommand."""
        for path, (lang, text, lines) in texts.items():
            self.cur = str(path)
            at = functions_at(text, lang)
            file_refs = bool(re.search(r"ettelem", text))
            for n, code in lines:
                if not file_refs:
                    break
                toks = qtokens(code)
                for i in range(len(toks) - 1):
                    tok, q, pre = toks[i]
                    kind = self.binary_kind(tok, file_refs, lang, q)
                    if kind not in ("path", "var", "program") or q == "p" or self.nonexec(toks, i, lang) or \
                            (lang == "sh" and self.word_list(toks, i)):
                        continue
                    nxt, nq, _ = toks[i + 1]
                    if lang == "py":
                        fwd = pre in ("[", "(", ",") and nq == "" and nxt.startswith("*")
                    elif lang == "sh":
                        fwd = (FORWARD_TOK.fullmatch(nxt) or re.fullmatch(r"\$\{?[1-9@*]\}?", nxt)) and \
                            not (i > 0 and toks[i - 1][0] in ("in", "for", "case"))
                    else:
                        fwd = False
                    if not fwd:
                        continue
                    fn = at[n] if n < len(at) else None
                    key = (str(path), fn) if fn else (Path(path).name, None)
                    self.wrappers.setdefault(key, (tok, kind, n))
        self.cur = None

    def dms_token(self, w):
        if "dev_mngt_service" in w:
            return True
        names = re.findall(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)", w) or ([w] if re.fullmatch(r"(?:self\.)?[A-Za-z_]\w*", w) else [])
        return any("dev_mngt_service" in rhs for nm in names for rhs in self.rhs_of(nm.split(".")[-1]))

    def scan_dms(self, path, n, code):
        allw = words(code)
        # words() splits at commas, so a -t argument's later operations ("SPST:extract,reset") are read from the line
        full_traces = re.findall(r"(?<![\w-])(?:-t|--trace)(?:=|\s+)[\"']?([A-Z]+:[a-z_,]+)", code)
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
                full = next((x for x in full_traces if x == tval or x.startswith(tval + ",")), None)
                if full is not None:
                    full_traces.remove(full)
                    tval = full
                m = re.fullmatch(r"(SPST|MMST|SP|MM|CM):([a-z_,]+)", tval)
                if not m:
                    self.add(path, n, "dev_mngt_service -t", "DYNAMIC", f"trace operation from '{tval}'")
                    continue
                ttype, ops = m.group(1), m.group(2).split(",")
                if "extract" in ops:
                    self.add(path, n, "dev_mngt_service -t", "TRACE_EXTRACT", tval)
                ctl = [op for op in ops if op in ("enable", "disable", "reset", "to_uart", "to_memory")]
                if not ctl:
                    continue
                if ttype == "SP":
                    self.add(path, n, "dev_mngt_service -t", "SET_DM_TRACE_RUN_CONTROL", tval)
                elif ttype in ("SPST", "MMST"):
                    # dev_mngt_service.cc doTraceOperation: enable is on unless the last of enable/disable is disable;
                    # reset adds RESET_TRACEBUF | RESET_COUNTER; to_uart/to_memory send the enable flag only
                    en = [op for op in ctl if op in ("enable", "disable")]
                    enable = not en or en[-1] == "enable"
                    control = (1 if enable else 0) | (6 if "reset" in ctl else 0)
                    typ = 1 if ttype == "SPST" else 2
                    form = "MMST_CONTROL" if ttype == "MMST" else ("SPST_RESET" if "reset" in ctl else "SPST_TRACE_CONTROL")
                    self.add(path, n, "dev_mngt_service -t", form,
                             f"{tval}: DM_CMD_SET_STATS_RUN_CONTROL type {typ}, control {control}")
                # MM and CM take no control: dev_mngt_service refuses them before sending anything
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
                        self.add(path, n, "reset option passed on", "STATS_RESET",
                                 f"{w} {val}: a sampler wrapper forwards it to ettelem sample", True)
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
        self.func_at = functions_at(text, lang)
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
                handled = self.scan_ettelem(path, n, code, lang, file_refs_ettelem)
            elif any(k[0] == str(path) for k in self.wrappers):
                handled = self.scan_wrapper_calls(path, n, code, lang, qtokens(code), False)
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
            self.programs.setdefault(p.name, str(p))
        self.cur = None
        self.collect_assignments(texts)
        self.collect_sources(texts)
        self.collect_wrappers(texts)
        for p, (lang, text, lines) in texts.items():
            self.scan_file(p, lang, text, lines)
        for key, (btok, _, ln) in sorted(self.wrappers.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]))):
            if key[1] is not None and not self.wrapper_calls.get(key):
                self.notes.append(f"{key[0]}:{ln}: {key[1]} forwards its arguments to ettelem ('{btok}') and no call "
                                  "of it was found in that file: a person reads its callers")
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
                reasons.append("WRITE not in the allow-list" + (
                    " (a form the checker cannot see: not provably the ruled statistics reset)"
                    if cmd == "SET_STATS_RUN_CONTROL" else ""))
            if r["cls"] in ("UNSUPPORTED", "UNCLASSIFIED") and cmd not in allow:
                reasons.append(cmd if cmd in NEVER_ALLOW else r["cls"])
            if r["cls"] == "READ" and deny_pmic_read and r["pmic"] == "read" and cmd not in allow:
                reasons.append("PMIC read denied (--deny-pmic-read)")
            for tag in r["tags"]:
                if tag not in allow:
                    reasons.append(tag)
            waived = excepts.get((os.path.normpath(r["file"]), r["line"]), {})
            kept = [x for x in reasons if not ((cmd in waived and x.startswith(("WRITE", "UNSUPPORTED", "UNCLASSIFIED",
                                                                                     "PMIC read") + NEVER_ALLOW))
                                                or x in waived)]
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
    binds = "; ".join(f"`{k}` = {v or 'no reviewed variant'}" for k, v in sorted(audit.bindings.items()))
    lines = ["## Device commands sent", "",
             f"Checked with `tools/claims-v3/dmcmd_audit.py` against `{audit.t.path.name}` (et-platform "
             f"`{audit.t.raw['source']['commit'][:7]}`, BL2 {audit.t.raw['source']['bl2_version'].split()[0]}); "
             f"allow-list: {', '.join(sorted(allow)) or 'none'}{'; PMIC reads denied' if args.deny_pmic_read else ''}"
             f"{'; variant sources: ' + binds if binds else ''}. "
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
        elif r["command"] == "WRAPPER":
            lines.append(f"- To read `{r['file']}:{r['line']}` {r['tool']}: {r['detail']}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="the runner's files or directories")
    ap.add_argument("--files-from", metavar="LIST", help="also scan the paths listed in LIST, one a line")
    ap.add_argument("--table", default=str(DEFAULT_TABLE), help="the audit table (default: beside this script)")
    ap.add_argument("--allow", action="append", default=[], help="allowed WRITE or tag names (repeatable, comma-separated)")
    ap.add_argument("--deny-pmic-read", action="store_true", help="treat PMIC register reads as NO-GO too")
    ap.add_argument("--variant-source", action="append", default=[], metavar="KEY=SOURCE",
                    help="the ettelem source a binary was built from: KEY is its build directory (build/ettelem-x/) or "
                         "program name, or 'unresolved' for every binary the checker cannot resolve; taken only when "
                         "SOURCE's sha256 equals a reviewed variant's")
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
        for name, c in table.forms.items():
            print(f"{c['id']:>3} {name:<42} {c['class']:<12} pmic={c.get('pmic', 'none'):<7} form of {c['of']}: "
                  f"{c['what'][:70]}")
        return EXIT_GO
    files_in = list(args.files)
    if args.files_from:
        try:
            files_in += [ln.strip() for ln in Path(args.files_from).read_text().splitlines() if ln.strip()]
        except OSError as e:
            print(f"dmcmd_audit: cannot read {args.files_from}: {e}", file=sys.stderr)
            return EXIT_USAGE
    if not files_in:
        ap.print_usage(sys.stderr)
        return EXIT_USAGE
    allow, notes = set(), []
    for a in args.allow:
        for x in a.split(","):
            x = x.strip()
            if x:
                x = x[len("DM_CMD_"):] if x.startswith("DM_CMD_") else x
                if x in FORM_ALIAS:
                    notes.append(f"--allow {x} is read as {FORM_ALIAS[x]}: the statistics reset the owner ruled on "
                                 "(type 1, control 2); SPST_TRACE_CONTROL, SPST_RESET, MMST_CONTROL and a send whose "
                                 "form is not visible stay disallowed")
                    x = FORM_ALIAS[x]
                allow.add(x)
    never = [a for a in allow if a in NEVER_ALLOW]
    if never:
        print(f"dmcmd_audit: {', '.join(sorted(never))} cannot be allowed: name the binary's reviewed source with "
              "--variant-source KEY=SOURCE, or record a reviewed --except for the line", file=sys.stderr)
        return EXIT_USAGE
    unknown = [a for a in allow if a not in table.commands and a not in table.forms and a not in table.pseudo and
               a not in TAG_NAMES]
    if unknown:
        print(f"dmcmd_audit: --allow names not in the table: {', '.join(sorted(unknown))}", file=sys.stderr)
        return EXIT_USAGE
    bindings = {}
    for vs in args.variant_source:
        m = re.fullmatch(r"([^=]+)=(.+)", vs)
        if not m:
            print(f"dmcmd_audit: --variant-source wants KEY=SOURCE, got '{vs}'", file=sys.stderr)
            return EXIT_USAGE
        try:
            sha = hashlib.sha256(Path(m.group(2)).read_bytes()).hexdigest()
        except OSError as e:
            print(f"dmcmd_audit: --variant-source: cannot read {m.group(2)}: {e}", file=sys.stderr)
            return EXIT_USAGE
        v = table.src_variant.get(sha)
        bindings[source_key(m.group(1))] = v
        notes.append(f"--variant-source {source_key(m.group(1))}: {m.group(2)} (sha256 {sha[:12]}) "
                     + (f"is the reviewed {v}" if v else "matches no reviewed variant: review it into the table first"))
    excepts = {}
    for e in args.excepts:
        m = re.fullmatch(r"(.+):(\d+):([A-Z0-9_]+)=(.+)", e)
        if not m:
            print(f"dmcmd_audit: --except wants FILE:LINE:NAME=REASON, got '{e}'", file=sys.stderr)
            return EXIT_USAGE
        name = m.group(3)[len("DM_CMD_"):] if m.group(3).startswith("DM_CMD_") else m.group(3)
        excepts.setdefault((os.path.normpath(m.group(1)), int(m.group(2))), {})[name] = m.group(4).strip()
    try:
        files = expand(files_in)
    except FileNotFoundError as e:
        print(f"dmcmd_audit: no such file: {e}", file=sys.stderr)
        return EXIT_USAGE
    audit = Audit(table, files, bindings).run()
    audit.notes = notes + audit.notes
    nogo = audit.judge(allow, args.deny_pmic_read, excepts)
    verdict = "NO-GO" if nogo else "GO"
    if args.json:
        summ = {k: {**v, "verdicts": sorted(v["verdicts"])} for k, v in summarize(audit.records).items()}
        print(json.dumps({"verdict": verdict, "allow": sorted(allow), "deny_pmic_read": args.deny_pmic_read,
                          "variant_sources": {k: v for k, v in sorted(bindings.items())},
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
        for note in notes:
            print("note: " + note, file=sys.stderr)
        for r in nogo:
            print(f"NO-GO {r['file']}:{r['line']}: {r['tool']}: {r['command']}: {r['verdict'][7:]}", file=sys.stderr)
        print(f"dmcmd_audit: {verdict} ({len(audit.records)} send site(s), {len(nogo)} disallowed; "
              f"allow-list: {', '.join(sorted(allow)) or 'none'})", file=sys.stderr)
    return EXIT_NOGO if nogo else EXIT_GO


if __name__ == "__main__":
    sys.exit(main())
