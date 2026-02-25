"""
Unit tests for utility modules - constants and image utilities.
"""
import pytest
import numpy as np
from app.utils import constants


class TestConstants:
    """Test suite for constants module."""

    def test_app_info(self):
        """Test application info constants."""
        assert constants.APP_NAME == "PixelForge"
        assert constants.APP_VERSION == "1.0.0"
        assert constants.APP_AUTHOR == "PixelForge Studio"

    def test_preview_settings(self):
        """Test preview dimension constants."""
        assert constants.PREVIEW_MAX_WIDTH == 1920
        assert constants.PREVIEW_MAX_HEIGHT == 1080

    def test_debounce_time(self):
        """Test slider debounce time."""
        assert constants.SLIDER_DEBOUNCE_MS == 60

    def test_max_history_states(self):
        """Test max undo/redo history states."""
        assert constants.MAX_HISTORY_STATES == 30

    def test_supported_image_formats(self):
        """Test supported image formats."""
        formats = constants.SUPPORTED_IMAGE_FORMATS
        assert "*.png" in formats
        assert "*.jpg" in formats
        assert "*.jpeg" in formats
        assert "*.bmp" in formats
        assert "*.tiff" in formats
        assert "*.webp" in formats

    def test_save_image_formats(self):
        """Test save image formats."""
        formats = constants.SAVE_IMAGE_FORMATS
        assert "PNG (*.png)" in formats
        assert "JPEG (*.jpg)" in formats

    def test_adjustment_ranges(self):
        """Test adjustment parameter ranges."""
        ranges = constants.ADJUSTMENT_RANGES
        
        # Check brightness
        assert "brightness" in ranges
        assert ranges["brightness"] == (-100, 100, 0, 1)
        
        # Check contrast
        assert "contrast" in ranges
        assert ranges["contrast"] == (-100, 100, 0, 1)
        
        # Check gamma (special case)
        assert ranges["gamma"] == (10, 300, 100, 1)
        
        # Check sharpness (0 to 100, not -100 to 100)
        assert ranges["sharpness"] == (0, 100, 0, 1)

    def test_adjustment_labels(self):
        """Test adjustment Turkish labels."""
        labels = constants.ADJUSTMENT_LABELS
        
        assert labels["brightness"] == "Parlaklık"
        assert labels["contrast"] == "Kontrast"
        assert labels["saturation"] == "Doygunluk"
        assert labels["gamma"] == "Gama"
        
        # All adjustments should have labels
        for key in constants.ADJUSTMENT_RANGES:
            assert key in labels, f"Missing label for {key}"

    def test_filter_definitions(self):
        """Test filter definitions."""
        filters = constants.FILTER_DEFINITIONS
        
        # Should have 18 filters
        assert len(filters) == 18
        
        # Check specific filters
        filter_names = [f[0] for f in filters]
        assert "gaussian_blur" in filter_names
        assert "sepia" in filter_names
        assert "vintage" in filter_names
        assert "sharpen" in filter_names

    def test_noise_types(self):
        """Test noise type definitions."""
        noise_types = constants.NOISE_TYPES
        
        # Should have 7 noise types
        assert len(noise_types) == 7
        
        # Check specific noise types
        noise_names = [n[0] for n in noise_types]
        assert "gaussian" in noise_names
        assert "salt_pepper" in noise_names
        assert "film_grain" in noise_names

    def test_interpolation_methods(self):
        """Test interpolation method definitions."""
        methods = constants.INTERPOLATION_METHODS
        
        # Should have 5 methods
        assert len(methods) == 5
        
        # Check specific methods
        method_names = [m[0] for m in methods]
        assert "nearest" in method_names
        assert "bilinear" in method_names
        assert "lanczos" in method_names
        assert "bicubic" in method_names

    def test_color_constants(self):
        """Test color constants."""
        assert constants.CANVAS_BACKGROUND == "#1a1a2e"
        assert constants.PANEL_BACKGROUND == "#16213e"
        assert constants.ACCENT_COLOR == "#0f3460"
        assert constants.HIGHLIGHT_COLOR == "#e94560"
        assert constants.TEXT_COLOR == "#eaeaea"
        assert constants.BORDER_COLOR == "#2a2a4a"

    def test_adjustment_ranges_consistency(self):
        """Test that all adjustment ranges have valid min/max/default/step."""
        for name, (min_val, max_val, default, step) in constants.ADJUSTMENT_RANGES.items():
            # Min should be less than max
            assert min_val < max_val, f"{name}: min >= max"
            
            # Default should be within range
            assert min_val <= default <= max_val, f"{name}: default out of range"
            
            # Step should be positive
            assert step > 0, f"{name}: step <= 0"


class TestImageUtils:
    """Test suite for image utility functions (non-Qt dependent)."""
    
    def test_create_preview_small_image(self):
        """Test that small images are returned as copy."""
        from app.utils.image_utils import create_preview
        
        # Create a small image
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = create_preview(img, 1920, 1080)
        
        # Should return a copy
        assert result is not None
        assert result.shape == img.shape
        # Should be equal but not the same object
        assert np.array_equal(result, img)

    def test_create_preview_large_image(self):
        """Test that large images are resized."""
        from app.utils.image_utils import create_preview
        
        # Create a large image
        img = np.zeros((2000, 3000, 3), dtype=np.uint8)
        
        result = create_preview(img, 1920, 1080)
        
        # Should be resized to fit within max dimensions
        assert result.shape[0] <= 1080
        assert result.shape[1] <= 1920

    def test_create_preview_none(self):
        """Test create_preview with None input."""
        from app.utils.image_utils import create_preview
        
        result = create_preview(None, 1920, 1080)
        
        assert result is None

    def test_get_image_info_rgb(self):
        """Test get_image_info for RGB image."""
        from app.utils.image_utils import get_image_info
        
        # Create a 1920x1080 RGB image
        img = np.zeros((1080, 1920, 3), dtype=np.uint8)
        
        info = get_image_info(img)
        
        assert info["width"] == 1920
        assert info["height"] == 1080
        assert info["channels"] == 3
        assert "MP" in info["megapixels"]

    def test_get_image_info_grayscale(self):
        """Test get_image_info for grayscale image."""
        from app.utils.image_utils import get_image_info
        
        # Create a grayscale image
        img = np.zeros((100, 200), dtype=np.uint8)
        
        info = get_image_info(img)
        
        assert info["width"] == 200
        assert info["height"] == 100
        assert info["channels"] == 1

    def test_get_image_info_none(self):
        """Test get_image_info with None input."""
        from app.utils.image_utils import get_image_info
        
        result = get_image_info(None)
        
        assert result == {}

    def test_get_image_info_size_calculation(self):
        """Test that size calculation is correct."""
        from app.utils.image_utils import get_image_info
        
        # 100x100 RGB = 30,000 bytes
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        
        info = get_image_info(img)
        
        # Should be around 29-30 KB
        assert "KB" in info["size"]
