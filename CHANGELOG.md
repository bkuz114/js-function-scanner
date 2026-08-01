# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- `--exclude` with glob pattern support (\*, ?, [seq], \*\*)
- `--exclude-common` flag for opt-in common exclusions
- Single file targeting support

## [1.0.0] - 2026-07-31

### Added
- Initial implementation of JavaScript function scanner
- Extract top-level function declarations, expressions, arrow functions, and classes
- Support for async functions and ES6 export syntax
- Comment stripping to avoid false positives
- Alphabetical and file-order sorting options via `--sort`
- Directory recursion (default behavior)
- `--hide-empty` flag to suppress files with no functions
- `--no-recursive` flag for disabling recursive scanning
- Dependency-free (Python standard library only)
- README.md, MIT License
