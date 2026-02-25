"""
Unit tests for TransformEngine - Tests resize, rotate, flip, crop operations.
"""
import pytest
import numpy as np
from app.core.transform_engine import TransformEngine


class TestTransformEngine:
    """Test suite for TransformEngine transformation functions."""

    # Test resize operations
    def test_resize_basic(self, test_image_rgb):
        """Test basic resize operation."""
        result = TransformEngine.resize(test_image_rgb, 50, 50)
        
        assert result is not None
        assert result.shape == (50, 50, 3)
        assert result.dtype == test_image_rgb.dtype

    def test_resize_larger(self, test_image_rgb):
        """Test resizing to larger dimensions."""
        result = TransformEngine.resize(test_image_rgb, 200, 200)
        assert result.shape == (200, 200, 3)

    def test_resize_different_aspect_ratio(self, test_image_rgb):
        """Test resizing with different aspect ratio."""
        result = TransformEngine.resize(test_image_rgb, 200, 100)
        assert result.shape == (100, 200, 3)

    def test_resize_zero_width(self, test_image_rgb):
        """Test resize with zero width returns original."""
        result = TransformEngine.resize(test_image_rgb, 0, 100)
        # Should return original image when width is 0
        np.testing.assert_array_equal(result, test_image_rgb)

    def test_resize_negative_dimensions(self, test_image_rgb):
        """Test resize with negative dimensions."""
        result = TransformEngine.resize(test_image_rgb, -10, 100)
        # Should return original
        assert result is None or np.array_equal(result, test_image_rgb)

    def test_resize_interpolation_methods(self, test_image_rgb):
        """Test all interpolation methods."""
        methods = ["nearest", "bilinear", "bicubic", "lanczos", "area"]
        
        for method in methods:
            result = TransformEngine.resize(test_image_rgb, 50, 50, method=method)
            assert result is not None, f"Method {method} failed"
            assert result.shape == (50, 50, 3)

    def test_resize_by_percentage(self, test_image_rgb):
        """Test resize by percentage."""
        result = TransformEngine.resize_by_percentage(test_image_rgb, 50)
        
        expected_h = int(100 * 0.5)
        expected_w = int(100 * 0.5)
        assert result.shape == (expected_h, expected_w, 3)

    def test_resize_by_percentage_invalid(self, test_image_rgb):
        """Test resize by percentage with invalid value."""
        result = TransformEngine.resize_by_percentage(test_image_rgb, 0)
        # Should return original
        assert result is None or np.array_equal(result, test_image_rgb)

    def test_resize_to_fit(self, test_image_rgb):
        """Test resize to fit within max dimensions."""
        result = TransformEngine.resize_to_fit(test_image_rgb, 200, 200)
        assert result.shape[0] <= 200
        assert result.shape[1] <= 200

    def test_resize_to_fit_already_small(self, test_image_rgb):
        """Test resize to fit when image is already smaller."""
        result = TransformEngine.resize_to_fit(test_image_rgb, 200, 200)
        # Image is 100x100, should remain unchanged
        assert result.shape == (100, 100, 3)

    # Test rotation operations
    def test_rotate_90_clockwise(self, test_image_rgb):
        """Test 90 degree clockwise rotation."""
        result = TransformEngine.rotate(test_image_rgb, 90)
        
        assert result is not None
        assert result.dtype == test_image_rgb.dtype

    def test_rotate_90_counter_clockwise(self, test_image_rgb):
        """Test 90 degree counter-clockwise rotation."""
        result = TransformEngine.rotate(test_image_rgb, -90)
        assert result is not None

    def test_rotate_180(self, test_image_rgb):
        """Test 180 degree rotation."""
        result = TransformEngine.rotate(test_image_rgb, 180)
        assert result is not None

    def test_rotate_45_degrees(self, test_image_rgb):
        """Test arbitrary angle rotation."""
        result = TransformEngine.rotate(test_image_rgb, 45)
        assert result is not None

    def test_rotate_no_expand(self, test_image_rgb):
        """Test rotation without canvas expansion."""
        result = TransformEngine.rotate(test_image_rgb, 45, expand=False)
        assert result is not None

    def test_rotate_with_expand(self, test_image_rgb):
        """Test rotation with canvas expansion."""
        result = TransformEngine.rotate(test_image_rgb, 45, expand=True)
        assert result is not None

    def test_rotate_zero_angle(self, test_image_rgb):
        """Test rotation with zero angle."""
        result = TransformEngine.rotate(test_image_rgb, 0)
        # Should return a copy of the image
        assert result is not None

    # Test flip operations
    def test_flip_horizontal(self, test_image_color):
        """Test horizontal flip."""
        result = TransformEngine.flip_horizontal(test_image_color)
        
        # Check that result has same shape
        assert result.shape == test_image_color.shape

    def test_flip_vertical(self, test_image_color):
        """Test vertical flip."""
        result = TransformEngine.flip_vertical(test_image_color)
        
        # Check that result has same shape
        assert result.shape == test_image_color.shape

    def test_flip_returns_copy(self, test_image_rgb):
        """Test that flip returns a new array, not a view."""
        result = TransformEngine.flip_horizontal(test_image_rgb)
        # Modify result
        result[0, 0] = [0, 0, 0]
        # Original should not be affected
        assert not np.array_equal(result[0, 0], test_image_rgb[0, 0])

    # Test crop operations
    def test_crop_basic(self, test_image_rgb):
        """Test basic crop operation."""
        result = TransformEngine.crop(test_image_rgb, 10, 10, 50, 50)
        
        assert result is not None
        assert result.shape == (50, 50, 3)

    def test_crop_partial(self, test_image_rgb):
        """Test crop with coordinates outside bounds."""
        result = TransformEngine.crop(test_image_rgb, -10, -10, 50, 50)
        
        # Should handle gracefully and crop what's available
        assert result is not None

    def test_crop_larger_than_image(self, test_image_rgb):
        """Test crop region larger than image."""
        result = TransformEngine.crop(test_image_rgb, 0, 0, 500, 500)
        
        # Should handle gracefully
        assert result is not None

    def test_crop_invalid_region(self, test_image_rgb):
        """Test crop with invalid region."""
        result = TransformEngine.crop(test_image_rgb, 50, 50, -10, -10)
        
        # Should return original or handle gracefully
        assert result is not None

    def test_auto_crop(self, test_image_rgb):
        """Test auto crop removes borders."""
        # Create image with border
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[10:90, 10:90] = 255  # White square in center
        
        result = TransformEngine.auto_crop(img)
        
        # Result should be smaller (border removed)
        assert result.shape[0] < 100
        assert result.shape[1] < 100

    def test_auto_crop_uniform(self, test_image_rgb):
        """Test auto crop with uniform image."""
        # Image with no border (uniform color)
        img = np.full((100, 100, 3), 128, dtype=np.uint8)
        
        result = TransformEngine.auto_crop(img)
        
        # Should return the original image (nothing to crop)
        assert result is not None

    # Test edge cases
    def test_none_image(self):
        """Test operations with None input."""
        result = TransformEngine.resize(None, 50, 50)
        assert result is None
        
        result = TransformEngine.rotate(None, 45)
        assert result is None
        
        result = TransformEngine.flip_horizontal(None)
        assert result is None

    def test_single_pixel_image(self):
        """Test operations on 1x1 pixel image."""
        img = np.array([[[255, 0, 0]]], dtype=np.uint8)
        
        result = TransformEngine.resize(img, 10, 10)
        assert result.shape == (10, 10, 3)
