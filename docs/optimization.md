# Optimization Guide

Tips for getting the best performance from RustMatch.

## Use Bytes for Repeated Matching

When matching multiple templates against the same source, load the source once:

```python
import rustmatch

# Load source image bytes once
with open("screenshot.png", "rb") as f:
    source_bytes = f.read()

# Match multiple templates
templates = ["button1.png", "button2.png", "icon.png"]
for tpl_path in templates:
    with open(tpl_path, "rb") as f:
        tpl_bytes = f.read()
    result = rustmatch.find_bytes(source_bytes, tpl_bytes)
    if result:
        print(f"{tpl_path}: found at ({result.x}, {result.y})")
```

## Thread Configuration

### Auto-detect (Default)

```python
rustmatch.set_threads(0)  # Use all CPU cores
```

### Limit Threads

For shared systems or to reduce CPU usage:

```python
rustmatch.set_threads(4)  # Use 4 threads
```

**Note:** `set_threads()` must be called before any matching operation.

## Threshold Tuning

### Start High, Lower if Needed

```python
# Try high threshold first
result = rustmatch.find("screen.png", "button.png", threshold=0.95)

# Lower if no match found
if result is None:
    result = rustmatch.find("screen.png", "button.png", threshold=0.85)
```

### Use Different Thresholds for Different Templates

```python
thresholds = {
    "exact_icon.png": 0.95,
    "variable_button.png": 0.80,
    "noisy_element.png": 0.70,
}

for template, threshold in thresholds.items():
    result = rustmatch.find("screen.png", template, threshold=threshold)
```

## Image Size Considerations

Larger images take longer to process. If pixel-perfect accuracy isn't required, consider:

1. Using smaller template images
2. Cropping the search region if you know the approximate location
3. Using lower resolution screenshots

## Performance Benchmarks

| Image Size | Template | Typical Time |
|------------|----------|--------------|
| 1920×1080 | 64×64 | ~15-25ms |
| 1602×364 | 15×16 | ~10-15ms |
| 3840×2160 | 128×128 | ~50-80ms |

## Memory Usage

RustMatch processes images efficiently:
- Images are converted to grayscale internally
- Integral images use ~16 bytes per pixel
- Memory is released after each match operation
