# RustMatch

[![PyPI version](https://badge.fury.io/py/rustmatch.svg)](https://badge.fury.io/py/rustmatch)
[![Python](https://img.shields.io/pypi/pyversions/rustmatch.svg)](https://pypi.org/project/rustmatch/)
[![License](https://img.shields.io/badge/license-MIT%2FApache--2.0-blue.svg)](LICENSE)

High-performance template matching library for Python, powered by Rust.

## ✨ Zero Dependencies!

Unlike other image processing libraries, RustMatch has **NO Python dependencies**:
- ❌ No numpy required
- ❌ No pillow required  
- ❌ No opencv required
- ✅ Just pure Rust performance!

This makes your packaged executables (PyInstaller, Nuitka, etc.) **much smaller** (~5MB vs ~50MB with numpy).

## Features

- 🚀 **Blazing Fast**: 10-50x faster than OpenCV's template matching
- 🎯 **High Accuracy**: Normalized Cross-Correlation (NCC) algorithm
- 📦 **Zero Dependencies**: No numpy/pillow needed
- 🧵 **Multi-threaded**: Automatic parallel processing
- 📐 **Smart Search**: Image pyramid acceleration for large images

## Installation

```bash
pip install rustmatch
```

## Quick Start

```python
import rustmatch

# Find single match (using file paths - recommended!)
result = rustmatch.find("screenshot.png", "button.png", threshold=0.8)
if result:
    print(f"Found at ({result.x}, {result.y}), confidence: {result.confidence:.2%}")

# Find all matches
results = rustmatch.find_all("screenshot.png", "icon.png", threshold=0.8, max_count=10)
for r in results:
    print(f"Match at ({r.x}, {r.y})")
```

### Using Image Bytes

```python
# Read image files as bytes
with open("screenshot.png", "rb") as f:
    source = f.read()
with open("button.png", "rb") as f:
    template = f.read()

# Match using bytes (useful for screenshots from memory)
result = rustmatch.find_bytes(source, template, threshold=0.8)
```

### Using Raw Pixel Data

```python
# For advanced users who handle image loading themselves
result = rustmatch.find_raw(
    source_pixels,      # grayscale pixels as list/bytes (0-255)
    source_width,
    source_height,
    template_pixels,
    template_width,
    template_height,
    threshold=0.8
)
```

## API Reference

### Functions

| Function | Description |
|----------|-------------|
| `find(source, template, threshold=0.8)` | Find best match using file paths |
| `find_all(source, template, threshold=0.8, max_count=10)` | Find all matches using file paths |
| `find_bytes(source, template, threshold=0.8)` | Find best match using image bytes |
| `find_all_bytes(source, template, threshold=0.8, max_count=10)` | Find all matches using image bytes |
| `find_raw(...)` | Find match using raw pixel data |
| `get_size(path)` | Get image dimensions (width, height) |
| `set_threads(num)` | Set thread count (0=auto) |
| `version()` | Get library version |

### MatchResult

```python
result = rustmatch.find("screen.png", "button.png")
if result:
    result.x          # X coordinate (left edge)
    result.y          # Y coordinate (top edge)
    result.confidence # Match confidence (0.0-1.0)
    result.to_tuple() # (x, y, confidence)
    result.bbox(w, h) # (x, y, width, height)
```

## Threshold Guide

| Threshold | Use Case |
|-----------|----------|
| 0.95+ | Exact match, identical images |
| 0.85-0.95 | High confidence, minor variations |
| 0.75-0.85 | Moderate confidence, some noise |
| < 0.75 | May produce false positives |

## Performance

| Image Size | Template | Time |
|------------|----------|------|
| 1920×1080 | 64×64 | ~15ms |
| 1602×364 | 15×16 | ~12ms |

## Building from Source

```bash
# Requires Rust toolchain
pip install maturin
git clone https://github.com/JunjieDuan/rustmatch.git
cd rustmatch
maturin build --release
pip install target/wheels/rustmatch-*.whl
```
## Disclaimer

This software is provided "as is", without warranty of any kind. Use at your own risk.

- This is an independent open-source project, not affiliated with or endorsed by the Rust Foundation or the Rust programming language team.
- The "Rust" name is used to indicate that this library is implemented in the Rust programming language.
- The authors are not responsible for any damages or losses resulting from the use of this software.
- This library is intended for legitimate use cases such as UI automation, testing, and image analysis. Users are responsible for ensuring their use complies with applicable laws and regulations.

## License

Dual-licensed under MIT or Apache-2.0.

