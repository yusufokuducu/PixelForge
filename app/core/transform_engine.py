"""
Dönüşüm Motoru - Görüntü boyutlandırma, döndürme, çevirme ve kırpma işlemleri.
Farklı interpolasyon yöntemleri desteklenir.
"""

import cv2
import numpy as np


class TransformEngine:
    """
    Görüntü geometrik dönüşüm işlemleri.
    Tüm metotlar statik olup, saf fonksiyonel yapıdadır.
    """

    # İnterpolasyon yöntemi eşleştirmesi
    INTERPOLATION_MAP = {
        "nearest":  cv2.INTER_NEAREST,
        "bilinear": cv2.INTER_LINEAR,
        "bicubic":  cv2.INTER_CUBIC,
        "lanczos":  cv2.INTER_LANCZOS4,
        "area":     cv2.INTER_AREA,
    }

    @classmethod
    def resize(cls, image: np.ndarray, width: int, height: int,
               method: str = "lanczos") -> np.ndarray:
        """
        Görüntüyü belirtilen boyutlara yeniden ölçeklendirir.
        Seçilen interpolasyon yöntemi ile kalite kontrolü sağlanır.

        Parametreler:
            width: Hedef genişlik (piksel)
            height: Hedef yükseklik (piksel)
            method: İnterpolasyon yöntemi (nearest, bilinear, bicubic, lanczos, area)
        """
        if image is None or width <= 0 or height <= 0:
            return image

        interp = cls.INTERPOLATION_MAP.get(method, cv2.INTER_LANCZOS4)
        return cv2.resize(image, (width, height), interpolation=interp)

    @staticmethod
    def resize_by_percentage(image: np.ndarray, percentage: float,
                             method: str = "lanczos") -> np.ndarray:
        """
        Görüntüyü yüzde oranına göre ölçeklendirir.
        En-boy oranı otomatik korunur.
        """
        if image is None or percentage <= 0:
            return image

        h, w = image.shape[:2]
        new_w = max(1, int(w * percentage / 100))
        new_h = max(1, int(h * percentage / 100))
        return TransformEngine.resize(image, new_w, new_h, method)

    @staticmethod
    def resize_to_fit(image: np.ndarray, max_width: int, max_height: int,
                      method: str = "lanczos") -> np.ndarray:
        """
        Görüntüyü maksimum boyutlara sığdırır, en-boy oranını korur.
        Görüntü zaten yeterince küçükse değişiklik yapmaz.
        """
        if image is None:
            return image

        h, w = image.shape[:2]
        if w <= max_width and h <= max_height:
            return image.copy()

        scale = min(max_width / w, max_height / h)
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        return TransformEngine.resize(image, new_w, new_h, method)

    @staticmethod
    def rotate(image: np.ndarray, angle: float,
               expand: bool = True) -> np.ndarray:
        """
        Görüntüyü belirtilen açı kadar döndürür.
        expand=True ise tüm görüntü sığacak şekilde tuval genişler.
        """
        if image is None:
            return image

        h, w = image.shape[:2]
        center = (w // 2, h // 2)

        # Dönüşüm matrisini oluştur
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

        if expand:
            # Döndürülmüş görüntünün tam sığacağı boyutu hesapla
            cos = np.abs(rotation_matrix[0, 0])
            sin = np.abs(rotation_matrix[0, 1])
            new_w = int(h * sin + w * cos)
            new_h = int(h * cos + w * sin)
            rotation_matrix[0, 2] += (new_w - w) / 2
            rotation_matrix[1, 2] += (new_h - h) / 2
            return cv2.warpAffine(image, rotation_matrix, (new_w, new_h),
                                  borderMode=cv2.BORDER_CONSTANT,
                                  borderValue=(0, 0, 0))
        else:
            return cv2.warpAffine(image, rotation_matrix, (w, h))

    @staticmethod
    def flip_horizontal(image: np.ndarray) -> np.ndarray:
        """Görüntüyü yatay eksende çevirir (ayna efekti)."""
        if image is None:
            return image
        return cv2.flip(image, 1)

    @staticmethod
    def flip_vertical(image: np.ndarray) -> np.ndarray:
        """Görüntüyü dikey eksende çevirir."""
        if image is None:
            return image
        return cv2.flip(image, 0)

    @staticmethod
    def crop(image: np.ndarray, x: int, y: int,
             width: int, height: int) -> np.ndarray:
        """
        Görüntünün belirtilen bölgesini kırpar.
        Koordinatlar sınır kontrolünden geçirilir.
        """
        if image is None:
            return image

        h, w = image.shape[:2]
        # Sınır kontrolü
        x = max(0, min(x, w - 1))
        y = max(0, min(y, h - 1))
        x2 = min(x + width, w)
        y2 = min(y + height, h)

        if x2 <= x or y2 <= y:
            return image.copy()

        return image[y:y2, x:x2].copy()

    @staticmethod
    def auto_crop(image: np.ndarray, threshold: int = 10) -> np.ndarray:
        """
        Boş (tek renkli) kenarları otomatik kırpar.
        Eşik değeri ile hangi piksellerin 'boş' sayılacağı belirlenir.
        """
        if image is None:
            return image

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # İkili (binary) görüntüye dönüştür
        _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        # Beyaz piksellerin sınırlayıcı kutusunu bul
        coords = cv2.findNonZero(thresh)
        if coords is None:
            return image.copy()

        x, y, w, h = cv2.boundingRect(coords)
        return image[y:y + h, x:x + w].copy()
