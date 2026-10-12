"""Scan source files for TODO-style markers. Offline, read-only, stdlib only."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from pathlib import Path

MARKER_RE = re.compile(
    r"\b(?P<tag>TODO|FIXME|XXX|HACK)\b"
    r"(?:\((?P<owner>[^)]*)\))?[:\s]?"
    r"(?P<text>.*?)(?=\b(?:TODO|FIXME|XXX|HACK)\b|$)"
)
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"}
BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".gz", ".ico", ".woff", ".woff2", ".ttf"}
MAX_BYTES = 1024 * 1024


@dataclass(frozen=True)
class Marker:
    file: str
    line: int
    tag: str
    owner: str | None
    text: str


def scan_text(text: str, file: str = "<text>") -> list[Marker]:
    markers: list[Marker] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for match in MARKER_RE.finditer(line):
            markers.append(Marker(file, number, match.group("tag"), match.group("owner"), match.group("text").strip()))
    return markers


def iter_files(root: Path):
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if path.is_file() and path.suffix.lower() not in BINARY_SUFFIXES and path.stat().st_size <= MAX_BYTES:
            yield path


def _excluded(rel: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(rel.rsplit("/", 1)[-1], pat) for pat in patterns)


def scan_repo(root: str | Path, exclude: tuple[str, ...] = ()) -> list[Marker]:
    """Scan text files under root; `exclude` globs skip paths (matched on full path or basename)."""
    base = Path(root).resolve()
    markers: list[Marker] = []
    for path in sorted(iter_files(base)):
        rel = path.relative_to(base).as_posix()
        if _excluded(rel, exclude):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        markers.extend(scan_text(text, rel))
    return markers


def violations(markers: list[Marker], block_tags: set[str], require_owner: bool) -> list[Marker]:
    """Markers that should fail CI: blocking tags, or any unowned marker when require_owner is set."""
    result = []
    for m in markers:
        if m.tag in block_tags or (require_owner and not m.owner):
            result.append(m)
    return result
