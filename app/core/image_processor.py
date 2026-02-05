"""
Ana Görüntü İşleme Motoru - Tüm düzenleme pipeline'ını yöneten merkezi modül.
İşlem sırası: Orijinal → Ayarlamalar → Filtreler → Gürültü → Sonuç
Tahribatsız (non-destructive) düzenleme yaklaşımı kullanılır.
"""

import cv2
import numpy as np
from typing import Optional

from app.core.filter_engine import FilterEngine
from app.core.noise_engine import NoiseEngine
from app.core.transform_engine import TransformEngine
from app.core.history_manager import HistoryManager
from app.utils.constants import PREVIEW_MAX_WIDTH, PREVIEW_MAX_HEIGHT
from app.utils.image_utils import create_preview


class ImageProcessor:
    """
    Merkezi görüntü işleme sınıfı.
    - Orijinal görüntüyü saklar
    - Tüm parametrelere göre pipeline'ı çalıştırır
    - Önizleme ve tam çözünürlük modlarını yönetir
    - Geçmiş (undo/redo) entegrasyonu sağlar
    """

    def __init__(self):
        # Orijinal (düzenlenmemiş) görüntü - tam çözünürlük
        self._original: Optional[np.ndarray] = None
        # Önizleme boyutunda orijinal kopya (performans için)
        self._preview_original: Optional[np.ndarray] = None
        # Son işlenmiş sonuç
        self._processed: Optional[np.ndarray] = None
        # Geçmiş yöneticisi
        self._history = HistoryManager()
        # Dosya yolu bilgisi
        self._file_path: Optional[str] = None

        # ─── Mevcut düzenleme parametreleri ────────────────────────
        # Ayarlamalar (adjustment) parametreleri
        self._adjustments: dict[str, float] = {
            "brightness": 0, "contrast": 0, "saturation": 0,
            "hue": 0, "gamma": 100, "exposure": 0,
            "temperature": 0, "tint": 0,
            "highlights": 0, "shadows": 0,
            "clarity": 0, "vibrance": 0, "sharpness": 0,
        }

        # Filtre parametreleri (her filtre için yoğunluk 0-100)
        self._filters: dict[str, int] = {}

        # Gürültü parametreleri
        self._noise_params: dict = {
            "type": "gaussian",
            "intensity": 0,
            "monochrome": True,
            "scale": 1.0,
        }

    # ─── Dosya İşlemleri ──────────────────────────────────────────────

    def load_image(self, file_path: str) -> bool:
        """
        Dosyadan görüntü yükler.
        Başarılıysa True, değilse False döndürür.
        """
        try:
            # OpenCV ile oku (BGR formatında)
            image = cv2.imread(file_path, cv2.IMREAD_COLOR)
            if image is None:
                return False

            self._original = image
            self._file_path = file_path
            self._preview_original = create_preview(
                image, PREVIEW_MAX_WIDTH, PREVIEW_MAX_HEIGHT
            )
            self._processed = None

            # Geçmişi sıfırla ve ilk durumu kaydet
            self._history.clear()
            self._history.push_state(image)

            # Tüm parametreleri sıfırla
            self._reset_all_params()
            return True

        except Exception:
            return False

    def save_image(self, file_path: str, quality: int = 95) -> bool:
        """
        İşlenmiş görüntüyü dosyaya kaydeder.
        Tam çözünürlükte işleme yapılır.
        """
        try:
            # Tam çözünürlükte pipeline'ı çalıştır
            result = self.process_full_resolution()
            if result is None:
                return False

            # Dosya uzantısına göre kaydetme parametreleri
            ext = file_path.lower().rsplit('.', 1)[-1]
            params = []
            if ext in ('jpg', 'jpeg'):
                params = [cv2.IMWRITE_JPEG_QUALITY, quality]
            elif ext == 'png':
                params = [cv2.IMWRITE_PNG_COMPRESSION, max(0, min(9, (100 - quality) // 10))]
            elif ext == 'webp':
                params = [cv2.IMWRITE_WEBP_QUALITY, quality]

            return cv2.imwrite(file_path, result, params)

        except Exception:
            return False

    # ─── Parametre Yönetimi ───────────────────────────────────────────

    def set_adjustment(self, key: str, value: float) -> None:
        """Bir ayarlama parametresini günceller."""
        if key in self._adjustments:
            self._adjustments[key] = value

    def set_filter(self, filter_name: str, intensity: int) -> None:
        """Bir filtrenin yoğunluğunu ayarlar (0 = kapalı)."""
        if intensity <= 0:
            self._filters.pop(filter_name, None)
        else:
            self._filters[filter_name] = intensity

    def set_noise_params(self, **kwargs) -> None:
        """Gürültü parametrelerini günceller."""
        for key, value in kwargs.items():
            if key in self._noise_params:
                self._noise_params[key] = value

    def get_adjustment(self, key: str) -> float:
        """Belirtilen ayarlama parametresinin değerini döndürür."""
        return self._adjustments.get(key, 0)

    def get_filter_intensity(self, filter_name: str) -> int:
        """Belirtilen filtrenin yoğunluğunu döndürür."""
        return self._filters.get(filter_name, 0)

    def _reset_all_params(self) -> None:
        """Tüm düzenleme parametrelerini varsayılanlara sıfırlar."""
        self._adjustments = {
            "brightness": 0, "contrast": 0, "saturation": 0,
            "hue": 0, "gamma": 100, "exposure": 0,
            "temperature": 0, "tint": 0,
            "highlights": 0, "shadows": 0,
            "clarity": 0, "vibrance": 0, "sharpness": 0,
        }
        self._filters.clear()
        self._noise_params = {
            "type": "gaussian", "intensity": 0,
            "monochrome": True, "scale": 1.0,
        }

    # ─── İşleme Pipeline ─────────────────────────────────────────────

    def process_preview(self) -> Optional[np.ndarray]:
        """
        Önizleme boyutunda görüntü işleme pipeline'ını çalıştırır.
        Gerçek zamanlı slider geri bildirimi için optimize edilmiştir.
        """
        if self._preview_original is None:
            return None
        return self._run_pipeline(self._preview_original)

    def process_full_resolution(self) -> Optional[np.ndarray]:
        """
        Tam çözünürlükte görüntü işleme pipeline'ını çalıştırır.
        Kaydetme ve 'Uygula' işlemleri için kullanılır.
        """
        if self._original is None:
            return None
        return self._run_pipeline(self._original)

    def _run_pipeline(self, source: np.ndarray) -> np.ndarray:
        """
        Ana işleme pipeline'ı. Sırasıyla:
        1. Ayarlamaları uygula (parlaklık, kontrast, doygunluk, vb.)
        2. Aktif filtreleri uygula
        3. Gürültü efektini uygula (varsa)
        """
        result = source.copy()

        # ── Adım 1: Ayarlamalar ──
        result = self._apply_adjustments(result)

        # ── Adım 2: Filtreler ──
        result = self._apply_filters(result)

        # ── Adım 3: Gürültü ──
        result = self._apply_noise(result)

        self._processed = result
        return result

    def _apply_adjustments(self, image: np.ndarray) -> np.ndarray:
        """
        Tüm ayarlama parametrelerini sırayla uygular.
        Her ayarlama bağımsız olarak çalışır ve birbirini etkiler.
        """
        result = image.copy()

        # ── Parlaklık & Kontrast ──
        brightness = self._adjustments["brightness"]
        contrast = self._adjustments["contrast"]
        if brightness != 0 or contrast != 0:
            # Kontrast: alpha katsayısı (0.5 - 1.5 arası)
            alpha = 1.0 + contrast / 100.0
            # Parlaklık: beta değeri (-100 - 100 arası)
            beta = brightness * 2.55  # 0-255 aralığına ölçekle
            result = cv2.convertScaleAbs(result, alpha=alpha, beta=beta)

        # ── Pozlama (Exposure) ──
        exposure = self._adjustments["exposure"] / 100.0
        if exposure != 0:
            # EV (Exposure Value) cinsinden: 2^EV çarpanı
            factor = pow(2, exposure)
            result = np.clip(result.astype(np.float32) * factor, 0, 255).astype(np.uint8)

        # ── Gama Düzeltme ──
        gamma = self._adjustments["gamma"] / 100.0  # Slider 10-300, gerçek 0.1-3.0
        if abs(gamma - 1.0) > 0.01:
            inv_gamma = 1.0 / gamma
            # Arama tablosu ile hızlı gama dönüşümü
            table = np.array([
                ((i / 255.0) ** inv_gamma) * 255
                for i in range(256)
            ], dtype=np.uint8)
            result = cv2.LUT(result, table)

        # ── HSV Tabanlı Ayarlamalar (Doygunluk, Ton, Canlılık) ──
        saturation = self._adjustments["saturation"]
        hue = self._adjustments["hue"]
        vibrance = self._adjustments["vibrance"]

        if saturation != 0 or hue != 0 or vibrance != 0:
            hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)

            # Ton (Hue) kaydırma
            if hue != 0:
                hsv[:, :, 0] = (hsv[:, :, 0] + hue / 2) % 180

            # Doygunluk ayarı
            if saturation != 0:
                factor = 1.0 + saturation / 100.0
                hsv[:, :, 1] = np.clip(hsv[:, :, 1] * factor, 0, 255)

            # Canlılık (düşük doygunluğu daha çok etkiler)
            if vibrance != 0:
                s = hsv[:, :, 1]
                # Düşük doygunluklu piksellere daha fazla etki
                low_sat_mask = 1.0 - (s / 255.0)
                boost = (vibrance / 100.0) * low_sat_mask * 50
                hsv[:, :, 1] = np.clip(s + boost, 0, 255)

            hsv = np.clip(hsv, 0, 255).astype(np.uint8)
            result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        # ── Sıcaklık (Temperature) ──
        temperature = self._adjustments["temperature"]
        if temperature != 0:
            result = result.astype(np.float32)
            # Sıcak: Kırmızı artır, Mavi azalt | Soğuk: tersi
            shift = temperature * 0.3
            result[:, :, 0] = np.clip(result[:, :, 0] - shift, 0, 255)  # Mavi
            result[:, :, 2] = np.clip(result[:, :, 2] + shift, 0, 255)  # Kırmızı
            result = result.astype(np.uint8)

        # ── Renk Tonu (Tint) ──
        tint = self._adjustments["tint"]
        if tint != 0:
            result = result.astype(np.float32)
            # Yeşil-Magenta ekseni
            shift = tint * 0.3
            result[:, :, 1] = np.clip(result[:, :, 1] + shift, 0, 255)  # Yeşil
            result = result.astype(np.uint8)

        # ── Açık Tonlar (Highlights) ──
        highlights = self._adjustments["highlights"]
        if highlights != 0:
            result = self._adjust_tonal_range(result, highlights, is_highlights=True)

        # ── Koyu Tonlar (Shadows) ──
        shadows = self._adjustments["shadows"]
        if shadows != 0:
            result = self._adjust_tonal_range(result, shadows, is_highlights=False)

        # ── Netlik (Clarity) ──
        clarity = self._adjustments["clarity"]
        if clarity != 0:
            result = self._apply_clarity(result, clarity)

        # ── Keskinlik (Sharpness) ──
        sharpness = self._adjustments["sharpness"]
        if sharpness > 0:
            amount = sharpness / 100.0
            blurred = cv2.GaussianBlur(result, (0, 0), 2)
            result = cv2.addWeighted(result, 1 + amount, blurred, -amount, 0)
            result = np.clip(result, 0, 255).astype(np.uint8)

        return result

    @staticmethod
    def _adjust_tonal_range(image: np.ndarray, value: float,
                            is_highlights: bool) -> np.ndarray:
        """
        Açık veya koyu ton aralığını seçici olarak ayarlar.
        Parlaklık maskesi kullanarak yalnızca hedef aralığı etkiler.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0

        if is_highlights:
            # Parlak pikselleri seç (sigmoid tabanlı maske)
            mask = np.clip((gray - 0.5) * 2, 0, 1)
        else:
            # Koyu pikselleri seç
            mask = np.clip((0.5 - gray) * 2, 0, 1)

        mask = np.dstack([mask] * 3)
        adjustment = value * 2.55 * mask  # 0-255 aralığına ölçekle
        result = image.astype(np.float32) + adjustment
        return np.clip(result, 0, 255).astype(np.uint8)

    @staticmethod
    def _apply_clarity(image: np.ndarray, value: float) -> np.ndarray:
        """
        Netlik efekti: Orta tonlardaki kontrastı artırır/azaltır.
        Lokal kontrast manipülasyonu ile detay vurgusu sağlar.
        """
        # Büyük çekirdekli bulanıklık ile düşük frekans bileşeni
        blurred = cv2.GaussianBlur(image, (0, 0), 10)
        # Detay katmanı = orijinal - bulanık
        detail = cv2.subtract(image, blurred)
        # Detayı güçlendir/zayıflat
        factor = value / 50.0
        enhanced = cv2.addWeighted(image, 1.0, detail, factor, 0)
        return np.clip(enhanced, 0, 255).astype(np.uint8)

    def _apply_filters(self, image: np.ndarray) -> np.ndarray:
        """Tüm aktif filtreleri sırayla uygular."""
        result = image
        for filter_name, intensity in self._filters.items():
            if intensity > 0:
                normalized_intensity = intensity / 100.0
                result = FilterEngine.apply_filter(result, filter_name, normalized_intensity)
        return result

    def _apply_noise(self, image: np.ndarray) -> np.ndarray:
        """Gürültü efektini uygular (yoğunluk > 0 ise)."""
        intensity = self._noise_params.get("intensity", 0)
        if intensity <= 0:
            return image

        return NoiseEngine.apply_noise(
            image=image,
            noise_type=self._noise_params["type"],
            intensity=intensity / 100.0,
            monochrome=self._noise_params.get("monochrome", True),
            scale=self._noise_params.get("scale", 1.0),
        )

    # ─── Dönüşüm İşlemleri ───────────────────────────────────────────

    def apply_resize(self, width: int, height: int, method: str = "lanczos") -> None:
        """Görüntüyü yeniden boyutlandırır ve geçmişe kaydeder."""
        if self._original is None:
            return

        self._original = TransformEngine.resize(self._original, width, height, method)
        self._preview_original = create_preview(
            self._original, PREVIEW_MAX_WIDTH, PREVIEW_MAX_HEIGHT
        )
        self._history.push_state(self._original)
        self._reset_all_params()

    def apply_rotation(self, angle: float) -> None:
        """Görüntüyü döndürür ve geçmişe kaydeder."""
        if self._original is None:
            return

        self._original = TransformEngine.rotate(self._original, angle)
        self._preview_original = create_preview(
            self._original, PREVIEW_MAX_WIDTH, PREVIEW_MAX_HEIGHT
        )
        self._history.push_state(self._original)

    def apply_flip(self, horizontal: bool = True) -> None:
        """Görüntüyü çevirir ve geçmişe kaydeder."""
        if self._original is None:
            return

        if horizontal:
            self._original = TransformEngine.flip_horizontal(self._original)
        else:
            self._original = TransformEngine.flip_vertical(self._original)

        self._preview_original = create_preview(
            self._original, PREVIEW_MAX_WIDTH, PREVIEW_MAX_HEIGHT
        )
        self._history.push_state(self._original)

    def apply_crop(self, x: int, y: int, w: int, h: int) -> None:
        """Görüntüyü kırpar ve geçmişe kaydeder."""
        if self._original is None:
            return

        self._original = TransformEngine.crop(self._original, x, y, w, h)
        self._preview_original = create_preview(
            self._original, PREVIEW_MAX_WIDTH, PREVIEW_MAX_HEIGHT
        )
        self._history.push_state(self._original)
        self._reset_all_params()

    # ─── Değişiklikleri Uygulama ──────────────────────────────────────

    def apply_current_changes(self) -> None:
        """
        Mevcut tüm düzenlemeleri kalıcı olarak uygular.
        İşlenmiş görüntü yeni 'orijinal' olur.
        Tüm slider'lar sıfırlanır.
        """
        if self._original is None:
            return

        # Tam çözünürlükte işle
        processed = self.process_full_resolution()
        if processed is not None:
            self._original = processed
            self._preview_original = create_preview(
                self._original, PREVIEW_MAX_WIDTH, PREVIEW_MAX_HEIGHT
            )
            self._history.push_state(self._original)
            self._reset_all_params()

    # ─── Geçmiş (Undo/Redo) ──────────────────────────────────────────

    def undo(self) -> bool:
        """Geri al. Başarılıysa True döndürür."""
        state = self._history.undo()
        if state is not None:
            self._original = state
            self._preview_original = create_preview(
                self._original, PREVIEW_MAX_WIDTH, PREVIEW_MAX_HEIGHT
            )
            self._reset_all_params()
            return True
        return False

    def redo(self) -> bool:
        """Yeniden yap. Başarılıysa True döndürür."""
        state = self._history.redo()
        if state is not None:
            self._original = state
            self._preview_original = create_preview(
                self._original, PREVIEW_MAX_WIDTH, PREVIEW_MAX_HEIGHT
            )
            self._reset_all_params()
            return True
        return False

    def can_undo(self) -> bool:
        return self._history.can_undo()

    def can_redo(self) -> bool:
        return self._history.can_redo()

    # ─── Özellikler (Properties) ──────────────────────────────────────

    @property
    def original(self) -> Optional[np.ndarray]:
        return self._original

    @property
    def preview_original(self) -> Optional[np.ndarray]:
        return self._preview_original

    @property
    def processed(self) -> Optional[np.ndarray]:
        return self._processed

    @property
    def file_path(self) -> Optional[str]:
        return self._file_path

    @property
    def has_image(self) -> bool:
        return self._original is not None

    @property
    def image_size(self) -> tuple[int, int]:
        """(genişlik, yükseklik) tuple'ı döndürür."""
        if self._original is None:
            return (0, 0)
        h, w = self._original.shape[:2]
        return (w, h)

    def has_pending_changes(self) -> bool:
        """Uygulanmamış değişiklik var mı kontrolü."""
        for v in self._adjustments.values():
            if v != 0 and v != 100:  # gamma varsayılanı 100
                return True
        if self._filters:
            return True
        if self._noise_params.get("intensity", 0) > 0:
            return True
        return False
