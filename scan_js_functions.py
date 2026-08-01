#!/usr/bin/env python3
"""
JavaScript Top-Level Function Scanner

A lightweight, dependency-free CLI tool for scanning JavaScript files and
extracting top-level function names. Useful for codebase exploration,
documentation generation, and quick API surface analysis.

Features:
    - Recursive directory scanning (with non-recursive option)
    - Extract function declarations, expressions, arrow functions, and classes
    - Support for async functions and ES6 export syntax
    - Smart comment stripping to avoid false positives
    - Output sorted alphabetically or in file-order
    - Exclusion patterns with glob support (*, ?, [seq], **)
    - Opt-in common exclusions (node_modules, dist, build, etc.)
    - Zero external dependencies (Python standard library only)

Usage Examples:
    # Scan current directory recursively
    python scan_js_functions.py

    # Scan specific directory with alphabetical sorting
    python scan_js_functions.py /path/to/project --sort alpha

    # Non-recursive scan (top-level only)
    python scan_js_functions.py /path/to/project --no-recursive

    # Exclude common directories and files
    python scan_js_functions.py /path/to/project --exclude-common

    # Custom exclusions with glob patterns
    python scan_js_functions.py /path/to/project --exclude "**/test/**" --exclude "*.min.js"

    # Combine exclusions: common + custom
    python scan_js_functions.py /path/to/project --exclude-common --exclude "legacy/**"

    # Hide files with no top-level functions
    python scan_js_functions.py /path/to/project --hide-empty

Exit Codes:
    0 - Success (functions found and processed)
    1 - Error (invalid directory, no files found, etc.)

Supported JavaScript Patterns:
    - Function declarations:        function name() { ... }
    - Async function declarations:  async function name() { ... }
    - Function expressions:         const name = function() { ... }
    - Arrow functions:              const name = () => { ... }
    - Async arrow functions:        const name = async () => { ... }
    - Class definitions:            class Name { ... }
    - Export declarations:          export function name() { ... }
    - Export default:               export default function name() { ... }

See Also:
    - GitHub: https://github.com/bkuz114/js-function-scanner
    - For bug reports or feature requests, please open an issue.

Author: K. Ivan
License: MIT
"""

import os
import re
import argparse
import glob
from pathlib import Path

# Common exclusion patterns (opt-in via --exclude-common)
COMMON_EXCLUDES = [
    "**/node_modules/**",
    "**/dist/**",
    "**/build/**",
    "**/.git/**",
    "**/__pycache__/**",
    "**/coverage/**",
    "**/.next/**",
    "**/.nuxt/**",
    "**/vendor/**",
    "*.min.js",
]


def extract_top_level_functions(content, sort_order="found"):
    """
    Extract top-level function names from JavaScript content.
    Handles function declarations, function expressions, and arrow functions.
    """
    functions = []

    # Remove multi-line comments to avoid false positives
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    # Remove single-line comments
    content = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)

    # Pattern for function declarations: function name() { ... }
    # Also handles async functions
    func_decl_pattern = r"^\s*(?:export\s+)?(?:async\s+)?function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\([^)]*\)\s*{"

    # Pattern for function expressions assigned to variables: const/let/var name = function() { ... }
    func_expr_pattern = r"^\s*(?:export\s+)?(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:async\s+)?function\s*(?:\([^)]*\)|[a-zA-Z_$][a-zA-Z0-9_$]*)\s*{"

    # Pattern for arrow functions assigned to variables: const name = () => { ... }
    arrow_func_pattern = r"^\s*(?:export\s+)?(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>\s*{"

    # Pattern for class methods (top-level class definitions)
    class_pattern = r"^\s*(?:export\s+)?class\s+([a-zA-Z_$][a-zA-Z0-9_$]*)"

    # Pattern for exported functions: export function name() { ... }
    export_decl_pattern = r"^\s*export\s+(?:async\s+)?function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\([^)]*\)\s*{"

    # Pattern for export default function (anonymous or named)
    export_default_pattern = r"^\s*export\s+default\s+(?:async\s+)?function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\([^)]*\)\s*{"

    # Combine all patterns
    all_patterns = [
        (func_decl_pattern, "function declaration"),
        (func_expr_pattern, "function expression"),
        (arrow_func_pattern, "arrow function"),
        (class_pattern, "class"),
        (export_decl_pattern, "exported function"),
        (export_default_pattern, "export default function"),
    ]

    # Process line by line to identify top-level functions
    lines = content.split("\n")
    bracket_count = 0
    in_function = False
    current_function = None

    for line_num, line in enumerate(lines, 1):
        # Skip if we're inside a function or block (not top-level)
        if bracket_count > 0:
            bracket_count += line.count("{") - line.count("}")
            if bracket_count == 0:
                in_function = False
                current_function = None
            continue

        # Check each pattern
        for pattern, func_type in all_patterns:
            match = re.match(pattern, line.strip())
            if match:
                func_name = match.group(1)
                # Check if it's truly top-level (not inside another function)
                if not in_function and func_name not in functions:
                    functions.append(func_name)
                    # Check if this function has a body with braces
                    if "{" in line:
                        bracket_count = line.count("{") - line.count("}")
                        if bracket_count > 0:
                            in_function = True
                            current_function = func_name
                break

    # Sort based on parameter
    if sort_order == "alpha":
        return sorted(set(functions))
    elif sort_order == "found":
        # Remove duplicates while preserving order
        seen = set()
        return [x for x in functions if not (x in seen or seen.add(x))]
    else:
        raise ValueError(f"invalid sort_order {sort_order}")


