"""
Integration tests for ImageProcessor - Tests the complete processing pipeline.
"""
import pytest
import numpy as np
import os
import tempfile
from app.core.image_processor import ImageProcessor


class TestImageProcessor:
    """Test suite for ImageProcessor integration tests."""

    @pytest.fixture
    def processor(self):
        """Create a fresh ImageProcessor instance."""
        return ImageProcessor()

    @pytest.fixture
    def temp_image_file(self, tmp_path, test_image_rgb):
        """Create a temporary image file."""
        import cv2
        img_path = tmp_path / "test_image.png"
        cv2.imwrite(str(img_path), test_image_rgb)
        return str(img_path)

    # Test initialization
    def test_processor_initialization(self, processor):
        """Test processor initializes with correct default values."""
        assert processor.has_image is False
        assert processor.file_path is None
        assert processor.original is None

    # Test image loading
    def test_load_image_success(self, processor, temp_image_file):
        """Test loading a valid image."""
        result = processor.load_image(temp_image_file)
        
        assert result is True
        assert processor.has_image is True
        assert processor.file_path == temp_image_file
        assert processor.original is not None

    def test_load_image_invalid_path(self, processor):
        """Test loading with invalid file path."""
        result = processor.load_image("nonexistent_file.png")
        
        assert result is False
        assert processor.has_image is False

    # Test image saving
    def test_save_image(self, processor, temp_image_file, tmp_path):
        """Test saving processed image."""
        # Load image first
        processor.load_image(temp_image_file)
        
        # Apply a filter
        processor.set_filter("gaussian_blur", 50)
        
        # Save to new location
        save_path = tmp_path / "output.png"
        result = processor.save_image(str(save_path))
        
        assert result is True
        assert os.path.exists(save_path)

    # Test adjustments
    def test_set_adjustment(self, processor, temp_image_file):
        """Test setting adjustment parameters."""
        processor.load_image(temp_image_file)
        
        processor.set_adjustment("brightness", 50)
        processor.set_adjustment("contrast", 30)
        
        assert processor.get_adjustment("brightness") == 50
        assert processor.get_adjustment("contrast") == 30

    def test_adjustment_bounds(self, processor, temp_image_file):
        """Test that adjustments handle bounds correctly."""
        processor.load_image(temp_image_file)
        
        # Set extreme values
        processor.set_adjustment("brightness", 1000)
        assert processor.get_adjustment("brightness") == 1000
        
        processor.set_adjustment("brightness", -1000)
        assert processor.get_adjustment("brightness") == -1000

    # Test filters
    def test_set_filter(self, processor, temp_image_file):
        """Test setting filter intensity."""
        processor.load_image(temp_image_file)
        
        processor.set_filter("gaussian_blur", 75)
        
        assert processor.get_filter_intensity("gaussian_blur") == 75

    def test_remove_filter(self, processor, temp_image_file):
        """Test removing a filter by setting intensity to 0."""
        processor.load_image(temp_image_file)
        
        processor.set_filter("gaussian_blur", 50)
        processor.set_filter("gaussian_blur", 0)  # Remove filter
        
        assert processor.get_filter_intensity("gaussian_blur") == 0

    def test_multiple_filters(self, processor, temp_image_file):
        """Test setting multiple filters simultaneously."""
        processor.load_image(temp_image_file)
        
        processor.set_filter("gaussian_blur", 50)
        processor.set_filter("sepia", 75)
        processor.set_filter("sharpen", 25)
        
        assert processor.get_filter_intensity("gaussian_blur") == 50
        assert processor.get_filter_intensity("sepia") == 75
        assert processor.get_filter_intensity("sharpen") == 25

    # Test noise
    def test_set_noise_params(self, processor, temp_image_file):
        """Test setting noise parameters."""
        processor.load_image(temp_image_file)
        
        processor.set_noise_params(
            type="gaussian",
            intensity=50,
            monochrome=True,
            scale=1.5
        )
        
        assert processor._noise_params["type"] == "gaussian"
        assert processor._noise_params["intensity"] == 50
        assert processor._noise_params["monochrome"] is True
        assert processor._noise_params["scale"] == 1.5

    # Test processing pipeline
    def test_process_preview(self, processor, temp_image_file):
        """Test preview processing."""
        processor.load_image(temp_image_file)
        
        # Apply some adjustments
        processor.set_adjustment("brightness", 20)
        processor.set_filter("gaussian_blur", 30)
        
        result = processor.process_preview()
        
        assert result is not None
        assert result.shape[2] == 3  # BGR color

    def test_process_full_resolution(self, processor, temp_image_file):
        """Test full resolution processing."""
        processor.load_image(temp_image_file)
        
        processor.set_adjustment("brightness", 20)
        
        result = processor.process_full_resolution()
        
        assert result is not None

    def test_process_no_image(self, processor):
        """Test processing without loading image returns None."""
        result = processor.process_preview()
        assert result is None

    # Test image properties
    def test_image_size(self, processor, temp_image_file):
        """Test image size property."""
        processor.load_image(temp_image_file)
        
        width, height = processor.image_size
        assert width > 0
        assert height > 0

    def test_has_pending_changes(self, processor, temp_image_file):
        """Test detecting pending changes."""
        processor.load_image(temp_image_file)
        
        # Initially no changes
        assert processor.has_pending_changes() is False
        
        # Apply an adjustment
        processor.set_adjustment("brightness", 50)
        assert processor.has_pending_changes() is True

    # Test transform operations
    def test_apply_resize(self, processor, temp_image_file):
        """Test resize transformation."""
        processor.load_image(temp_image_file)
        
        original_width, original_height = processor.image_size
        
        processor.apply_resize(50, 50)
        
        new_width, new_height = processor.image_size
        assert new_width == 50
        assert new_height == 50

    def test_apply_rotation(self, processor, temp_image_file):
        """Test rotation transformation."""
        processor.load_image(temp_image_file)
        
        processor.apply_rotation(90)
        
        assert processor.has_image is True

    def test_apply_flip_horizontal(self, processor, temp_image_file):
        """Test horizontal flip."""
        processor.load_image(temp_image_file)
        
        processor.apply_flip(horizontal=True)
        
        assert processor.has_image is True

    def test_apply_flip_vertical(self, processor, temp_image_file):
        """Test vertical flip."""
        processor.load_image(temp_image_file)
        
        processor.apply_flip(horizontal=False)
        
        assert processor.has_image is True

    # Test apply changes
    def test_apply_current_changes(self, processor, temp_image_file):
        """Test applying current changes to make them permanent."""
        processor.load_image(temp_image_file)
        
        # Apply changes
        processor.set_adjustment("brightness", 30)
        processor.apply_current_changes()
        
        # Check that changes were applied
        assert processor.has_image is True

    # Test reset
    def test_reset_params_after_transform(self, processor, temp_image_file):
        """Test that params are reset after transform."""
        processor.load_image(temp_image_file)
        
        # Set some adjustments
        processor.set_adjustment("brightness", 50)
        processor.set_filter("gaussian_blur", 50)
        
        # Apply transform
        processor.apply_resize(50, 50)
        
        # Check adjustments were reset
        assert processor.get_adjustment("brightness") == 0
        assert processor.get_filter_intensity("gaussian_blur") == 0

    # Test pipeline order (adjustments -> filters -> noise)
    def test_pipeline_order(self, processor, temp_image_file):
        """Test that pipeline applies operations in correct order."""
        processor.load_image(temp_image_file)
        
        # Set all three types of operations
        processor.set_adjustment("brightness", 50)
        processor.set_filter("sepia", 100)
        processor.set_noise_params(type="gaussian", intensity=30)
        
        # Process should succeed
        result = processor.process_preview()
        
        assert result is not None

    # Test edge cases
    def test_process_empty_adjustments(self, processor, temp_image_file):
        """Test processing with all default adjustments."""
        processor.load_image(temp_image_file)
        
        result = processor.process_preview()
        
        # Should return a valid (possibly unchanged) image
        assert result is not None

    def test_very_large_adjustment_values(self, processor, temp_image_file):
        """Test handling very large adjustment values."""
        processor.load_image(temp_image_file)
        
        processor.set_adjustment("brightness", 10000)
        processor.set_adjustment("contrast", 10000)
        
        result = processor.process_preview()
        
        # Should still produce valid output (clamped)
        assert result is not None
        assert result.dtype == np.uint8


