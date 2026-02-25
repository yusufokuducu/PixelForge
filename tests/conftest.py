"""
Pytest configuration and shared fixtures for PixelForge tests.
"""
import sys
import os
import numpy as np
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Mock Qt if not available (for CI without display)
try:
    from PySide6.QtGui import QImage, QPixmap
except ImportError:
    # Create mock classes for headless testing
    class QImage:
        def __init__(self, *args, **kwargs):
            pass
    
    class QPixmap:
        def __init__(self, *args, **kwargs):
            pass
    
    # Inject mocks into sys.modules so image_utils can import them
    import types
    mock_qt = types.ModuleType('PySide6')
    mock_qt_gui = types.ModuleType('PySide6.QtGui')
    mock_qt_gui.QImage = QImage
    mock_qt_gui.QPixmap = QPixmap
    sys.modules['PySide6'] = mock_qt
    sys.modules['PySide6.QtGui'] = mock_qt_gui


@pytest.fixture
def test_image_rgb():
    """
    Create a simple RGB test image (100x100).
    Returns a numpy array with shape (100, 100, 3) and dtype uint8.
    """
    # Create a gradient image with different colors
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Red gradient (left to right)
    img[:, :, 2] = np.linspace(0, 255, 100, dtype=np.uint8)
    
    # Green gradient (top to bottom)
    img[:, :, 1] = np.linspace(0, 255, 100, dtype=np.uint8)[:, np.newaxis].reshape(100)
    
    # Blue channel constant
    img[:, :, 0] = 128
    
    return img


@pytest.fixture
def test_image_grayscale():
    """
    Create a simple grayscale test image (100x100).
    Returns a numpy array with shape (100, 100) and dtype uint8.
    """
    # Create gradient from black to white
    img = np.linspace(0, 255, 100, dtype=np.uint8)
    img = np.tile(img, (100, 1))
    return img


@pytest.fixture
def test_image_color():
    """
    Create a colorful RGB test image with distinct regions.
    Useful for testing filters and transformations.
    """
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Top-left: Red
    img[0:50, 0:50] = [0, 0, 255]
    
    # Top-right: Green
    img[0:50, 50:100] = [0, 255, 0]
    
    # Bottom-left: Blue
    img[50:100, 0:50] = [255, 0, 0]
    
    # Bottom-right: White
    img[50:100, 50:100] = [255, 255, 255]
    
    return img


@pytest.fixture
def small_test_image():
    """
    Create a small test image (10x10) for quick tests.
    """
    return np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)


@pytest.fixture
def temp_image_file(tmp_path, test_image_rgb):
    """
    Create a temporary image file and return its path.
    Cleans up automatically after test.
    """
    import cv2
    img_path = tmp_path / "test_image.png"
    cv2.imwrite(str(img_path), test_image_rgb)
    return str(img_path)
