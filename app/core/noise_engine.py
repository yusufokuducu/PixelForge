"""
Gürültü Motoru - Detaylı gürültü efektleri oluşturma modülü.
Farklı gürültü türleri, yoğunluk kontrolü, monokrom/renkli seçenekleri
ve ölçek parametresi ile profesyonel gürültü ekleme imkanı sağlar.
"""

import cv2
import numpy as np


class NoiseEngine:
    """
    Farklı gürültü türlerini uygulayan motor.
    Her metot şu parametreleri alır:
        - image: Giriş görüntüsü (BGR, uint8)
        - intensity: Gürültü yoğunluğu (0.0 - 1.0)
        - monochrome: True ise gri tonlamalı gürültü, False ise renkli
        - scale: Gürültü ölçeği (1.0 = piksel bazlı, >1 = büyük tanecikli)
    """

    @staticmethod
    def _generate_noise_layer(shape: tuple, monochrome: bool, scale: float) -> np.ndarray:
        """
        Temel gürültü katmanı oluşturur.
        Monokrom modda tek kanallı, renkli modda 3 kanallı gürültü üretir.
        Ölçek parametresi ile gürültü tanecik boyutu kontrol edilir.
        """
        h, w = shape[:2]

        if scale > 1.0:
            # Küçük boyutta üret, sonra büyüt (büyük tanecikli gürültü)
            small_h = max(1, int(h / scale))
            small_w = max(1, int(w / scale))
            if monochrome:
                noise_small = np.random.randn(small_h, small_w).astype(np.float32)
                noise = cv2.resize(noise_small, (w, h), interpolation=cv2.INTER_LINEAR)
                noise = np.dstack([noise] * 3)
            else:
                noise_small = np.random.randn(small_h, small_w, 3).astype(np.float32)
                noise = cv2.resize(noise_small, (w, h), interpolation=cv2.INTER_LINEAR)
        else:
            if monochrome:
                noise = np.random.randn(h, w).astype(np.float32)
                noise = np.dstack([noise] * 3)
            else:
                noise = np.random.randn(h, w, 3).astype(np.float32)

        return noise

    @staticmethod
    def gaussian(image: np.ndarray, intensity: float,
                 monochrome: bool = True, scale: float = 1.0) -> np.ndarray:
        """
        Gaussian Gürültü: En yaygın gürültü türü.
        Normal dağılıma sahip rastgele değerler eklenir.
        Doğal görüntü sensör gürültüsünü simüle eder.
        """
        if intensity <= 0:
            return image.copy()

        # Standart sapma yoğunluğa göre ayarlanır (0-80 arası)
        sigma = intensity * 80.0
        noise = NoiseEngine._generate_noise_layer(image.shape, monochrome, scale)

        # Gürültüyü görüntüye ekle
        noisy = image.astype(np.float32) + noise * sigma
        return np.clip(noisy, 0, 255).astype(np.uint8)

    @staticmethod
    def salt_pepper(image: np.ndarray, intensity: float,
                    monochrome: bool = True, scale: float = 1.0) -> np.ndarray:
        """
        Tuz & Biber Gürültüsü: Rastgele siyah ve beyaz pikseller ekler.
        Dijital iletim hatalarını simüle eder.
        """
        if intensity <= 0:
            return image.copy()

        result = image.copy()
        h, w = image.shape[:2]

        # Etkilenecek piksel oranı (yoğunluğa göre 0-%20)
        prob = intensity * 0.20

        if scale > 1.0:
            # Büyük tanecikli tuz-biber
            small_h = max(1, int(h / scale))
            small_w = max(1, int(w / scale))
            mask_small = np.random.random((small_h, small_w))
            mask = cv2.resize(mask_small, (w, h), interpolation=cv2.INTER_NEAREST)
        else:
            mask = np.random.random((h, w))

        # Tuz (beyaz piksel) ekleme
        salt_mask = mask < (prob / 2)
        if monochrome:
            result[salt_mask] = 255
        else:
            # Renkli modda rastgele kanalları etkile
            for c in range(3):
                channel_mask = salt_mask & (np.random.random((h, w)) > 0.5)
                result[:, :, c][channel_mask] = 255

        # Biber (siyah piksel) ekleme
        pepper_mask = mask > (1 - prob / 2)
        if monochrome:
            result[pepper_mask] = 0
        else:
            for c in range(3):
                channel_mask = pepper_mask & (np.random.random((h, w)) > 0.5)
                result[:, :, c][channel_mask] = 0

        return result

    @staticmethod
    def poisson(image: np.ndarray, intensity: float,
                monochrome: bool = True, scale: float = 1.0) -> np.ndarray:
        """
        Poisson Gürültüsü: Foton sayımına dayalı gürültü.
        Düşük ışıkta çekilmiş fotoğraflardaki gürültüyü simüle eder.
        """
        if intensity <= 0:
            return image.copy()

        # Poisson gürültüsü görüntü değerlerine bağlıdır
        # Lambda parametresini yoğunluğa göre ayarla
        lam = max(1.0, 256.0 / (1.0 + intensity * 50))

        noisy = np.random.poisson(image.astype(np.float32) / lam) * lam
        noisy = np.clip(noisy, 0, 255).astype(np.uint8)

        # Yoğunluk ile orijinali karıştır
        return cv2.addWeighted(image, 1.0 - intensity, noisy, intensity, 0)

    @staticmethod
    def speckle(image: np.ndarray, intensity: float,
                monochrome: bool = True, scale: float = 1.0) -> np.ndarray:
        """
        Speckle Gürültüsü: Çarpımsal gürültü.
        Radar/ultrason görüntülerdeki gürültüye benzer.
        Formül: noisy = image + image * noise
        """
        if intensity <= 0:
            return image.copy()

        noise = NoiseEngine._generate_noise_layer(image.shape, monochrome, scale)
        variance = intensity * 0.5

        # Çarpımsal gürültü: orijinal + orijinal × gürültü
        noisy = image.astype(np.float32) + image.astype(np.float32) * noise * variance
        return np.clip(noisy, 0, 255).astype(np.uint8)

    @staticmethod
    def uniform(image: np.ndarray, intensity: float,
                monochrome: bool = True, scale: float = 1.0) -> np.ndarray:
        """
        Düzgün (Uniform) Gürültü: Eşit olasılıklı rastgele değerler.
        Gaussian'dan daha sert ve belirgin bir gürültü oluşturur.
        """
        if intensity <= 0:
            return image.copy()

        h, w = image.shape[:2]
        amplitude = intensity * 80.0

        if scale > 1.0:
            small_h = max(1, int(h / scale))
            small_w = max(1, int(w / scale))
            if monochrome:
                noise_small = np.random.uniform(-amplitude, amplitude, (small_h, small_w)).astype(np.float32)
                noise = cv2.resize(noise_small, (w, h), interpolation=cv2.INTER_LINEAR)
                noise = np.dstack([noise] * 3)
            else:
                noise_small = np.random.uniform(-amplitude, amplitude, (small_h, small_w, 3)).astype(np.float32)
                noise = cv2.resize(noise_small, (w, h), interpolation=cv2.INTER_LINEAR)
        else:
            if monochrome:
                noise = np.random.uniform(-amplitude, amplitude, (h, w)).astype(np.float32)
                noise = np.dstack([noise] * 3)
            else:
                noise = np.random.uniform(-amplitude, amplitude, (h, w, 3)).astype(np.float32)

        noisy = image.astype(np.float32) + noise
        return np.clip(noisy, 0, 255).astype(np.uint8)

    @staticmethod
    def film_grain(image: np.ndarray, intensity: float,
                   monochrome: bool = True, scale: float = 1.0) -> np.ndarray:
        """
        Film Grain: Analog film tanecik efekti.
        Parlaklığa bağlı gürültü - koyu alanlarda daha belirgin.
        Gerçek film emülsiyonunu simüle eder.
        """
        if intensity <= 0:
            return image.copy()

        h, w = image.shape[:2]
        grain = NoiseEngine._generate_noise_layer(image.shape, monochrome, scale)

        # Parlaklık haritası oluştur (koyu alanlar daha fazla gürültü alır)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        # Koyu alanlarda daha güçlü, parlak alanlarda daha zayıf
        luminance_mask = 1.0 - gray * 0.6
        luminance_mask = np.dstack([luminance_mask] * 3)

        sigma = intensity * 60.0
        grain_weighted = grain * sigma * luminance_mask

        noisy = image.astype(np.float32) + grain_weighted
        return np.clip(noisy, 0, 255).astype(np.uint8)

    @staticmethod
    def color_noise(image: np.ndarray, intensity: float,
                    monochrome: bool = False, scale: float = 1.0) -> np.ndarray:
        """
        Renk Gürültüsü: Her renk kanalına bağımsız gürültü ekler.
        Dijital kamera sensörlerindeki renk gürültüsünü simüle eder.
        Monochrome parametresi burada her zaman False olarak davranır.
        """
        if intensity <= 0:
            return image.copy()

        h, w = image.shape[:2]
        sigma = intensity * 50.0

        # Her kanal için farklı gürültü üret (renk gürültüsünün doğası)
        if scale > 1.0:
            small_h = max(1, int(h / scale))
            small_w = max(1, int(w / scale))
            noise = np.zeros((h, w, 3), dtype=np.float32)
            for c in range(3):
                n = np.random.randn(small_h, small_w).astype(np.float32)
                noise[:, :, c] = cv2.resize(n, (w, h), interpolation=cv2.INTER_LINEAR)
        else:
            noise = np.random.randn(h, w, 3).astype(np.float32)

        noisy = image.astype(np.float32) + noise * sigma
        return np.clip(noisy, 0, 255).astype(np.uint8)

    @classmethod
    def apply_noise(cls, image: np.ndarray, noise_type: str,
                    intensity: float, monochrome: bool = True,
                    scale: float = 1.0) -> np.ndarray:
        """
        Gürültü türüne göre ilgili metodu çağıran fabrika metodu.
        Tek giriş noktası olarak dışarıdan kullanılır.
        """
        noise_map = {
            "gaussian":    cls.gaussian,
            "salt_pepper": cls.salt_pepper,
            "poisson":     cls.poisson,
            "speckle":     cls.speckle,
            "uniform":     cls.uniform,
            "film_grain":  cls.film_grain,
            "color_noise": cls.color_noise,
        }

        method = noise_map.get(noise_type)
        if method is None:
            return image.copy()

        return method(image, intensity, monochrome, scale)
