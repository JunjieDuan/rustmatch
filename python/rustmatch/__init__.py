"""
RustMatch - High-Performance Template Matching Library (Zero Dependencies!)
===========================================================================

A Python library for fast template matching powered by Rust.
NO numpy or pillow required for basic usage!

Features:
- Normalized Cross-Correlation (NCC) algorithm
- Integral images for O(1) region statistics
- Image pyramids for coarse-to-fine search
- Multi-threaded parallel processing
- Zero Python dependencies for core functionality

Quick Start (No numpy needed!):
    >>> import rustmatch
    >>> 
    >>> # Find single match using file paths
    >>> result = rustmatch.find("screenshot.png", "button.png")
    >>> if result:
    ...     print(f"Found at ({result.x}, {result.y})")
    >>>
    >>> # Find all matches
    >>> results = rustmatch.find_all("screenshot.png", "icon.png", threshold=0.8)
    >>> for r in results:
    ...     print(f"Match at ({r.x}, {r.y})")

Classes:
    MatchResult: Match result containing position and confidence

Functions:
    find: Find single best match (file paths)
    find_all: Find all matches (file paths)
    find_bytes: Find single match (image bytes)
    find_all_bytes: Find all matches (image bytes)
"""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "Junjie Duan"
__all__ = [
    # Core classes
    "MatchResult",
    # File path based (recommended!)
    "find",
    "find_all",
    # Bytes based
    "find_bytes",
    "find_all_bytes",
    # Raw pixel data
    "find_raw",
    "find_all_raw",
    # Utilities
    "get_size",
    "get_size_bytes",
    "set_threads",
    "version",
]

# Import from Rust core
from rustmatch._core import (
    MatchResult,
    find_template as _find_template,
    find_all_templates as _find_all_templates,
    find_template_bytes as _find_template_bytes,
    find_all_templates_bytes as _find_all_templates_bytes,
    find_template_raw as _find_template_raw,
    find_all_templates_raw as _find_all_templates_raw,
    get_image_size as _get_image_size,
    get_image_size_bytes as _get_image_size_bytes,
    set_num_threads,
    version as _version,
)

from typing import Optional, List, Union


def find(
    source: str,
    template: str,
    threshold: float = 0.8,
) -> Optional[MatchResult]:
    """
    Find single best match using file paths.
    
    This is the recommended way to use RustMatch - no numpy needed!
    
    Args:
        source: Path to source image file (PNG, JPEG, BMP, etc.)
        template: Path to template image file
        threshold: Matching threshold (0.0-1.0), default 0.8
    
    Returns:
        MatchResult if found, None otherwise
    
    Example:
        >>> result = rustmatch.find("screen.png", "button.png")
        >>> if result:
        ...     print(f"Found at ({result.x}, {result.y}), confidence: {result.confidence:.2%}")
    """
    return _find_template(source, template, threshold)


def find_all(
    source: str,
    template: str,
    threshold: float = 0.8,
    max_count: int = 10,
) -> List[MatchResult]:
    """
    Find all matches using file paths.
    
    Args:
        source: Path to source image file
        template: Path to template image file
        threshold: Matching threshold (0.0-1.0), default 0.8
        max_count: Maximum number of matches to return, default 10
    
    Returns:
        List of MatchResult objects, sorted by confidence (descending)
    
    Example:
        >>> results = rustmatch.find_all("screen.png", "star.png", max_count=5)
        >>> print(f"Found {len(results)} stars")
    """
    return _find_all_templates(source, template, threshold, max_count)


def find_bytes(
    source: bytes,
    template: bytes,
    threshold: float = 0.8,
) -> Optional[MatchResult]:
    """
    Find single best match using image bytes.
    
    Useful when you have image data in memory (e.g., from screenshot capture).
    
    Args:
        source: Source image as bytes (PNG, JPEG, etc. encoded)
        template: Template image as bytes
        threshold: Matching threshold (0.0-1.0), default 0.8
    
    Returns:
        MatchResult if found, None otherwise
    
    Example:
        >>> with open("screen.png", "rb") as f:
        ...     source = f.read()
        >>> with open("button.png", "rb") as f:
        ...     template = f.read()
        >>> result = rustmatch.find_bytes(source, template)
    """
    return _find_template_bytes(source, template, threshold)


def find_all_bytes(
    source: bytes,
    template: bytes,
    threshold: float = 0.8,
    max_count: int = 10,
) -> List[MatchResult]:
    """
    Find all matches using image bytes.
    
    Args:
        source: Source image as bytes
        template: Template image as bytes
        threshold: Matching threshold (0.0-1.0), default 0.8
        max_count: Maximum number of matches, default 10
    
    Returns:
        List of MatchResult objects
    """
    return _find_all_templates_bytes(source, template, threshold, max_count)


def find_raw(
    source_pixels: Union[bytes, List[int]],
    source_width: int,
    source_height: int,
    template_pixels: Union[bytes, List[int]],
    template_width: int,
    template_height: int,
    threshold: float = 0.8,
) -> Optional[MatchResult]:
    """
    Find single match using raw grayscale pixel data.
    
    For advanced users who want to handle image loading themselves.
    
    Args:
        source_pixels: Grayscale pixels as bytes or list (row-major, 0-255)
        source_width: Source image width
        source_height: Source image height
        template_pixels: Template grayscale pixels
        template_width: Template width
        template_height: Template height
        threshold: Matching threshold (0.0-1.0)
    
    Returns:
        MatchResult if found, None otherwise
    """
    src = list(source_pixels) if isinstance(source_pixels, bytes) else source_pixels
    tpl = list(template_pixels) if isinstance(template_pixels, bytes) else template_pixels
    return _find_template_raw(src, source_width, source_height, tpl, template_width, template_height, threshold)


def find_all_raw(
    source_pixels: Union[bytes, List[int]],
    source_width: int,
    source_height: int,
    template_pixels: Union[bytes, List[int]],
    template_width: int,
    template_height: int,
    threshold: float = 0.8,
    max_count: int = 10,
) -> List[MatchResult]:
    """
    Find all matches using raw grayscale pixel data.
    """
    src = list(source_pixels) if isinstance(source_pixels, bytes) else source_pixels
    tpl = list(template_pixels) if isinstance(template_pixels, bytes) else template_pixels
    return _find_all_templates_raw(src, source_width, source_height, tpl, template_width, template_height, threshold, max_count)


def get_size(path: str) -> tuple:
    """
    Get image dimensions from file.
    
    Args:
        path: Path to image file
    
    Returns:
        Tuple of (width, height)
    """
    return _get_image_size(path)


def get_size_bytes(data: bytes) -> tuple:
    """
    Get image dimensions from bytes.
    
    Args:
        data: Image data as bytes
    
    Returns:
        Tuple of (width, height)
    """
    return _get_image_size_bytes(data)


def set_threads(num: int = 0) -> None:
    """
    Set number of threads for parallel processing.
    
    Args:
        num: Number of threads (0 = auto-detect based on CPU cores)
    """
    set_num_threads(num)


def version() -> str:
    """Get library version."""
    return _version()
