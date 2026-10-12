# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.1.2] - 2026-10-13

### Added

- Report multiple markers found on the same line as separate findings.
- Add wheel installation instructions, release badges, and a tag-based release workflow with SHA-256 checksums.
- Pin CI actions to verified commit SHAs and add version regression coverage.

### Fixed

- A blocking marker after another marker on the same line is no longer hidden from CI.

## [0.1.1] - 2026-10-11

### Added

- CI now also runs the test suite on Windows (windows-latest), not only Ubuntu.
- `--exclude GLOB` (repeatable) to skip paths such as generated docs.


## [0.1.0] - 2026-10-11

### Added

- Scan text files for TODO, FIXME, XXX and HACK markers, skipping vendor folders and binaries.
- `--block TAG` fails the run for chosen tags; `--require-owner` requires `TODO(name)` style owners.
- `--json` output and a summary line per run.

[Unreleased]: https://github.com/GhosTnever-lkm/todo-scan/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/GhosTnever-lkm/todo-scan/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/GhosTnever-lkm/todo-scan/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/GhosTnever-lkm/todo-scan/releases/tag/v0.1.0
