# js-function-scanner

A lightweight, dependency-free Python CLI tool for scanning JavaScript files and extracting top-level function names.

## Features

- **Zero Dependencies**: Uses only the Python standard library
- **Fast Execution**: Regex-based parsing without heavy AST overhead
- **Comprehensive Pattern Support**: Function declarations, expressions, arrow functions, classes, and ES6 exports
- **Configurable Output**: Sort alphabetically or preserve file order
- **Smart Exclusions**: Exclude directories or files with glob patterns (`*`, `?`, `[seq]`, `**`)
- **Common Exclusions**: Opt-in to exclude common directories (node_modules, dist, build, etc.) with `--exclude-common`
- **Clean Output**: Strips comments to avoid false positives
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

```bash
# Clone the repository
git clone https://github.com/bkuz114/js-function-scanner.git
cd js-function-scanner

# Make the script executable (Linux/macOS)
chmod +x scan_js_functions.py

# Optional: Add to PATH for system-wide access
# Linux/macOS:
sudo ln -s $(pwd)/scan_js_functions.py /usr/local/bin/js-func-scan

# Windows: Add the directory to your PATH environment variable
```

## Usage

### Basic Usage

```bash
# Scan current directory recursively
python scan_js_functions.py

# Scan a specific directory
python scan_js_functions.py /path/to/your/project

# Scan and sort functions alphabetically
python scan_js_functions.py /path/to/your/project --sort alpha

# Hide files with no top-level functions
python scan_js_functions.py /path/to/your/project --hide-empty

# Non-recursive scan (top-level only)
python scan_js_functions.py /path/to/project --no-recursive

# Exclude common directories and files
python scan_js_functions.py /path/to/project --exclude-common

# Custom exclusions with glob patterns
python scan_js_functions.py /path/to/project --exclude "**/test/**" --exclude "*.min.js"

# Combine common + custom exclusions
python scan_js_functions.py /path/to/project --exclude-common --exclude "legacy/**"
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `directory` | Directory to scan (default: current directory) |
| `--sort {alpha,found}` | Sort order: "alpha" (alphabetical) or "found" (order found) (default: "found") |
| `--exclude PATTERN` |	Glob pattern to exclude (can be specified multiple times). Supports \*, ?, [seq], and \*\* |
| `--exclude-common` | Exclude common directories and files (node_modules, dist, build, .git, etc.) |
| `--no-recursive` | Disable recursive scanning (only scan the specified directory, not subdirectories) |
| `--hide-empty` | Hide files with no top-level functions |
| `-h, --help` | Show help message and exit |

### Supported JavaScript Patterns

The scanner recognizes the following patterns at the top level:

```javascript
// Function declarations
function calculateTotal(items) { ... }

// Async function declarations
async function fetchData(url) { ... }

// Function expressions
const formatDate = function(date) { ... };

// Arrow functions
const validateEmail = (email) => { ... };

// Async arrow functions
const getUserData = async (id) => { ... };

// Classes
class UserModel { ... }

// ES6 exports
export function helperFunction() { ... }
export default function main() { ... }
```

## Example Output

```
Found 3 JavaScript file(s):

================================================================================

📁 src/utils.js
   (4 top-level function(s))
   1. calculateTotal
   2. formatDate
   3. getUserData
   4. validateEmail

📁 src/components/App.js
   (2 top-level function(s))
   1. App
   2. useCustomHook

📁 src/config.js
   (0 top-level function(s))
   (no top-level functions found)

================================================================================
```

## Use Cases

- **Codebase Exploration**: Quickly understand the API surface of a JavaScript project
- **Documentation Generation**: Extract function names for documentation scaffolding
- **Code Review**: Identify exported functions and their distribution across files
- **Refactoring Planning**: Locate functions that may need reorganization
- **Onboarding**: Help new team members navigate unfamiliar codebases

## Development

### Running Tests

```bash
# Run pytest suite
pytest tests/

# Validate against your own codebase
python scan_js_functions.py /path/to/your/js/project
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your changes maintain:
- Zero external dependencies (standard library only)
- Python 3.6+ compatibility
- Clear, readable code with appropriate comments

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Author

Ivan

## Acknowledgments

- Inspired by the need for quick JavaScript codebase analysis without heavy tooling
- Built with Python's `pathlib` and `re` modules for cross-platform compatibility