def get_excluded_files(scan_root, exclude_patterns, exclude_common=False):
    """
    Return set of .js files (as Path objects relative to scan_root) that match any exclusion pattern.

    Args:
        scan_root: Path object for the root directory being scanned
        exclude_patterns: List of user-specified exclusion patterns
        exclude_common: Boolean, whether to apply COMMON_EXCLUDES

    Returns:
        Set of relative paths (as strings) to exclude
    """
    all_patterns = list(exclude_patterns) if exclude_patterns else []
    if exclude_common:
        all_patterns.extend(COMMON_EXCLUDES)

    if not all_patterns:
        return set()

    excluded = set()
    scan_root_path = Path(scan_root)

    for pattern in all_patterns:
        # Build the full glob pattern from the scan root
        full_pattern = str(scan_root_path / pattern)
        matches = glob.glob(full_pattern, recursive=True)
        for match in matches:
            match_path = Path(match)

            # If it's a .js file, add it directly
            if match_path.suffix.lower() == ".js":
                rel_path = match_path.relative_to(scan_root_path)
                excluded.add(rel_path)

            # If it's a directory, collect all .js files under it
            elif match_path.is_dir():
                for js_file in match_path.rglob("*.js"):
                    rel_path = js_file.relative_to(scan_root_path)
                    excluded.add(rel_path)

    return excluded


def scan_js_files(
    directory,
    show_empty=True,
    sort_order="found",
    recursive=True,
    exclude_patterns=None,
    exclude_common=False,
):
    """
    Scan directory for .js files and extract top-level function names.
    """
    js_files = []
    directory_path = Path(directory)

    if not directory_path.exists():
        print(f"Error: Directory '{directory}' does not exist.")
        return

    if not directory_path.is_dir():
        print(f"Error: '{directory}' is not a directory.")
        return

    # Get excluded files
    excluded_files = get_excluded_files(
        directory_path, exclude_patterns, exclude_common
    )

    if exclude_common:
        print(f"Excluding common patterns: {', '.join(COMMON_EXCLUDES)}")

    if exclude_patterns:
        print(f"Excluding user patterns: {', '.join(exclude_patterns)}")

    # Collect files with exclusions applied
    if recursive:
        iterator = directory_path.rglob("*.js")
    else:
        iterator = directory_path.glob("*.js")

    for file_path in iterator:
        if file_path.is_file():
            # Get relative path for matching
            rel_path = file_path.relative_to(directory_path)
            if not is_excluded(rel_path, exclude_patterns, exclude_common):
                js_files.append(file_path)

    if not js_files:
        print(f"No .js files found in '{directory}' (after applying exclusions).")
        return

    print(f"Found {len(js_files)} JavaScript file(s):\n")
    print("=" * 80)

    for js_file in sorted(js_files):
        try:
            with open(js_file, "r", encoding="utf-8") as f:
                content = f.read()

            functions = extract_top_level_functions(content, sort_order)

            # Display results
            relative_path = js_file.relative_to(directory_path)
            print(f"\n📁 {relative_path}")
            print(f"   ({len(functions)} top-level function(s))")

            if functions:
                for i, func in enumerate(functions, 1):
                    print(f"   {i}. {func}")
            elif show_empty:
                print("   (no top-level functions found)")

        except Exception as e:
            print(f"\n❌ Error reading {js_file}: {e}")

    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Scan a directory for JavaScript files and list top-level functions."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--hide-empty",
        action="store_true",
        help="Hide files with no top-level functions",
    )
    parser.add_argument(
        "--sort",
        choices=["alpha", "found"],
        default="found",
        help='Sort order: "alpha" (alphabetical) or "found" (order found) (default: "found")',
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Disable recursive scanning (only scan the specified directory, not subdirectories)",
    )
    parser.add_argument(
        "--exclude-common",
        action="store_true",
        help="Exclude common directories and files: " + ", ".join(COMMON_EXCLUDES),
    )
    parser.add_argument(
        "--exclude",
        action="append",
        dest="exclude_patterns",
        default=[],
        help="Glob pattern to exclude (can be specified multiple times). Supports *, ?, [seq], and **",
    )

    args = parser.parse_args()
    show_empty = not args.hide_empty

    scan_js_files(
        args.directory,
        show_empty,
        args.sort,
        not args.no_recursive,
        args.exclude_patterns,
        args.exclude_common,
    )


if __name__ == "__main__":
    main()
