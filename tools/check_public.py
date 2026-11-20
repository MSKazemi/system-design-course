#!/usr/bin/env python3
"""Static checks for the public surface of the course repository.

Standard library + PyYAML only. Nothing here runs lab code, starts a container,
touches the network or calls any API. Run it from anywhere:

    python3 -I tools/check_public.py            # all checks
    python3 -I tools/check_public.py --root DIR # check another checkout
    python3 -I tools/check_public.py --extract-mermaid OUTDIR

Exit status: 0 = clean (warnings allowed), 1 = at least one error, 2 = usage.
Messages look like ``path:line: [rule] message`` so editors and the GitHub
Actions log can jump to the line.

Only the *public surface* is inspected (README.md, CONTRIBUTING.md,
SYLLABUS.md, REFERENCES.md, LICENSE, course.yaml, course/, slides/,
exercises/, labs/, tools/, .github/). Links must resolve inside that surface,
so the result is identical on a full working tree and on a clean public clone.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment problem, not a content problem
    sys.exit("check_public.py needs PyYAML: pip install pyyaml")

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

SURFACE_FILES = ("README.md", "CONTRIBUTING.md", "SYLLABUS.md", "REFERENCES.md",
                 "LICENSE", "course.yaml")
SURFACE_DIRS = ("course", "slides", "exercises", "labs", "tools", ".github")
SKIP_DIRS = {"__pycache__", ".git", "node_modules", ".pytest_cache", ".ruff_cache"}
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".py", ".sh", ".js", ".cfg",
                 ".sql", ".txt", ".toml", ".conf", ".html", ".css", ".ini",
                 ".env", ".service", ""}
MAX_TEXT_BYTES = 4_000_000

LESSON_GLOB = "course/*/*.md"
REQUIRED_KEYS = ("id", "title", "status", "requirement",
                 "learning_objectives", "last_reviewed")
ID_PREFIX = "SYSDESIGN-"
LAB_STATUS_LABELS = ("illustrative", "syntax-reviewed", "runtime-tested")

# Private top-level directories / tooling names. Assembled from pieces so this
# file never matches its own rules.
_PRIVATE_DIRS = ("des" + "ign", "produc" + "tion", "inter" + "nal", "ic" + "ons")
PRIVATE_PATH_RE = re.compile(
    r"(?<![\w./~-])(?:" + "|".join(_PRIVATE_DIRS) + r")/[\w.-]+(?:/|\.[A-Za-z]{1,5}\b)"
    r"|(?<![\w-])\.(?:clau" + r"de|dual" + r"git)(?:/|\b)"
    r"|\.git-" + "priv" + r"ate\b"
    r"|\bdual" + r"git\b"
)
PRIVATE_REPO_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]*-" + "priv" + r"ate\b")
HOSTED_PRIVATE_REPO_RE = re.compile(r"(?:github|gitlab)\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]*-" + "priv" + r"ate\b")
HOME_PATH_RE = re.compile(r"(?<![\w.-])(?:/home/([a-z_][a-z0-9_-]*)/|/Users/([A-Za-z_][\w-]*)/"
                          r"|[A-Za-z]:\\Users\\([\w-]+)\\)")
GENERIC_HOME_USERS = {"app", "appuser", "node", "nonroot", "user", "runner",
                      "ubuntu", "vscode", "postgres", "redis", "www-data",
                      "python", "lab", "name", "username", "you", "me"}
# Tool paths that exist only in the private tree; reported as warnings.
PRIVATE_TOOL_RE = re.compile(r"(?<![\w./-])scr" + r"ipts/[\w.-]+\.py\b")

SECRET_PATTERNS = [
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("github-token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}\b")),
    ("api-key", re.compile(r"\bsk-(?:[A-Za-z0-9]+-)*[A-Za-z0-9_]{20,}")),
    ("aws-key-id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("slack-token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("docker-auth", re.compile(r"\"auth\"\s*:\s*\"[A-Za-z0-9+/=]{20,}\"")),
]
SECRET_ALLOW_RE = re.compile(r"EXAMPLE|PLACEHOLDER|REDACTED", re.I)
SECRET_FILENAMES = {".env", "id_rsa", "id_ed25519", "credentials", ".netrc",
                    ".npmrc", ".pypirc"}
SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".kdbx"}

ATTRIBUTION_RES = [
    re.compile(r"co-authored-" + r"by\s*:\s*(?:claude|.*anthropic)", re.I),
    re.compile(r"generated\s+with\s+\[?claude", re.I),
    re.compile(r"noreply@anthr" + r"opic\.com", re.I),
    re.compile("\U0001F916" + r"\s*generated", re.I),
]

URL_RE = re.compile(r"https?://[^\s<>\"]+")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")

# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #


class Report:
    def __init__(self) -> None:
        self.errors: list[tuple[str, int, str, str]] = []
        self.warnings: list[tuple[str, int, str, str]] = []
        self.counts: dict[str, int] = {}

    def error(self, path: str, line: int, rule: str, msg: str) -> None:
        self.errors.append((path, line, rule, msg))

    def warn(self, path: str, line: int, rule: str, msg: str) -> None:
        self.warnings.append((path, line, rule, msg))

    def count(self, what: str, n: int = 1) -> None:
        self.counts[what] = self.counts.get(what, 0) + n


# --------------------------------------------------------------------------- #
# Surface discovery
# --------------------------------------------------------------------------- #


class Surface:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.files: list[Path] = []
        for name in SURFACE_FILES:
            p = self.root / name
            if p.is_file():
                self.files.append(p)
        for d in SURFACE_DIRS:
            base = self.root / d
            if not base.is_dir():
                continue
            for dirpath, dirnames, filenames in os.walk(base):
                dirnames[:] = sorted(x for x in dirnames if x not in SKIP_DIRS)
                for fn in sorted(filenames):
                    self.files.append(Path(dirpath) / fn)
        self.rel_set = {self.rel(p) for p in self.files}
        self.dir_set: set[str] = set()
        for r in self.rel_set:
            parts = r.split("/")
            for i in range(1, len(parts)):
                self.dir_set.add("/".join(parts[:i]))

    def rel(self, p: Path) -> str:
        return p.resolve().relative_to(self.root).as_posix()

    def has_file(self, rel: str) -> bool:
        return rel in self.rel_set

    def has_dir(self, rel: str) -> bool:
        return rel in self.dir_set

    def read(self, rel: str) -> str | None:
        p = self.root / rel
        try:
            if p.stat().st_size > MAX_TEXT_BYTES:
                return None
            data = p.read_bytes()
        except OSError:
            return None
        if b"\0" in data:
            return None
        return data.decode("utf-8", errors="replace")

    def text_files(self) -> list[str]:
        out = []
        for p in self.files:
            r = self.rel(p)
            name = p.name
            suffix = p.suffix.lower()
            if suffix in TEXT_SUFFIXES or name == "Dockerfile" or name.startswith("Dockerfile."):
                out.append(r)
        return out

    def glob(self, pattern: str) -> list[str]:
        regex = re.compile("^" + re.escape(pattern).replace(r"\*", "[^/]*") + "$")
        return sorted(r for r in self.rel_set if regex.match(r))


# --------------------------------------------------------------------------- #
# Markdown model
# --------------------------------------------------------------------------- #

FENCE_RE = re.compile(r"^[ \t]*(?:>[ \t]*)*(`{3,}|~{3,})(.*)$")
HEADING_RE = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.*?)[ \t]*$")
CODE_SPAN_RE = re.compile(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)")
HTML_ANCHOR_RE = re.compile(r"<a\b[^>]*?\b(?:name|id)\s*=\s*[\"']([^\"']+)[\"']", re.I)
HTML_ID_RE = re.compile(r"\bid\s*=\s*[\"']([^\"']+)[\"']", re.I)
HTML_ATTR_LINK_RE = re.compile(r"\b(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", re.I)
REF_DEF_RE = re.compile(r"^ {0,3}\[[^\]]+\]:[ \t]*(<[^>]*>|\S+)")


class MdDoc:
    """Line-oriented view of a Markdown file: front matter, fences, headings."""

    def __init__(self, rel: str, text: str) -> None:
        self.rel = rel
        self.lines = text.split("\n")
        self.fm_end = 0  # number of lines occupied by front matter (incl. delimiters)
        self.fm_text = None
        self._split_front_matter()
        self.in_fence = [False] * len(self.lines)
        self.fences: list[dict] = []      # {info, start, end (0-based), closed}
        self.unclosed: list[dict] = []
        self._scan_fences()
        self.headings: list[tuple[int, int, str]] = []  # (lineno, level, raw text)
        self._scan_headings()
        self._anchors: set[str] | None = None

    def _split_front_matter(self) -> None:
        if self.lines and self.lines[0].rstrip() == "---":
            for i in range(1, len(self.lines)):
                if self.lines[i].rstrip() in ("---", "..."):
                    self.fm_end = i + 1
                    self.fm_text = "\n".join(self.lines[1:i])
                    return

    def _scan_fences(self) -> None:
        open_f = None
        for i in range(self.fm_end, len(self.lines)):
            line = self.lines[i]
            m = FENCE_RE.match(line)
            if open_f is None:
                if m:
                    marker, info = m.group(1), m.group(2).strip()
                    if marker[0] == "`" and "`" in info:
                        continue  # inline code that merely starts with ```
                    open_f = {"char": marker[0], "len": len(marker), "info": info,
                              "start": i, "end": None}
                    self.in_fence[i] = True
            else:
                self.in_fence[i] = True
                if m:
                    marker, rest = m.group(1), m.group(2).strip()
                    if marker[0] == open_f["char"] and len(marker) >= open_f["len"] and not rest:
                        open_f["end"] = i
                        self.fences.append(open_f)
                        open_f = None
        if open_f is not None:
            self.unclosed.append(open_f)
            self.fences.append(open_f)

    def _scan_headings(self) -> None:
        for i in range(self.fm_end, len(self.lines)):
            if self.in_fence[i]:
                continue
            m = HEADING_RE.match(self.lines[i])
            if m:
                text = re.sub(r"[ \t]+#+[ \t]*$", "", m.group(2))
                self.headings.append((i + 1, len(m.group(1)), text))

    def prose_lines(self):
        """Yield (lineno, text) for lines outside front matter and fences."""
        for i in range(self.fm_end, len(self.lines)):
            if not self.in_fence[i]:
                yield i + 1, self.lines[i]

    @property
    def anchors(self) -> set[str]:
        if self._anchors is None:
            seen: dict[str, int] = {}
            out: set[str] = set()
            for _, _, text in self.headings:
                slug = github_slug(text)
                n = seen.get(slug, 0)
                seen[slug] = n + 1
                out.add(slug if n == 0 else f"{slug}-{n}")
            for _, line in self.prose_lines():
                for m in HTML_ANCHOR_RE.finditer(line):
                    out.add(m.group(1).lower())
                for m in HTML_ID_RE.finditer(line):
                    out.add(m.group(1).lower())
            self._anchors = out
        return self._anchors


def github_slug(heading: str) -> str:
    """GitHub's heading anchor: github-slugger applied to the rendered text."""
    s = heading.strip()
    s = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", s)      # images -> alt
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)        # links -> text
    s = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", s)       # ref links -> text
    s = re.sub(r"<[^>]+>", "", s)                          # inline HTML
    s = re.sub(r"`+", "", s)                               # code span markers
    s = s.replace("*", "").replace("~~", "")
    s = re.sub(r"(?<![\w])_+|_+(?![\w])", "", s)           # emphasis underscores
    s = s.lower()
    keep = []
    for ch in s:
        cat = unicodedata.category(ch)
        if ch in " -" or cat[0] in "LMN" or cat == "Pc":
            keep.append(ch)
    return "".join(keep).replace(" ", "-")


