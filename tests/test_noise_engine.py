"""
Unit tests for NoiseEngine - Tests all 7 noise types.
"""
import pytest
import numpy as np
from app.core.noise_engine import NoiseEngine


class TestNoiseEngine:
    """Test suite for NoiseEngine noise functions."""

    # Test all noise types with various parameters
    def test_gaussian_noise(self, test_image_rgb):
        """Test Gaussian noise."""
        result = NoiseEngine.gaussian(test_image_rgb, 0.5)
        
        assert result is not None
        assert result.shape == test_image_rgb.shape
        assert result.dtype == test_image_rgb.dtype
    
    def test_gaussian_zero_intensity(self, test_image_rgb):
        """Test that zero intensity returns original image."""
        result = NoiseEngine.gaussian(test_image_rgb, 0.0)
        np.testing.assert_array_equal(result, test_image_rgb)

    def test_salt_pepper(self, test_image_rgb):
        """Test salt & pepper noise."""
        result = NoiseEngine.salt_pepper(test_image_rgb, 0.3)
        assert result.shape == test_image_rgb.shape
    
    def test_salt_pepper_zero_intensity(self, test_image_rgb):
        """Test zero intensity for salt pepper."""
        result = NoiseEngine.salt_pepper(test_image_rgb, 0.0)
        np.testing.assert_array_equal(result, test_image_rgb)

    def test_poisson(self, test_image_rgb):
        """Test Poisson noise."""
        result = NoiseEngine.poisson(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    def test_poisson_zero_intensity(self, test_image_rgb):
        """Test zero intensity for Poisson."""
        result = NoiseEngine.poisson(test_image_rgb, 0.0)
        np.testing.assert_array_equal(result, test_image_rgb)

    def test_speckle(self, test_image_rgb):
        """Test speckle noise."""
        result = NoiseEngine.speckle(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    def test_speckle_zero_intensity(self, test_image_rgb):
        """Test zero intensity for speckle."""
        result = NoiseEngine.speckle(test_image_rgb, 0.0)
        np.testing.assert_array_equal(result, test_image_rgb)

    def test_uniform(self, test_image_rgb):
        """Test uniform noise."""
        result = NoiseEngine.uniform(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    def test_uniform_zero_intensity(self, test_image_rgb):
        """Test zero intensity for uniform."""
        result = NoiseEngine.uniform(test_image_rgb, 0.0)
        np.testing.assert_array_equal(result, test_image_rgb)

    def test_film_grain(self, test_image_rgb):
        """Test film grain noise."""
        result = NoiseEngine.film_grain(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    def test_film_grain_zero_intensity(self, test_image_rgb):
        """Test zero intensity for film grain."""
        result = NoiseEngine.film_grain(test_image_rgb, 0.0)
        np.testing.assert_array_equal(result, test_image_rgb)

    def test_color_noise(self, test_image_rgb):
        """Test color noise."""
        result = NoiseEngine.color_noise(test_image_rgb, 0.5)
        assert result.shape == test_image_rgb.shape

    def test_color_noise_zero_intensity(self, test_image_rgb):
        """Test zero intensity for color noise."""
        result = NoiseEngine.color_noise(test_image_rgb, 0.0)
        np.testing.assert_array_equal(result, test_image_rgb)

    # Test monochrome parameter
    def test_gaussian_monochrome(self, test_image_rgb):
        """Test Gaussian noise with monochrome=True."""
        result = NoiseEngine.gaussian(test_image_rgb, 0.5, monochrome=True)
        assert result.shape == test_image_rgb.shape

    def test_gaussian_color(self, test_image_rgb):
        """Test Gaussian noise with monochrome=False."""
        result = NoiseEngine.gaussian(test_image_rgb, 0.5, monochrome=False)
        assert result.shape == test_image_rgb.shape

    # Test scale parameter
    def test_gaussian_scale_small(self, test_image_rgb):
        """Test Gaussian noise with small scale."""
        result = NoiseEngine.gaussian(test_image_rgb, 0.5, scale=1.0)
        assert result.shape == test_image_rgb.shape

    def test_gaussian_scale_large(self, test_image_rgb):
        """Test Gaussian noise with large scale (large grain)."""
        result = NoiseEngine.gaussian(test_image_rgb, 0.5, scale=5.0)
        assert result.shape == test_image_rgb.shape

    # Test apply_noise factory method
    def test_apply_noise_gaussian(self, test_image_rgb):
        """Test factory method with gaussian noise."""
        result = NoiseEngine.apply_noise(
            test_image_rgb, "gaussian", 0.5, monochrome=True, scale=1.0
        )
        assert result.shape == test_image_rgb.shape

    def test_apply_noise_unknown_type(self, test_image_rgb):
        """Test factory method with unknown noise type."""
        result = NoiseEngine.apply_noise(
            test_image_rgb, "unknown_noise", 0.5
        )
        # Should return original image unchanged
        np.testing.assert_array_equal(result, test_image_rgb)

    def test_apply_noise_all_types(self, test_image_rgb):
        """Test that all noise types can be applied without error."""
        noise_types = [
            "gaussian", "salt_pepper", "poisson",
            "speckle", "uniform", "film_grain", "color_noise"
        ]
        
        for noise_type in noise_types:
            result = NoiseEngine.apply_noise(
                test_image_rgb, noise_type, 0.5, monochrome=True, scale=1.0
            )
            assert result is not None, f"Noise type {noise_type} returned None"
            assert result.shape == test_image_rgb.shape

    # Test intensity bounds
    def test_full_intensity(self, test_image_rgb):
        """Test noise with full intensity (1.0)."""
        result = NoiseEngine.gaussian(test_image_rgb, 1.0)
        assert result.shape == test_image_rgb.shape

    def test_low_intensity(self, test_image_rgb):
        """Test noise with very low intensity (0.01)."""
        result = NoiseEngine.gaussian(test_image_rgb, 0.01)
        assert result.shape == test_image_rgb.shape

    # Test edge cases
    def test_grayscale_image(self, test_image_grayscale):
        """Test noise works with grayscale images."""
        img_bgr = np.dstack([test_image_grayscale] * 3)
        result = NoiseEngine.gaussian(img_bgr, 0.5)
        assert result.shape == img_bgr.shape

    def test_small_image(self, small_test_image):
        """Test noise works with small images."""
        result = NoiseEngine.gaussian(small_test_image, 0.5)
        assert result.shape == small_test_image.shape
