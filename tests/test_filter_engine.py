"""
Unit tests for FilterEngine - Tests all 18 image filters.
"""
import pytest
import numpy as np
from app.core.filter_engine import FilterEngine


class TestFilterEngine:
    """Test suite for FilterEngine filter functions."""

    # Test blur filters
    def test_gaussian_blur(self, test_image_rgb):
        """Test Gaussian blur filter with intensity 0.5."""
        result = FilterEngine.gaussian_blur(test_image_rgb, 0.5)
        
        assert result is not None
        assert result.shape == test_image_rgb.shape
        assert result.dtype == test_image_rgb.dtype
    
    def test_gaussian_blur_zero_intensity(self, test_image_rgb):
        """Test that zero intensity returns original image."""
        result = FilterEngine.gaussian_blur(test_image_rgb, 0.0)
        np.testing.assert_array_equal(result, test_image_rgb)

    def test_box_blur(self, test_image_rgb):
        """Test box blur filter."""
        result = FilterEngine.box_blur(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    def test_median_blur(self, test_image_rgb):
        """Test median blur filter."""
        result = FilterEngine.median_blur(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    # Test sharpen filters
    def test_sharpen(self, test_image_rgb):
        """Test sharpen filter."""
        result = FilterEngine.sharpen(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    def test_unsharp_mask(self, test_image_rgb):
        """Test unsharp mask filter."""
        result = FilterEngine.unsharp_mask(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    # Test artistic filters
    def test_edge_detect(self, test_image_rgb):
        """Test edge detection filter."""
        result = FilterEngine.edge_detect(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    def test_emboss(self, test_image_rgb):
        """Test emboss filter."""
        result = FilterEngine.emboss(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    # Test color/style filters
    def test_sepia(self, test_image_rgb):
        """Test sepia filter."""
        result = FilterEngine.sepia(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    def test_vintage(self, test_image_rgb):
        """Test vintage filter."""
        result = FilterEngine.vintage(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    def test_vignette(self, test_image_rgb):
        """Test vignette filter."""
        result = FilterEngine.vignette(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    def test_hdr_effect(self, test_image_rgb):
        """Test HDR effect filter."""
        result = FilterEngine.hdr_effect(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    def test_pencil_sketch(self, test_image_rgb):
        """Test pencil sketch filter."""
        result = FilterEngine.pencil_sketch(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    def test_oil_painting(self, test_image_rgb):
        """Test oil painting filter."""
        result = FilterEngine.oil_painting(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    def test_pixelate(self, test_image_rgb):
        """Test pixelate filter."""
        result = FilterEngine.pixelate(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    def test_posterize(self, test_image_rgb):
        """Test posterize filter."""
        result = FilterEngine.posterize(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    def test_warm_filter(self, test_image_rgb):
        """Test warm filter."""
        result = FilterEngine.warm_filter(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    def test_cool_filter(self, test_image_rgb):
        """Test cool filter."""
        result = FilterEngine.cool_filter(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    def test_dramatic(self, test_image_rgb):
        """Test dramatic filter."""
        result = FilterEngine.dramatic(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    # Test apply_filter factory method
    def test_apply_filter_gaussian_blur(self, test_image_rgb):
        """Test factory method with gaussian_blur."""
        result = FilterEngine.apply_filter(test_image_rgb, "gaussian_blur", 0.5)
        assert result.shape == test_image_rgb.shape

    def test_apply_filter_unknown_filter(self, test_image_rgb):
        """Test factory method with unknown filter name."""
        result = FilterEngine.apply_filter(test_image_rgb, "unknown_filter", 0.5)
        # Should return original image unchanged
        np.testing.assert_array_equal(result, test_image_rgb)

    def test_apply_filter_all_filters(self, test_image_rgb):
        """Test that all defined filters can be applied without error."""
        filter_names = [
            "gaussian_blur", "box_blur", "median_blur",
            "sharpen", "unsharp_mask", "edge_detect", "emboss",
            "sepia", "vintage", "vignette", "hdr_effect",
            "pencil_sketch", "oil_painting", "pixelate",
            "posterize", "warm_filter", "cool_filter", "dramatic"
        ]
        
        for filter_name in filter_names:
            result = FilterEngine.apply_filter(test_image_rgb, filter_name, 0.5)
            assert result is not None, f"Filter {filter_name} returned None"
            assert result.shape == test_image_rgb.shape

    # Test blend function
    def test_blend_zero_intensity(self, test_image_rgb):
        """Test blend with zero intensity returns original."""
        result = FilterEngine._blend(test_image_rgb, test_image_rgb, 0.0)
        np.testing.assert_array_equal(result, test_image_rgb)

    def test_blend_full_intensity(self, test_image_rgb):
        """Test blend with full intensity returns filtered."""
        # Create a completely different image to filter
        filtered = np.zeros_like(test_image_rgb)
        result = FilterEngine._blend(test_image_rgb, filtered, 1.0)
        np.testing.assert_array_equal(result, filtered)

    # Test edge cases
    def test_grayscale_image(self, test_image_grayscale):
        """Test filters work with grayscale images."""
        # Convert grayscale to BGR for filter functions
        img_bgr = np.dstack([test_image_grayscale] * 3)
        result = FilterEngine.gaussian_blur(img_bgr, 0.5)
        assert result.shape == img_bgr.shape

    def test_small_image(self, small_test_image):
        """Test filters work with small images."""
        result = FilterEngine.gaussian_blur(small_test_image, 0.5)
        assert result.shape == small_test_image.shape
