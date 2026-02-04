"""
Benchmark tests for RustMatch.

Run with: pytest tests/test_benchmark.py --benchmark-only
"""

import pytest
import os

try:
    import rustmatch
    RUSTMATCH_AVAILABLE = True
except ImportError:
    RUSTMATCH_AVAILABLE = False


pytestmark = pytest.mark.skipif(
    not RUSTMATCH_AVAILABLE,
    reason="rustmatch not built"
)

# Test image paths
TEST_DIR = os.path.dirname(os.path.dirname(__file__))
IMAGES_DIR = os.path.join(TEST_DIR, "images")
SOURCE_IMAGE = os.path.join(IMAGES_DIR, "A.png")
TEMPLATE_IMAGE = os.path.join(IMAGES_DIR, "a3.png")


class TestBenchmarkFilePath:
    """Benchmarks for file path based matching."""
    
    @pytest.mark.benchmark(group="find-single")
    def test_find_single(self, benchmark):
        """Benchmark single match."""
        result = benchmark(rustmatch.find, SOURCE_IMAGE, TEMPLATE_IMAGE, 0.8)
        assert result is not None
    
    @pytest.mark.benchmark(group="find-all")
    def test_find_all(self, benchmark):
        """Benchmark multi-match."""
        results = benchmark(rustmatch.find_all, SOURCE_IMAGE, TEMPLATE_IMAGE, 0.8, 10)
        assert len(results) > 0


class TestBenchmarkBytes:
    """Benchmarks for bytes based matching."""
    
    @pytest.fixture
    def image_bytes(self):
        """Load image bytes once."""
        with open(SOURCE_IMAGE, "rb") as f:
            source = f.read()
        with open(TEMPLATE_IMAGE, "rb") as f:
            template = f.read()
        return source, template
    
    @pytest.mark.benchmark(group="find-bytes")
    def test_find_bytes(self, benchmark, image_bytes):
        """Benchmark bytes matching (excludes file I/O)."""
        source, template = image_bytes
        result = benchmark(rustmatch.find_bytes, source, template, 0.8)
        assert result is not None
    
    @pytest.mark.benchmark(group="find-all-bytes")
    def test_find_all_bytes(self, benchmark, image_bytes):
        """Benchmark bytes multi-match."""
        source, template = image_bytes
        results = benchmark(rustmatch.find_all_bytes, source, template, 0.8, 10)
        assert len(results) > 0