class TestImageProcessorHistory:
    """Test suite for undo/redo functionality."""

    @pytest.fixture
    def processor(self):
        return ImageProcessor()

    @pytest.fixture
    def temp_image_file(self, tmp_path, test_image_rgb):
        import cv2
        img_path = tmp_path / "test_image.png"
        cv2.imwrite(str(img_path), test_image_rgb)
        return str(img_path)

    def test_initial_no_undo(self, processor, temp_image_file):
        """Test that undo is not available initially."""
        processor.load_image(temp_image_file)
        
        assert processor.can_undo() is False
        assert processor.can_redo() is False

    def test_undo_after_transform(self, processor, temp_image_file):
        """Test undo becomes available after transform."""
        processor.load_image(temp_image_file)
        
        processor.apply_resize(50, 50)
        
        assert processor.can_undo() is True

    def test_undo(self, processor, temp_image_file):
        """Test undo operation."""
        processor.load_image(temp_image_file)
        
        original_width, original_height = processor.image_size
        
        # Apply resize
        processor.apply_resize(50, 50)
        
        # Undo
        result = processor.undo()
        
        assert result is True

    def test_redo(self, processor, temp_image_file):
        """Test redo operation."""
        processor.load_image(temp_image_file)
        
        # Apply resize
        processor.apply_resize(50, 50)
        
        # Undo first
        processor.undo()
        
        # Now redo should work
        assert processor.can_redo() is True
        
        result = processor.redo()
        assert result is True

    def test_undo_no_history(self, processor, temp_image_file):
        """Test undo with no history returns False."""
        processor.load_image(temp_image_file)
        
        result = processor.undo()
        
        assert result is False

    def test_redo_no_history(self, processor, temp_image_file):
        """Test redo with no history returns False."""
        processor.load_image(temp_image_file)
        
        result = processor.redo()
        
        assert result is False

    def test_multiple_undos(self, processor, temp_image_file):
        """Test multiple undo operations."""
        processor.load_image(temp_image_file)
        
        # Apply multiple transforms
        processor.apply_resize(75, 75)
        processor.apply_rotation(45)
        
        # Undo twice
        processor.undo()
        result = processor.undo()
        
        assert result is True
