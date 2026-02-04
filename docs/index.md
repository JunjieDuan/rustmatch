# RustMatch Documentation

High-performance template matching library for Python, powered by Rust.

## Overview

RustMatch provides fast and accurate template matching using the Normalized Cross-Correlation (NCC) algorithm. It's designed for applications like:

- UI automation and testing
- Game bot development
- Image analysis
- Object detection in screenshots

## Key Features

- **10-50x faster** than OpenCV's template matching
- **Zero dependencies** - no numpy or pillow required!
- **Multi-threaded** parallel processing
- **Image pyramid** acceleration for large images
- **Simple API** with type hints

## Quick Start

```python
import rustmatch

# Find single match using file paths
result = rustmatch.find("screenshot.png", "button.png", threshold=0.8)
if result:
    print(f"Found at ({result.x}, {result.y})")

# Find all matches
results = rustmatch.find_all("screenshot.png", "icon.png", max_count=10)
for r in results:
    print(f"Match at ({r.x}, {r.y})")
```

## Contents

```{toctree}
:maxdepth: 2

installation
quickstart
api
algorithms
optimization
examples
changelog
```

## Indices

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
