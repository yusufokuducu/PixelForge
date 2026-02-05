"""
Filtre Motoru - Tüm görüntü filtrelerinin uygulandığı modül.
Her filtre, yoğunluk (intensity) parametresi ile kontrol edilir.
Yoğunluk 0.0-1.0 arasında olup, orijinal ile filtrelenmiş görüntü
arasında doğrusal enterpolasyon (blending) yapılır.
"""

import cv2
import numpy as np


class FilterEngine:
    """
    Statik filtre metotları içeren ana filtre motoru.
    Her metot (image, intensity) parametreleri alır ve işlenmiş görüntüyü döndürür.
    Intensity = 0.0 → Orijinal, Intensity = 1.0 → Tam filtre etkisi.
    """

    @staticmethod
    def _blend(original: np.ndarray, filtered: np.ndarray, intensity: float) -> np.ndarray:
        """
        Orijinal ve filtrelenmiş görüntüyü yoğunluğa göre karıştırır.
        Bu, her filtrede kademeli geçiş sağlar.
        """
        if intensity <= 0.0:
            return original.copy()
        if intensity >= 1.0:
            return filtered
        return cv2.addWeighted(original, 1.0 - intensity, filtered, intensity, 0)

    @staticmethod
    def gaussian_blur(image: np.ndarray, intensity: float) -> np.ndarray:
        """
        Gaussian Bulanıklık: Yumuşak, doğal görünümlü bulanıklaştırma.
        Çekirdek boyutu yoğunluğa göre dinamik olarak hesaplanır.
        """
        if intensity <= 0:
            return image.copy()
        # Çekirdek boyutunu yoğunluğa göre ayarla (1-51 arası, tek sayı olmalı)
        ksize = int(intensity * 50) | 1  # Bitwise OR ile tek sayı garantisi
        ksize = max(1, min(ksize, 51))
        blurred = cv2.GaussianBlur(image, (ksize, ksize), 0)
        return FilterEngine._blend(image, blurred, intensity)

    @staticmethod
    def box_blur(image: np.ndarray, intensity: float) -> np.ndarray:
        """
        Kutu Bulanıklık: Eşit ağırlıklı ortalama filtresi.
        Gaussian'dan daha agresif bulanıklaştırma sağlar.
        """
        if intensity <= 0:
            return image.copy()
        ksize = int(intensity * 40) | 1
        ksize = max(1, min(ksize, 41))
        blurred = cv2.blur(image, (ksize, ksize))
        return FilterEngine._blend(image, blurred, intensity)

    @staticmethod
    def median_blur(image: np.ndarray, intensity: float) -> np.ndarray:
        """
        Medyan Bulanıklık: Tuz-biber gürültüsünü temizlemede etkilidir.
        Kenarları koruyarak bulanıklaştırma yapar.
        """
        if intensity <= 0:
            return image.copy()
        ksize = int(intensity * 30) | 1
        ksize = max(3, min(ksize, 31))
        blurred = cv2.medianBlur(image, ksize)
        return FilterEngine._blend(image, blurred, intensity)

    @staticmethod
    def sharpen(image: np.ndarray, intensity: float) -> np.ndarray:
        """
        Keskinleştirme: Kenarları vurgulayarak detayları ortaya çıkarır.
        Unsharp maskeleme tekniği kullanılır.
        """
        if intensity <= 0:
            return image.copy()
        # Gaussian bulanıklık ile orijinal arasındaki farkı kullanarak keskinleştir
        gaussian = cv2.GaussianBlur(image, (0, 0), 3)
        sharpened = cv2.addWeighted(image, 1.5, gaussian, -0.5, 0)
        return FilterEngine._blend(image, sharpened, intensity)

    @staticmethod
    def unsharp_mask(image: np.ndarray, intensity: float) -> np.ndarray:
        """
        Unsharp Mask: Profesyonel keskinleştirme tekniği.
        Daha kontrollü ve doğal keskinleştirme sağlar.
        """
        if intensity <= 0:
            return image.copy()
        # Sigma ve güç değerlerini yoğunluğa göre ayarla
        sigma = 1.0 + intensity * 4.0
        amount = 0.5 + intensity * 2.0
        gaussian = cv2.GaussianBlur(image, (0, 0), sigma)
        sharpened = cv2.addWeighted(image, 1.0 + amount, gaussian, -amount, 0)
        sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
        return FilterEngine._blend(image, sharpened, intensity)

    @staticmethod
    def edge_detect(image: np.ndarray, intensity: float) -> np.ndarray:
        """
        Kenar Algılama: Canny algoritması ile kenarları tespit eder.
        Sonuç renkli görüntüyle harmanlanır.
        """
        if intensity <= 0:
            return image.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Eşik değerlerini dinamik olarak hesapla
        threshold1 = int(50 * (1 - intensity * 0.5))
        threshold2 = int(150 * (1 - intensity * 0.5))
        edges = cv2.Canny(gray, threshold1, threshold2)
        # Tek kanallı kenar haritasını 3 kanala dönüştür
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return FilterEngine._blend(image, edges_bgr, intensity)

    @staticmethod
    def emboss(image: np.ndarray, intensity: float) -> np.ndarray:
        """
        Kabartma Efekti: 3D kabartma görüntüsü oluşturur.
        Konvolüsyon çekirdeği ile ışık-gölge simülasyonu yapar.
        """
        if intensity <= 0:
            return image.copy()
        # Kabartma çekirdeği (kernel)
        kernel = np.array([[-2, -1, 0],
                           [-1,  1, 1],
                           [ 0,  1, 2]], dtype=np.float32)
        embossed = cv2.filter2D(image, -1, kernel) + 128
        embossed = np.clip(embossed, 0, 255).astype(np.uint8)
        return FilterEngine._blend(image, embossed, intensity)

    @staticmethod
    def sepia(image: np.ndarray, intensity: float) -> np.ndarray:
        """
        Sepya Filtresi: Nostaljik, sıcak tonlu kahverengi efekt.
        Renk dönüşüm matrisi kullanılır.
        """
        if intensity <= 0:
            return image.copy()
        # Sepya dönüşüm matrisi (BGR formatında)
        sepia_matrix = np.array([
            [0.272, 0.534, 0.131],
            [0.349, 0.686, 0.168],
            [0.393, 0.769, 0.189]
        ], dtype=np.float32)
        sepia_img = cv2.transform(image, sepia_matrix)
        sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
        return FilterEngine._blend(image, sepia_img, intensity)

    @staticmethod
    def vintage(image: np.ndarray, intensity: float) -> np.ndarray:
        """
        Vintage Filtre: Eski fotoğraf görünümü.
        Sepya tonu + vinyet + hafif solma efekti birleştirilir.
        """
        if intensity <= 0:
            return image.copy()

        h, w = image.shape[:2]

        # Adım 1: Hafif sepya tonu ekle
        sepia_matrix = np.array([
            [0.30, 0.52, 0.15],
            [0.35, 0.67, 0.17],
            [0.38, 0.74, 0.19]
        ], dtype=np.float32)
        vintage_img = cv2.transform(image, sepia_matrix)
        vintage_img = np.clip(vintage_img, 0, 255).astype(np.uint8)

        # Adım 2: Kontrastı azalt (solmuş görünüm)
        vintage_img = cv2.convertScaleAbs(vintage_img, alpha=0.9, beta=15)

        # Adım 3: Hafif vinyet ekle
        center_x, center_y = w // 2, h // 2
        Y, X = np.ogrid[:h, :w]
        dist = np.sqrt((X - center_x) ** 2 + (Y - center_y) ** 2)
        max_dist = np.sqrt(center_x ** 2 + center_y ** 2)
        vignette_mask = 1 - (dist / max_dist) * 0.4
        vignette_mask = np.clip(vignette_mask, 0, 1)
        vignette_mask = np.dstack([vignette_mask] * 3).astype(np.float32)
        vintage_img = (vintage_img.astype(np.float32) * vignette_mask).astype(np.uint8)

        return FilterEngine._blend(image, vintage_img, intensity)

    @staticmethod
    def vignette(image: np.ndarray, intensity: float) -> np.ndarray:
        """
        Vinyet Efekti: Köşeleri karartarak merkeze odaklanma sağlar.
        Gaussian tabanlı yumuşak geçiş kullanılır.
        """
        if intensity <= 0:
            return image.copy()

        h, w = image.shape[:2]
        # Merkez koordinatları
        center_x, center_y = w // 2, h // 2

        # Mesafe haritası oluştur
        Y, X = np.ogrid[:h, :w]
        dist = np.sqrt((X - center_x) ** 2 + (Y - center_y) ** 2)
        max_dist = np.sqrt(center_x ** 2 + center_y ** 2)

        # Vinyet maskesi (merkez = 1, kenarlar = 0)
        vignette_strength = 0.3 + intensity * 0.7
        mask = 1 - (dist / max_dist) * vignette_strength
        mask = np.clip(mask, 0, 1)
        mask = cv2.GaussianBlur(mask, (0, 0), max(w, h) * 0.05)
        mask = np.dstack([mask] * 3).astype(np.float32)

        vignetted = (image.astype(np.float32) * mask).astype(np.uint8)
        return FilterEngine._blend(image, vignetted, intensity)

    @staticmethod
    def hdr_effect(image: np.ndarray, intensity: float) -> np.ndarray:
        """
        HDR Efekti: Yüksek dinamik aralık simülasyonu.
        Detay haritası çıkarılarak lokal kontrast artırılır.
        """
        if intensity <= 0:
            return image.copy()

        # Detay katmanını çıkar (orijinal - bulanık = detay)
        sigma = 15
        blurred = cv2.GaussianBlur(image, (0, 0), sigma)
        detail = cv2.subtract(image, blurred)

        # Detay katmanını güçlendir ve geri ekle
        boost = 1.0 + intensity * 2.0
        detail_boosted = cv2.convertScaleAbs(detail, alpha=boost, beta=0)
        hdr = cv2.add(image, detail_boosted)

        # Doygunluğu hafifçe artır
        hsv = cv2.cvtColor(hdr, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + intensity * 0.3), 0, 255)
        hdr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

        return FilterEngine._blend(image, hdr, intensity)

    @staticmethod
    def pencil_sketch(image: np.ndarray, intensity: float) -> np.ndarray:
        """
        Kalem Çizimi: Fotoğrafı kalem eskizine dönüştürür.
        Gaussian bulanıklık ve bölme tekniği kullanılır.
        """
        if intensity <= 0:
            return image.copy()

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inv = 255 - gray

        # Bulanıklaştırma miktarını yoğunluğa göre ayarla
        sigma = 10 + intensity * 40
        blurred_inv = cv2.GaussianBlur(inv, (0, 0), sigma)

        # Bölme ile eskiz elde et (dodge blend)
        sketch = cv2.divide(gray, 255 - blurred_inv, scale=256)
        sketch_bgr = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

        return FilterEngine._blend(image, sketch_bgr, intensity)

    @staticmethod
    def oil_painting(image: np.ndarray, intensity: float) -> np.ndarray:
        """
        Yağlıboya Efekti: Bilateral filtre ile yağlıboya görünümü.
        Kenarları koruyarak yüzeyleri düzleştirir.
        """
        if intensity <= 0:
            return image.copy()

        # Bilateral filtre parametrelerini yoğunluğa göre ayarla
        d = int(5 + intensity * 10)
        sigma_color = 30 + intensity * 120
        sigma_space = 30 + intensity * 120

        # Birden fazla geçiş ile daha güçlü efekt
        oil = image.copy()
        passes = max(1, int(intensity * 3))
        for _ in range(passes):
            oil = cv2.bilateralFilter(oil, d, sigma_color, sigma_space)

        return FilterEngine._blend(image, oil, intensity)

    @staticmethod
    def pixelate(image: np.ndarray, intensity: float) -> np.ndarray:
        """
        Pikselleştirme: Görüntüyü büyük piksellere böler.
        Küçültüp tekrar büyütme tekniği ile yapılır.
        """
        if intensity <= 0:
            return image.copy()

        h, w = image.shape[:2]
        # Piksel boyutunu hesapla (2-64 arası)
        pixel_size = max(2, int(intensity * 64))

        # Küçült ve tekrar büyüt (nearest neighbor ile piksel efekti)
        small_w = max(1, w // pixel_size)
        small_h = max(1, h // pixel_size)
        small = cv2.resize(image, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
        pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

        return FilterEngine._blend(image, pixelated, intensity)

    @staticmethod
    def posterize(image: np.ndarray, intensity: float) -> np.ndarray:
        """
        Posterize: Renk sayısını azaltarak poster efekti oluşturur.
        Kuantizasyon ile belirli sayıda renk seviyesine indirgenir.
        """
        if intensity <= 0:
            return image.copy()

        # Renk seviyesi sayısı (2-16 arası, ters orantılı)
        levels = max(2, int(16 - intensity * 14))
        step = 256 // levels
        posterized = (image // step) * step + step // 2
        posterized = np.clip(posterized, 0, 255).astype(np.uint8)

        return FilterEngine._blend(image, posterized, intensity)

    @staticmethod
    def warm_filter(image: np.ndarray, intensity: float) -> np.ndarray:
        """
        Sıcak Filtre: Görüntüye sıcak (turuncu/sarı) tonlar ekler.
        Kırmızı ve yeşil kanalları artırır, maviyi azaltır.
        """
        if intensity <= 0:
            return image.copy()

        warm = image.astype(np.float32)
        # BGR formatında: B kanalını azalt, R kanalını artır
        strength = intensity * 30
        warm[:, :, 0] = np.clip(warm[:, :, 0] - strength, 0, 255)      # Mavi azalt
        warm[:, :, 1] = np.clip(warm[:, :, 1] + strength * 0.3, 0, 255)  # Yeşil hafif artır
        warm[:, :, 2] = np.clip(warm[:, :, 2] + strength, 0, 255)      # Kırmızı artır

        return FilterEngine._blend(image, warm.astype(np.uint8), intensity)

    @staticmethod
    def cool_filter(image: np.ndarray, intensity: float) -> np.ndarray:
        """
        Soğuk Filtre: Görüntüye soğuk (mavi) tonlar ekler.
        Mavi kanalı artırır, kırmızıyı azaltır.
        """
        if intensity <= 0:
            return image.copy()

        cool = image.astype(np.float32)
        strength = intensity * 30
        cool[:, :, 0] = np.clip(cool[:, :, 0] + strength, 0, 255)      # Mavi artır
        cool[:, :, 2] = np.clip(cool[:, :, 2] - strength, 0, 255)      # Kırmızı azalt

        return FilterEngine._blend(image, cool.astype(np.uint8), intensity)

    @staticmethod
    def dramatic(image: np.ndarray, intensity: float) -> np.ndarray:
        """
        Dramatik Efekt: Yüksek kontrast + desatürasyon + vinyet.
        Sinematik bir görünüm oluşturur.
        """
        if intensity <= 0:
            return image.copy()

        # Adım 1: Kontrastı artır
        dramatic = cv2.convertScaleAbs(image, alpha=1.0 + intensity * 0.5, beta=-10 * intensity)

        # Adım 2: Doygunluğu kısmen azalt
        hsv = cv2.cvtColor(dramatic, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = hsv[:, :, 1] * (1 - intensity * 0.4)
        dramatic = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

        # Adım 3: Vinyet ekle
        h, w = dramatic.shape[:2]
        Y, X = np.ogrid[:h, :w]
        center_x, center_y = w // 2, h // 2
        dist = np.sqrt((X - center_x) ** 2 + (Y - center_y) ** 2)
        max_dist = np.sqrt(center_x ** 2 + center_y ** 2)
        mask = 1 - (dist / max_dist) * 0.5 * intensity
        mask = np.clip(mask, 0, 1)
        mask = np.dstack([mask] * 3).astype(np.float32)
        dramatic = (dramatic.astype(np.float32) * mask).astype(np.uint8)

        return FilterEngine._blend(image, dramatic, intensity)

    @classmethod
    def apply_filter(cls, image: np.ndarray, filter_name: str, intensity: float) -> np.ndarray:
        """
        Filtre adına göre ilgili metodu çağırır.
        Bu, dışarıdan tek bir giriş noktası sağlayan fabrika metodudur.
        """
        # Filtre adı → metot eşleştirmesi
        filter_map = {
            "gaussian_blur": cls.gaussian_blur,
            "box_blur":      cls.box_blur,
            "median_blur":   cls.median_blur,
            "sharpen":       cls.sharpen,
            "unsharp_mask":  cls.unsharp_mask,
            "edge_detect":   cls.edge_detect,
            "emboss":        cls.emboss,
            "sepia":         cls.sepia,
            "vintage":       cls.vintage,
            "vignette":      cls.vignette,
            "hdr_effect":    cls.hdr_effect,
            "pencil_sketch": cls.pencil_sketch,
            "oil_painting":  cls.oil_painting,
            "pixelate":      cls.pixelate,
            "posterize":     cls.posterize,
            "warm_filter":   cls.warm_filter,
            "cool_filter":   cls.cool_filter,
            "dramatic":      cls.dramatic,
        }

        method = filter_map.get(filter_name)
        if method is None:
            return image.copy()

        return method(image, intensity)
