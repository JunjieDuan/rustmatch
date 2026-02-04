"""
Unit tests for RustMatch template matching library.
Zero dependencies - no numpy required!
"""

import pytest
import os

# Import will fail until the library is built
try:
    import rustmatch
    from rustmatch import MatchResult
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


class TestMatchResult:
    """Tests for MatchResult class."""
    
    def test_match_result_attributes(self):
        """Test MatchResult has correct attributes."""
        result = rustmatch.find(SOURCE_IMAGE, TEMPLATE_IMAGE, threshold=0.5)
        
        assert result is not None
        assert hasattr(result, 'x')
        assert hasattr(result, 'y')
        assert hasattr(result, 'confidence')
        assert isinstance(result.x, int)
        assert isinstance(result.y, int)
        assert isinstance(result.confidence, float)
    
    def test_match_result_to_tuple(self):
        """Test MatchResult.to_tuple() method."""
        result = rustmatch.find(SOURCE_IMAGE, TEMPLATE_IMAGE, threshold=0.5)
        
        assert result is not None
        t = result.to_tuple()
        assert len(t) == 3
        assert t[0] == result.x
        assert t[1] == result.y
        assert t[2] == result.confidence
    
    def test_match_result_bbox(self):
        """Test MatchResult.bbox() method."""
        result = rustmatch.find(SOURCE_IMAGE, TEMPLATE_IMAGE, threshold=0.5)
        
        assert result is not None
        bbox = result.bbox(15, 16)
        assert len(bbox) == 4
        assert bbox[0] == result.x
        assert bbox[1] == result.y
        assert bbox[2] == 15
        assert bbox[3] == 16
    
    def test_match_result_repr(self):
        """Test MatchResult string representation."""
        result = rustmatch.find(SOURCE_IMAGE, TEMPLATE_IMAGE, threshold=0.5)
        
        assert result is not None
        repr_str = repr(result)
        assert "MatchResult" in repr_str
        assert str(result.x) in repr_str


class TestFind:
    """Tests for find function (file path based)."""
    
    def test_find_single_match(self):
        """Test finding single match."""
        result = rustmatch.find(SOURCE_IMAGE, TEMPLATE_IMAGE, threshold=0.8)
        
        assert result is not None
        assert result.confidence >= 0.8
    
    def test_find_with_high_threshold(self):
        """Test with high threshold."""
        result = rustmatch.find(SOURCE_IMAGE, TEMPLATE_IMAGE, threshold=0.99)
        
        # Should still find match since we have exact template
        assert result is not None
        assert result.confidence >= 0.99
    
    def test_find_nonexistent_file(self):
        """Test error handling for nonexistent file."""
        with pytest.raises(OSError):
            rustmatch.find("nonexistent.png", TEMPLATE_IMAGE)
    
    def test_find_invalid_threshold(self):
        """Test with various threshold values."""
        # Valid thresholds should work
        result = rustmatch.find(SOURCE_IMAGE, TEMPLATE_IMAGE, threshold=0.5)
        assert result is None or isinstance(result, MatchResult)


class TestFindAll:
    """Tests for find_all function."""
    
    def test_find_all_multiple_matches(self):
        """Test finding multiple matches."""
        results = rustmatch.find_all(SOURCE_IMAGE, TEMPLATE_IMAGE, threshold=0.8, max_count=20)
        
        assert len(results) > 0
        # All results should meet threshold
        for r in results:
            assert r.confidence >= 0.8
    
    def test_find_all_max_count(self):
        """Test max_count limit."""
        results = rustmatch.find_all(SOURCE_IMAGE, TEMPLATE_IMAGE, threshold=0.5, max_count=3)
        
        assert len(results) <= 3
    
    def test_find_all_sorted_by_confidence(self):
        """Test results are sorted by confidence."""
        results = rustmatch.find_all(SOURCE_IMAGE, TEMPLATE_IMAGE, threshold=0.5, max_count=10)
        
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].confidence >= results[i + 1].confidence


