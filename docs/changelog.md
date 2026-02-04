# Changelog

All notable changes to RustMatch will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release preparation

## [0.1.0] - 2024-XX-XX

### Added
- Core template matching with NCC algorithm
- Single target matching with `match_template()`
- Multi-target matching with `match_template_all()`
- `TemplateMatcher` class for reusable matching
- `MatchResult` class with position and confidence
- Image pyramid acceleration for large images
- Integral images for O(1) region statistics
- Parallel processing with Rayon
- Non-Maximum Suppression for multi-target
- Convenience functions: `match_from_files()`, `match_from_pil()`
- Image preprocessing with `preprocess_image()`
- Thread configuration with `set_num_threads()`
- Type hints and py.typed marker
- Comprehensive documentation
- Unit tests and benchmarks

### Performance
- 10-50x faster than OpenCV's matchTemplate
- Automatic pyramid acceleration for templates > 64px
- Multi-threaded row-wise parallel search

### Supported Formats
- PNG, JPEG, BMP, GIF, TIFF, WebP (via Rust image crate)

[0.1.0]: https://github.com/JunjieDuan/rustmatch/releases/tag/v0.1.0
