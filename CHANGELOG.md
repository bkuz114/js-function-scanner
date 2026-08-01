# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-08-01

### Added
- `--exclude` with glob pattern support (\*, ?, [seq], \*\*) for flexible file and directory exclusions
- `--exclude-common` flag to opt-in to predefined exclusion patterns (node_modules, dist, build, .git, etc.)
- Test suite for exclusion patterns using pytest
- File-level documentation updated with new features
- README updated with new CLI options and usage examples

### Planned
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
