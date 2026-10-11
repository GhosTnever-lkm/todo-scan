import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from todo_scan.cli import main
from todo_scan.core import scan_repo, scan_text, violations


class ScanTests(unittest.TestCase):
    def test_finds_tags_with_and_without_owner(self):
        found = scan_text("# TODO(alice): one\n# FIXME two\nnothing here\n")
        self.assertEqual([(m.line, m.tag, m.owner) for m in found], [(1, "TODO", "alice"), (2, "FIXME", None)])

    def test_word_boundary_ignores_substrings(self):
        self.assertEqual(scan_text("TODOS are not markers\nmytodo here\n"), [])

    def test_violations(self):
        found = scan_text("TODO(a): x\nFIXME: y\nHACK: z\n")
        self.assertEqual({m.tag for m in violations(found, {"FIXME"}, False)}, {"FIXME"})
        self.assertEqual(len(violations(found, set(), True)), 2)

    def test_repo_scan_skips_vendor_and_binary(self):
        root = Path(tempfile.mkdtemp())
        (root / "node_modules").mkdir()
        (root / "node_modules" / "x.js").write_text("// TODO: vendor\n", encoding="utf-8")
        (root / "app.py").write_text("# TODO(bob): real\n", encoding="utf-8")
        (root / "logo.png").write_bytes(b"TODO")
        markers = scan_repo(root)
        self.assertEqual([m.file for m in markers], ["app.py"])


class CliTests(unittest.TestCase):
    def run_cli(self, argv):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main(argv)
        return code, buf.getvalue()

    def test_clean_repo_exit_zero_and_summary(self):
        root = Path(tempfile.mkdtemp())
        (root / "a.txt").write_text("hello\n", encoding="utf-8")
        code, out = self.run_cli([str(root)])
        self.assertEqual(code, 0)
        self.assertIn("markers: 0", out)

    def test_block_tag_fails(self):
        root = Path(tempfile.mkdtemp())
        (root / "a.py").write_text("# FIXME: boom\n", encoding="utf-8")
        self.assertEqual(self.run_cli(["--block", "FIXME", str(root)])[0], 1)
        self.assertEqual(self.run_cli([str(root)])[0], 0)

    def test_require_owner_and_json(self):
        root = Path(tempfile.mkdtemp())
        (root / "a.py").write_text("# TODO: no owner\n", encoding="utf-8")
        code, out = self.run_cli(["--require-owner", "--json", str(root)])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["violations"], 1)

    def test_bad_path(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.run_cli(["/no/such"])[0], 2)


if __name__ == "__main__":
    unittest.main()