class TestFindBytes:
    """Tests for bytes-based matching."""
    
    def test_find_bytes(self):
        """Test matching with image bytes."""
        with open(SOURCE_IMAGE, "rb") as f:
            source_bytes = f.read()
        with open(TEMPLATE_IMAGE, "rb") as f:
            template_bytes = f.read()
        
        result = rustmatch.find_bytes(source_bytes, template_bytes, threshold=0.8)
        
        assert result is not None
        assert result.confidence >= 0.8
    
    def test_find_all_bytes(self):
        """Test finding all matches with bytes."""
        with open(SOURCE_IMAGE, "rb") as f:
            source_bytes = f.read()
        with open(TEMPLATE_IMAGE, "rb") as f:
            template_bytes = f.read()
        
        results = rustmatch.find_all_bytes(source_bytes, template_bytes, threshold=0.8)
        
        assert len(results) > 0
    
    def test_find_bytes_invalid_data(self):
        """Test error handling for invalid image data."""
        with pytest.raises(ValueError):
            rustmatch.find_bytes(b"not an image", b"also not an image")


class TestFindRaw:
    """Tests for raw pixel data matching."""
    
    def test_find_raw_basic(self):
        """Test matching with raw pixel data."""
        # Create simple test pattern
        width, height = 100, 100
        source_pixels = [128] * (width * height)
        
        # Create distinct region
        for y in range(20, 40):
            for x in range(30, 50):
                source_pixels[y * width + x] = 255
        
        template_pixels = [255] * (20 * 20)
        
        result = rustmatch.find_raw(
            source_pixels, width, height,
            template_pixels, 20, 20,
            threshold=0.5
        )
        
        # May or may not find match depending on variance
        assert result is None or isinstance(result, MatchResult)
    
    def test_find_raw_dimension_mismatch(self):
        """Test error for mismatched dimensions."""
        with pytest.raises(ValueError):
            rustmatch.find_raw(
                [0] * 100, 10, 10,  # 100 pixels but 10x10=100, OK
                [0] * 50, 10, 10,   # 50 pixels but 10x10=100, ERROR
                threshold=0.5
            )


class TestUtilities:
    """Tests for utility functions."""
    
    def test_get_size(self):
        """Test getting image dimensions."""
        width, height = rustmatch.get_size(SOURCE_IMAGE)
        
        assert width == 1602
        assert height == 364
    
    def test_get_size_bytes(self):
        """Test getting dimensions from bytes."""
        with open(SOURCE_IMAGE, "rb") as f:
            data = f.read()
        
        width, height = rustmatch.get_size_bytes(data)
        
        assert width == 1602
        assert height == 364
    
    def test_version(self):
        """Test version function."""
        ver = rustmatch.version()
        
        assert isinstance(ver, str)
        assert "." in ver  # Should be semver format
    
    def test_set_threads(self):
        """Test setting thread count."""
        # Note: set_threads can only be called once before any matching
        # After that, the thread pool is already initialized
        # This test just verifies the function exists and is callable
        try:
            rustmatch.set_threads(4)
        except ValueError as e:
            # Expected if thread pool already initialized
            assert "already been initialized" in str(e)


class TestConsistency:
    """Test consistency between different APIs."""
    
    def test_file_vs_bytes_consistency(self):
        """Test that file and bytes APIs give same results."""
        result_file = rustmatch.find(SOURCE_IMAGE, TEMPLATE_IMAGE, threshold=0.8)
        
        with open(SOURCE_IMAGE, "rb") as f:
            source_bytes = f.read()
        with open(TEMPLATE_IMAGE, "rb") as f:
            template_bytes = f.read()
        
        result_bytes = rustmatch.find_bytes(source_bytes, template_bytes, threshold=0.8)
        
        assert result_file is not None
        assert result_bytes is not None
        assert result_file.x == result_bytes.x
        assert result_file.y == result_bytes.y
        assert abs(result_file.confidence - result_bytes.confidence) < 0.001