def mask_code_spans(line: str) -> str:
    return CODE_SPAN_RE.sub(lambda m: " " * len(m.group(0)), line)


def link_targets(line: str):
    """Yield link destinations found in one prose line (inline, reference, HTML)."""
    masked = mask_code_spans(line)
    m = REF_DEF_RE.match(masked)
    if m:
        yield m.group(1).strip("<>")
    pos = 0
    while True:
        i = masked.find("](", pos)
        if i < 0:
            break
        j = i + 2
        n = len(masked)
        while j < n and masked[j] in " \t":
            j += 1
        if j < n and masked[j] == "<":
            k = masked.find(">", j)
            if k < 0:
                break
            yield masked[j + 1:k]
            pos = k
            continue
        depth = 0
        k = j
        while k < n:
            c = masked[k]
            if c == "\\":
                k += 2
                continue
            if c == "(":
                depth += 1
            elif c == ")":
                if depth == 0:
                    break
                depth -= 1
            elif c in " \t" and depth == 0:
                break
            k += 1
        dest = masked[j:k]
        if dest:
            yield dest
        pos = max(k, i + 2)
    for hm in HTML_ATTR_LINK_RE.finditer(masked):
        yield hm.group(1)


# --------------------------------------------------------------------------- #
# Individual checks
# --------------------------------------------------------------------------- #


