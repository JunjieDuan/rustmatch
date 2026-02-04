# Quick Start Guide

Get up and running with RustMatch in minutes - no numpy required!

## Basic Usage

### Single Target Matching

```python
import rustmatch

# Find the best match using file paths (recommended!)
result = rustmatch.find("screenshot.png", "button.png", threshold=0.8)

if result:
    print(f"Found at position: ({result.x}, {result.y})")
    print(f"Confidence: {result.confidence:.2%}")
else:
    print("No match found")
```

### Multi-Target Matching

```python
# Find all occurrences
results = rustmatch.find_all(
    "screenshot.png", 
    "icon.png", 
    threshold=0.8,
    max_count=10
)

print(f"Found {len(results)} matches:")
for i, r in enumerate(results):
    print(f"  {i+1}. ({r.x}, {r.y}) - confidence: {r.confidence:.2%}")
```

## Using Image Bytes

For screenshots captured in memory:

```python
# Read files as bytes
with open("screenshot.png", "rb") as f:
    source = f.read()
with open("button.png", "rb") as f:
    template = f.read()

# Match using bytes
result = rustmatch.find_bytes(source, template, threshold=0.8)
```

## Working with Results

### MatchResult Properties

```python
result = rustmatch.find("screen.png", "button.png")

if result:
    # Position (top-left corner)
    x, y = result.x, result.y
    
    # Confidence score (0.0 to 1.0)
    confidence = result.confidence
    
    # Get as tuple
    x, y, conf = result.to_tuple()
    
    # Get bounding box
    template_size = rustmatch.get_size("button.png")
    bbox = result.bbox(template_size[0], template_size[1])
```

## Choosing Threshold

| Threshold | Use Case |
|-----------|----------|
| 0.95+ | Exact match, identical images |
| 0.85-0.95 | High confidence, minor variations |
| 0.75-0.85 | Moderate confidence, some noise |
| < 0.75 | May produce false positives |

## Performance Tips

### 1. Use Bytes for Repeated Matching

```python
# Load once
with open("screenshot.png", "rb") as f:
    source = f.read()

# Match multiple templates
for template_path in ["icon1.png", "icon2.png", "icon3.png"]:
    with open(template_path, "rb") as f:
        template = f.read()
    result = rustmatch.find_bytes(source, template)
```

### 2. Configure Thread Count

```python
# Use all CPU cores (default)
rustmatch.set_threads(0)

# Limit to 4 threads
rustmatch.set_threads(4)
```
