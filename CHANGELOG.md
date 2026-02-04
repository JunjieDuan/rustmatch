# Changelog

All notable changes to RustMatch will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-02-04

### Added
- Initial release
- Core template matching with NCC algorithm
- **Zero dependencies** - no numpy or pillow required!
- File path based matching: `find()`, `find_all()`
- Bytes based matching: `find_bytes()`, `find_all_bytes()`
- Raw pixel data matching: `find_raw()`, `find_all_raw()`
- `MatchResult` class with position and confidence
- Image pyramid acceleration for large images
- Integral images for O(1) region statistics
- Parallel processing with Rayon
- Non-Maximum Suppression for multi-target matching
- Utility functions: `get_size()`, `get_size_bytes()`, `set_threads()`
- Type hints and py.typed marker
- Comprehensive documentation
- Unit tests and benchmarks

### Performance
- 10-50x faster than OpenCV's matchTemplate
- Automatic pyramid acceleration for templates > 64px
- Multi-threaded row-wise parallel search
- ~12ms for 1602x364 image with 15x16 template

### Supported Formats
- PNG, JPEG, BMP, GIF, TIFF, WebP (via Rust image crate)

[0.1.0]: https://github.com/JunjieDuan/rustmatch/releases/tag/v0.1.0
