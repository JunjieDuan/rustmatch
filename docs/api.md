# API Reference

Complete API documentation for RustMatch.

## Functions

### find

```python
def find(
    source: str,
    template: str,
    threshold: float = 0.8
) -> Optional[MatchResult]
```

Find the best matching location using file paths.

**Parameters:**
- `source`: Path to source image file (PNG, JPEG, BMP, etc.)
- `template`: Path to template image file
- `threshold`: Minimum confidence threshold (0.0-1.0)

**Returns:**
- `MatchResult` if match found with confidence >= threshold
- `None` if no match found

**Example:**
```python
result = rustmatch.find("screen.png", "button.png", threshold=0.85)
if result:
    print(f"Match at ({result.x}, {result.y})")
```

---

### find_all

```python
def find_all(
    source: str,
    template: str,
    threshold: float = 0.8,
    max_count: int = 10
) -> List[MatchResult]
```

Find all matching locations using file paths.

**Parameters:**
- `source`: Path to source image file
- `template`: Path to template image file
- `threshold`: Minimum confidence (0.0-1.0)
- `max_count`: Maximum number of matches to return

**Returns:**
- List of `MatchResult` objects, sorted by confidence (descending)

---

### find_bytes

```python
def find_bytes(
    source: bytes,
    template: bytes,
    threshold: float = 0.8
) -> Optional[MatchResult]
```

Find the best match using image bytes.

**Parameters:**
- `source`: Source image as bytes (PNG, JPEG, etc. encoded)
- `template`: Template image as bytes
- `threshold`: Minimum confidence (0.0-1.0)

**Returns:**
- `MatchResult` if found, `None` otherwise

---

### find_all_bytes

```python
def find_all_bytes(
    source: bytes,
    template: bytes,
    threshold: float = 0.8,
    max_count: int = 10
) -> List[MatchResult]
```

Find all matches using image bytes.

---

### find_raw

```python
def find_raw(
    source_pixels: Union[bytes, List[int]],
    source_width: int,
    source_height: int,
    template_pixels: Union[bytes, List[int]],
    template_width: int,
    template_height: int,
    threshold: float = 0.8
) -> Optional[MatchResult]
```

Find match using raw grayscale pixel data.

**Parameters:**
- `source_pixels`: Grayscale pixels as bytes or list (row-major, 0-255)
- `source_width`: Source image width
- `source_height`: Source image height
- `template_pixels`: Template grayscale pixels
- `template_width`: Template width
- `template_height`: Template height
- `threshold`: Minimum confidence (0.0-1.0)

---

### get_size

```python
def get_size(path: str) -> Tuple[int, int]
```

Get image dimensions from file.

**Returns:** `(width, height)`

---

### get_size_bytes

```python
def get_size_bytes(data: bytes) -> Tuple[int, int]
```

Get image dimensions from bytes.

---

### set_threads

```python
def set_threads(num: int = 0) -> None
```

Set number of threads for parallel processing.

**Parameters:**
- `num`: Number of threads (0 = auto-detect based on CPU cores)

---

### version

```python
def version() -> str
```

Get library version string.

---

## Classes

### MatchResult

Match result containing position and confidence score.

**Attributes:**
- `x: int` - X coordinate of match (left edge)
- `y: int` - Y coordinate of match (top edge)
- `confidence: float` - Match confidence (0.0-1.0)

**Methods:**

#### to_tuple

```python
def to_tuple(self) -> Tuple[int, int, float]
```

Convert to tuple `(x, y, confidence)`.

#### bbox

```python
def bbox(self, width: int, height: int) -> Tuple[int, int, int, int]
```

Get bounding box as `(x, y, width, height)`.