class Checker:
    def __init__(self, surface: Surface, report: Report) -> None:
        self.s = surface
        self.r = report
        self._docs: dict[str, MdDoc] = {}

    def doc(self, rel: str) -> MdDoc | None:
        if rel not in self._docs:
            text = self.s.read(rel)
            if text is None:
                return None
            self._docs[rel] = MdDoc(rel, text)
        return self._docs[rel]

    def md_files(self) -> list[str]:
        return [r for r in sorted(self.s.rel_set) if r.endswith(".md")]

    # -- lessons ------------------------------------------------------------ #

    def lessons(self) -> list[str]:
        return self.s.glob(LESSON_GLOB)

    def check_lessons(self) -> None:
        seen_ids: dict[str, str] = {}
        lessons = self.lessons()
        if not lessons:
            self.r.error("course", 0, "lessons", "no lessons found under course/*/*.md")
        for rel in lessons:
            self.r.count("lessons")
            d = self.doc(rel)
            if d is None:
                self.r.error(rel, 1, "front-matter", "cannot read file")
                continue
            base = Path(rel).stem
            fm = self._front_matter(d, rel)
            if fm is not None:
                for key in REQUIRED_KEYS:
                    if key not in fm or fm[key] in (None, "", []):
                        self.r.error(rel, 1, "front-matter", f"missing or empty key '{key}'")
                m = re.match(r"^([A-Z]?\d+)-", base)
                if not m:
                    self.r.error(rel, 1, "filename", "file name must start with a lesson code, e.g. 04- or C01-")
                else:
                    want = ID_PREFIX + m.group(1)
                    got = fm.get("id")
                    if got is not None and str(got) != want:
                        self.r.error(rel, self._fm_line(d, "id"), "front-matter",
                                     f"id '{got}' does not match file name (expected '{want}')")
                    if got is not None:
                        if str(got) in seen_ids:
                            self.r.error(rel, self._fm_line(d, "id"), "front-matter",
                                         f"duplicate id '{got}' (also in {seen_ids[str(got)]})")
                        seen_ids[str(got)] = rel
                lo = fm.get("learning_objectives")
                if lo not in (None, "", []):
                    if not isinstance(lo, list) or not all(isinstance(x, str) and x.strip() for x in lo):
                        self.r.error(rel, self._fm_line(d, "learning_objectives"), "front-matter",
                                     "learning_objectives must be a list of non-empty strings")
                lr = fm.get("last_reviewed")
                if lr not in (None, ""):
                    ok = isinstance(lr, (datetime.date, datetime.datetime)) or (
                        isinstance(lr, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", lr))
                    if not ok:
                        self.r.error(rel, self._fm_line(d, "last_reviewed"), "front-matter",
                                     f"last_reviewed must be an ISO date YYYY-MM-DD, got {lr!r}")
                for key in ("title", "status", "requirement"):
                    v = fm.get(key)
                    if v not in (None, "") and not isinstance(v, str):
                        self.r.error(rel, self._fm_line(d, key), "front-matter", f"'{key}' must be a string")
            for kind in ("slides", "exercises"):
                want = f"{kind}/{base}.md"
                if not self.s.has_file(want):
                    self.r.error(rel, 1, "companion", f"missing {want}")
        # orphans
        bases = {Path(x).stem for x in lessons}
        for kind in ("slides", "exercises"):
            for rel in self.s.glob(f"{kind}/*.md"):
                if Path(rel).stem not in bases:
                    self.r.error(rel, 1, "companion", "no matching lesson in course/*/")
        # syllabus lists every lesson id
        syl = self.s.read("SYLLABUS.md")
        if syl is not None:
            for rel in lessons:
                m = re.match(r"^([A-Z]?\d+)-", Path(rel).stem)
                if m and not re.search(r"^### " + re.escape(m.group(1)) + r"\b", syl, re.M):
                    self.r.error("SYLLABUS.md", 1, "syllabus", f"lesson {m.group(1)} ({rel}) is not listed")

    def _front_matter(self, d: MdDoc, rel: str):
        if d.fm_text is None:
            self.r.error(rel, 1, "front-matter", "no YAML front matter (file must start with '---')")
            return None
        try:
            data = load_yaml(d.fm_text)
        except yaml.YAMLError as exc:
            line = 1 + (getattr(getattr(exc, "problem_mark", None), "line", 0) or 0) + 1
            self.r.error(rel, line, "front-matter", f"invalid YAML: {first_line(exc)}")
            return None
        if not isinstance(data, dict):
            self.r.error(rel, 1, "front-matter", "front matter must be a YAML mapping")
            return None
        return data

    @staticmethod
    def _fm_line(d: MdDoc, key: str) -> int:
        for i in range(1, d.fm_end):
            if d.lines[i].startswith(key + ":"):
                return i + 1
        return 1

    # -- fences / mermaid --------------------------------------------------- #

    def check_fences(self) -> None:
        for rel in self.md_files():
            d = self.doc(rel)
            if d is None:
                continue
            for f in d.unclosed:
                self.r.error(rel, f["start"] + 1, "fence",
                             f"code fence opened here ({f['char'] * f['len']}{f['info']}) is never closed")
            for f in d.fences:
                if f["info"].split(" ")[0:1] == ["mermaid"] and f["end"] is not None:
                    self.r.count("mermaid-blocks")
                    body = d.lines[f["start"] + 1:f["end"]]
                    real = [x for x in body if x.strip() and not x.strip().startswith("%%")]
                    if not real:
                        self.r.error(rel, f["start"] + 1, "mermaid", "empty mermaid block")

    def extract_mermaid(self, outdir: Path) -> int:
        outdir.mkdir(parents=True, exist_ok=True)
        n = 0
        manifest: list[str] = []
        for rel in self.md_files():
            d = self.doc(rel)
            if d is None:
                continue
            for f in d.fences:
                if f["info"].split(" ")[0:1] == ["mermaid"] and f["end"] is not None:
                    body = "\n".join(d.lines[f["start"] + 1:f["end"]]).strip("\n")
                    if not body.strip():
                        continue
                    n += 1
                    name = re.sub(r"[^A-Za-z0-9]+", "_", rel[:-3]).strip("_")
                    path = outdir / f"{name}__L{f['start'] + 1}.mmd"
                    path.write_text(body + "\n", encoding="utf-8")
                    manifest.append(f"{path.name}\t{rel}:{f['start'] + 1}")
        (outdir / "manifest.tsv").write_text("\n".join(manifest) + "\n", encoding="utf-8")
        return n

    # -- links ---------------------------------------------------------------- #

    def check_links(self) -> None:
        for rel in self.md_files():
            d = self.doc(rel)
            if d is None:
                continue
            base_dir = Path(rel).parent
            for lineno, line in d.prose_lines():
                for dest in link_targets(line):
                    self._check_one_link(rel, d, base_dir, lineno, dest)

    def _check_one_link(self, rel: str, d: MdDoc, base_dir: Path, lineno: int, dest: str) -> None:
        dest = dest.strip()
        if not dest or SCHEME_RE.match(dest) or dest.startswith("//"):
            return
        self.r.count("relative-links")
        path_part, _, frag = dest.partition("#")
        path_part = path_part.split("?", 1)[0]
        path_part = urllib.parse.unquote(path_part)
        frag = urllib.parse.unquote(frag)
        if path_part == "":
            target_rel = rel
        else:
            if path_part.startswith("/"):
                joined = os.path.normpath(path_part.lstrip("/"))
            else:
                joined = os.path.normpath(str(base_dir / path_part))
            if joined.startswith(".."):
                self.r.error(rel, lineno, "link", f"link leaves the repository: {dest}")
                return
            target_rel = joined.replace(os.sep, "/")
            if target_rel == ".":
                return
            if not (self.s.has_file(target_rel) or self.s.has_dir(target_rel)):
                self.r.error(rel, lineno, "link", f"broken link: {dest} (no such path in the public repo: {target_rel})")
                return
        if frag and target_rel.endswith(".md") and self.s.has_file(target_rel):
            if re.fullmatch(r"L\d+(?:C\d+)?(?:-L\d+(?:C\d+)?)?", frag):
                return
            td = d if target_rel == rel else self.doc(target_rel)
            if td is not None and frag.lower() not in td.anchors:
                self.r.error(rel, lineno, "anchor",
                             f"broken anchor: {dest} (no heading with slug '{frag}' in {target_rel})")

    # -- labs ----------------------------------------------------------------- #

    def check_labs(self) -> None:
        lab_dirs = sorted({r.split("/")[1] for r in self.s.rel_set
                           if r.startswith("labs/") and r.count("/") >= 2})
        for name in lab_dirs:
            self.r.count("labs")
            readme = f"labs/{name}/README.md"
            if not self.s.has_file(readme):
                self.r.error(f"labs/{name}", 0, "lab", "lab directory has no README.md")
                continue
            d = self.doc(readme)
            idx = None
            for lineno, level, text in d.headings:
                if re.search(r"test\s+status", text, re.I):
                    idx = lineno
                    break
            if idx is None:
                self.r.error(readme, 1, "lab", "missing 'Test status' section")
                continue
            level = next(lv for ln, lv, _ in d.headings if ln == idx)
            body = []
            for i in range(idx, len(d.lines)):
                nxt = HEADING_RE.match(d.lines[i]) if not d.in_fence[i] else None
                if nxt and len(nxt.group(1)) <= level:
                    break
                body.append(d.lines[i])
            joined = "\n".join(body).lower()
            if not any(lbl in joined for lbl in LAB_STATUS_LABELS):
                self.r.error(readme, idx, "lab",
                             "'Test status' must state one of: " + ", ".join(LAB_STATUS_LABELS))
        referenced: set[str] = set()
        for rel in self.lessons():
            d = self.doc(rel)
            if d is None:
                continue
            for i in range(d.fm_end, len(d.lines)):
                for m in re.finditer(r"(?<![\w-])labs/([0-9]{2}-[A-Za-z0-9-]+)", d.lines[i]):
                    name = m.group(1)
                    referenced.add(name)
                    if not self.s.has_dir(f"labs/{name}"):
                        self.r.error(rel, i + 1, "lab", f"referenced lab directory labs/{name} does not exist")
        for name in lab_dirs:
            if name not in referenced:
                self.r.warn(f"labs/{name}", 0, "lab", "lab is not referenced from any lesson")

    # -- YAML / JSON ---------------------------------------------------------- #

    def check_data_files(self) -> None:
        for rel in sorted(self.s.rel_set):
            low = rel.lower()
            is_yaml = low.endswith((".yaml", ".yml"))
            is_json = low.endswith(".json")
            if not (is_yaml or is_json):
                continue
            text = self.s.read(rel)
            if text is None:
                continue
            if is_json:
                self.r.count("json-files")
                try:
                    json.loads(text)
                except ValueError as exc:
                    self.r.error(rel, getattr(exc, "lineno", 1), "json", f"invalid JSON: {exc}")
                continue
            self.r.count("yaml-files")
            try:
                docs = list(load_yaml_all(text))
            except yaml.YAMLError as exc:
                line = 1 + (getattr(getattr(exc, "problem_mark", None), "line", 0) or 0)
                self.r.error(rel, line, "yaml", f"invalid YAML: {first_line(exc)}")
                continue
            if re.fullmatch(r"labs/[^/]+/compose\.ya?ml", rel):
                self.r.count("compose-files")
                svc = docs[0].get("services") if docs and isinstance(docs[0], dict) else None
                if not isinstance(svc, dict) or not svc:
                    self.r.error(rel, 1, "compose", "compose file has no 'services' mapping")
                else:
                    for name, body in svc.items():
                        if not isinstance(body, dict) or not ("image" in body or "build" in body):
                            self.r.error(rel, 1, "compose", f"service '{name}' has neither 'image' nor 'build'")
            if rel == "course.yaml":
                if not docs or not isinstance(docs[0], dict) or "course_id" not in docs[0]:
                    self.r.error(rel, 1, "course-yaml", "course.yaml must be a mapping with 'course_id'")

    # -- content scans ---------------------------------------------------------- #

    def check_text_hygiene(self) -> None:
        for rel in self.s.text_files():
            text = self.s.read(rel)
            if text is None:
                continue
            self.r.count("text-files-scanned")
            name = Path(rel).name
            if name in SECRET_FILENAMES or Path(rel).suffix.lower() in SECRET_SUFFIXES:
                self.r.error(rel, 1, "secret", f"file name '{name}' looks like a credential file")
            for i, line in enumerate(text.split("\n"), start=1):
                self._scan_line(rel, i, line)
        for rel in sorted(self.s.rel_set):
            name = Path(rel).name
            if (name in SECRET_FILENAMES or Path(rel).suffix.lower() in SECRET_SUFFIXES) \
                    and rel not in self.s.text_files():
                self.r.error(rel, 1, "secret", f"file name '{name}' looks like a credential file")

    def _scan_line(self, rel: str, i: int, line: str) -> None:
        for label, rx in SECRET_PATTERNS:
            for m in rx.finditer(line):
                if SECRET_ALLOW_RE.search(m.group(0)):
                    continue
                self.r.error(rel, i, "secret", f"possible {label}: '{m.group(0)[:8]}...' (value not shown)")
        for rx in ATTRIBUTION_RES:
            if rx.search(line):
                self.r.error(rel, i, "attribution", "AI-assistant attribution string; remove it")
                break
        no_urls = URL_RE.sub(lambda m: " " * len(m.group(0)), line)
        m = PRIVATE_REPO_RE.search(no_urls) or HOSTED_PRIVATE_REPO_RE.search(line)
        if m:
            self.r.error(rel, i, "private-ref", f"reference to a private repository name: {m.group(0)}")
        m = PRIVATE_PATH_RE.search(no_urls)
        if m:
            self.r.error(rel, i, "private-ref", f"reference to a private path or tool: '{m.group(0)}'")
        for hm in HOME_PATH_RE.finditer(no_urls):
            user = next(g for g in hm.groups() if g)
            if user.lower() not in GENERIC_HOME_USERS:
                self.r.error(rel, i, "private-ref", "absolute path into a personal home directory")
                break
        if not rel.startswith("labs/") and PRIVATE_TOOL_RE.search(no_urls):
            self.r.warn(rel, i, "private-ref",
                        f"mentions a tool path that is not in the public repo: '{PRIVATE_TOOL_RE.search(no_urls).group(0)}'")

    # -- references --------------------------------------------------------------- #

    def check_references(self) -> None:
        ref_doc = self.doc("REFERENCES.md")
        if ref_doc is None:
            self.r.error("REFERENCES.md", 0, "references", "REFERENCES.md is missing")
            return
        known = set()
        for i, line in enumerate(ref_doc.lines):
            for u in urls_in(line):
                known.add(u)
        for rel in self.lessons():
            d = self.doc(rel)
            if d is None:
                continue
            start = None
            for lineno, level, text in d.headings:
                if level == 2 and text.strip().lower() == "references":
                    start = lineno
                    break
            if start is None:
                self.r.error(rel, 1, "references", "lesson has no '## References' section")
                continue
            entry_first: tuple[int, str] | None = None
            entries: list[tuple[int, str]] = []
            for i in range(start, len(d.lines)):
                line = d.lines[i]
                if i + 1 > start and not d.in_fence[i] and re.match(r"^#{1,2} ", line):
                    break
                if re.match(r"^ {0,3}(?:\d+\.|\[\d+\])\s", line):
                    if entry_first is not None:
                        entries.append(entry_first)
                    entry_first = None
                if entry_first is None:
                    found = urls_in(line)
                    if found:
                        entry_first = (i + 1, found[0])
            if entry_first is not None:
                entries.append(entry_first)
            # Only the primary (first) URL of each entry must be in REFERENCES.md;
            # later URLs in parenthetical notes ("checked in the author's copy ...") are exempt.
            for lineno, u in entries:
                self.r.count("reference-urls")
                if u not in known:
                    self.r.error(rel, lineno, "references", f"primary URL not listed in REFERENCES.md: {u}")


def urls_in(line: str) -> list[str]:
    out = []
    for m in URL_RE.finditer(line):
        u = m.group(0)
        while u and (u[-1] in ".,;:'\"!?*" or (u[-1] == ")" and u.count(")") > u.count("("))
                     or (u[-1] == "]" and u.count("]") > u.count("["))):
            u = u[:-1]
        out.append(u)
    return out


def first_line(exc: Exception) -> str:
    problem = getattr(exc, "problem", None)
    if problem:
        context = getattr(exc, "context", None)
        return f"{context}: {problem}" if context else str(problem)
    text = str(exc).strip()
    return text.splitlines()[0] if text else exc.__class__.__name__


class _UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader that rejects duplicate mapping keys (PyYAML accepts them silently)."""


def _construct_unique(loader, node, deep=False):
    seen = set()
    for key_node, _ in node.value:
        if key_node.tag == "tag:yaml.org,2002:merge":
            continue  # '<<: *anchor' merge keys may legitimately repeat
        key = loader.construct_object(key_node, deep=deep)
        try:
            hash(key)
        except TypeError:
            continue
        if key in seen:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping", node.start_mark,
                f"found duplicate key {key!r}", key_node.start_mark)
        seen.add(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)


_UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique)


def load_yaml(text: str):
    return yaml.load(text, Loader=_UniqueKeyLoader)


def load_yaml_all(text: str):
    return yaml.load_all(text, Loader=_UniqueKeyLoader)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

CHECKS = [
    ("lessons: front matter, companions, syllabus", "check_lessons"),
    ("markdown: code fences, mermaid blocks", "check_fences"),
    ("markdown: relative links and anchors", "check_links"),
    ("labs: README, test status, lesson references", "check_labs"),
    ("data: YAML / compose / JSON parse", "check_data_files"),
    ("hygiene: secrets, attribution, private references", "check_text_hygiene"),
    ("references: lesson URLs listed in REFERENCES.md", "check_references"),
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent,
                    help="repository root (default: parent of tools/)")
    ap.add_argument("--extract-mermaid", metavar="DIR", type=Path,
                    help="write every non-empty mermaid block to DIR/*.mmd and exit")
    args = ap.parse_args(argv)
    if not args.root.is_dir():
        print(f"error: {args.root} is not a directory", file=sys.stderr)
        return 2

    t0 = time.monotonic()
    surface = Surface(args.root)
    report = Report()
    checker = Checker(surface, report)

    if args.extract_mermaid:
        checker.check_fences()  # reports unclosed fences / empty blocks
        n = checker.extract_mermaid(args.extract_mermaid)
        for path, line, rule, msg in report.errors:
            print(f"{path}:{line}: [{rule}] {msg}")
        print(f"extracted {n} mermaid block(s) to {args.extract_mermaid}")
        return 1 if report.errors else 0

    for title, method in CHECKS:
        before = len(report.errors)
        getattr(checker, method)()
        status = "ok" if len(report.errors) == before else f"{len(report.errors) - before} error(s)"
        print(f"  {title}: {status}")

    for path, line, rule, msg in report.warnings:
        print(f"{path}:{line}: warning [{rule}] {msg}")
    for path, line, rule, msg in sorted(report.errors):
        print(f"{path}:{line}: error [{rule}] {msg}")
    c = report.counts
    print(f"\nchecked {c.get('lessons', 0)} lessons, {c.get('labs', 0)} labs, "
          f"{c.get('relative-links', 0)} relative links, {c.get('mermaid-blocks', 0)} mermaid blocks, "
          f"{c.get('yaml-files', 0)} YAML + {c.get('json-files', 0)} JSON files "
          f"({c.get('compose-files', 0)} compose), {c.get('text-files-scanned', 0)} text files scanned, "
          f"{c.get('reference-urls', 0)} reference URLs in {time.monotonic() - t0:.1f}s")
    print(f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
