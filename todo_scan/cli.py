"""todo-scan [PATH] [--block TAG ...] [--require-owner] [--json]"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from . import __version__
from .core import scan_repo, violations


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="todo-scan", description="Report TODO/FIXME markers and fail CI on blocking ones (offline).")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("--block", action="append", default=[], metavar="TAG", help="tag that fails the run, e.g. FIXME (repeatable)")
    p.add_argument("--require-owner", action="store_true", help="every marker needs an owner, e.g. TODO(alice)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--version", action="version", version=__version__)
    args = p.parse_args(argv)
    if not Path(args.path).is_dir():
        print(f"todo-scan: not a directory: {args.path}", file=sys.stderr)
        return 2
    markers = scan_repo(args.path)
    bad = violations(markers, set(args.block), args.require_owner)
    if args.json:
        print(json.dumps({"markers": [asdict(m) for m in markers], "violations": len(bad)}, indent=2, ensure_ascii=False))
    else:
        for m in markers:
            owner = f"({m.owner})" if m.owner else ""
            print(f"{m.file}:{m.line}: {m.tag}{owner} {m.text}".rstrip())
        counts = Counter(m.tag for m in markers)
        summary = ", ".join(f"{t}={n}" for t, n in sorted(counts.items())) or "none"
        print(f"markers: {len(markers)} ({summary}); violations: {len(bad)}")
    return 1 if bad else 0
