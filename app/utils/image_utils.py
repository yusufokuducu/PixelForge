"""
Görüntü dönüştürme ve yardımcı fonksiyonlar.
OpenCV (BGR) ↔ QImage/QPixmap dönüşümleri burada yapılır.
"""

import cv2
import numpy as np
from PySide6.QtGui import QImage, QPixmap


def numpy_to_qimage(img: np.ndarray) -> QImage:
    """
    NumPy dizisini (BGR veya BGRA) QImage nesnesine dönüştürür.
    OpenCV BGR formatından Qt RGB formatına çevirir.
    """
    if img is None:
        return QImage()

    # Gri tonlamalı görüntü kontrolü
    if len(img.shape) == 2:
        height, width = img.shape
        bytes_per_line = width
        return QImage(img.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8).copy()

    height, width, channels = img.shape

    if channels == 4:
        # BGRA → RGBA dönüşümü
        rgba = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        bytes_per_line = 4 * width
        return QImage(rgba.data, width, height, bytes_per_line, QImage.Format.Format_RGBA8888).copy()
    else:
        # BGR → RGB dönüşümü
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        bytes_per_line = 3 * width
        return QImage(rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).copy()


def numpy_to_qpixmap(img: np.ndarray) -> QPixmap:
    """NumPy dizisini doğrudan QPixmap'e dönüştürür."""
    return QPixmap.fromImage(numpy_to_qimage(img))


def qimage_to_numpy(qimg: QImage) -> np.ndarray:
    """QImage nesnesini NumPy dizisine (BGR) dönüştürür."""
    qimg = qimg.convertToFormat(QImage.Format.Format_RGB888)
    width = qimg.width()
    height = qimg.height()
    bytes_per_line = qimg.bytesPerLine()

    ptr = qimg.bits()
    arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, bytes_per_line))
    arr = arr[:, :width * 3].reshape((height, width, 3))
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def create_preview(img: np.ndarray, max_width: int = 1920, max_height: int = 1080) -> np.ndarray:
    """
    Performans için büyük görüntülerin önizleme boyutunda kopyasını oluşturur.
    En-boy oranı korunarak küçültme yapılır.
    """
    if img is None:
        return None

    h, w = img.shape[:2]

    # Zaten yeterince küçükse kopyala ve döndür
    if w <= max_width and h <= max_height:
        return img.copy()

    # Ölçek faktörünü hesapla (en-boy oranını koru)
    scale = min(max_width / w, max_height / h)
    new_w = int(w * scale)
    new_h = int(h * scale)

    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


def get_image_info(img: np.ndarray) -> dict:
    """Görüntü hakkında temel bilgileri döndürür."""
    if img is None:
        return {}

    h, w = img.shape[:2]
    channels = img.shape[2] if len(img.shape) == 3 else 1
    dtype = img.dtype

    # Dosya boyutunu tahmin et (sıkıştırılmamış)
    size_bytes = img.nbytes
    if size_bytes > 1024 * 1024:
        size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
    elif size_bytes > 1024:
        size_str = f"{size_bytes / 1024:.1f} KB"
    else:
        size_str = f"{size_bytes} B"

    return {
        "width": w,
        "height": h,
        "channels": channels,
        "dtype": str(dtype),
        "size": size_str,
        "megapixels": f"{(w * h) / 1_000_000:.1f} MP",
    }
