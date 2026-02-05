"""
Uygulama genelinde kullanılan sabitler ve yapılandırma değerleri.
Tüm sabit değerler merkezi olarak burada tanımlanır.
"""

# ─── Uygulama Bilgileri ───────────────────────────────────────────────
APP_NAME = "PixelForge"
APP_VERSION = "1.0.0"
APP_AUTHOR = "PixelForge Studio"

# ─── Önizleme Ayarları ────────────────────────────────────────────────
# Gerçek zamanlı düzenleme için maksimum önizleme çözünürlüğü
PREVIEW_MAX_WIDTH = 1920
PREVIEW_MAX_HEIGHT = 1080

# ─── Debounce Süresi (ms) ─────────────────────────────────────────────
# Slider değişikliklerinde işleme gecikmesi (performans için)
SLIDER_DEBOUNCE_MS = 60

# ─── Geçmiş (Undo/Redo) ───────────────────────────────────────────────
MAX_HISTORY_STATES = 30

# ─── Desteklenen Dosya Formatları ──────────────────────────────────────
SUPPORTED_IMAGE_FORMATS = (
    "PNG Dosyaları (*.png);;JPEG Dosyaları (*.jpg *.jpeg);;"
    "BMP Dosyaları (*.bmp);;TIFF Dosyaları (*.tiff *.tif);;"
    "WebP Dosyaları (*.webp);;Tüm Dosyalar (*)"
)

SAVE_IMAGE_FORMATS = (
    "PNG (*.png);;JPEG (*.jpg);;BMP (*.bmp);;"
    "TIFF (*.tiff);;WebP (*.webp)"
)

# ─── Ayar (Adjustment) Aralıkları ─────────────────────────────────────
# Her ayar parametresi: (minimum, maksimum, varsayılan, adım)
ADJUSTMENT_RANGES = {
    "brightness":  (-100, 100, 0, 1),
    "contrast":    (-100, 100, 0, 1),
    "saturation":  (-100, 100, 0, 1),
    "hue":         (-180, 180, 0, 1),
    "gamma":       (10, 300, 100, 1),      # Gerçek değer = slider / 100
    "exposure":    (-300, 300, 0, 1),       # Gerçek değer = slider / 100
    "temperature": (-100, 100, 0, 1),
    "tint":        (-100, 100, 0, 1),
    "highlights":  (-100, 100, 0, 1),
    "shadows":     (-100, 100, 0, 1),
    "clarity":     (-100, 100, 0, 1),
    "vibrance":    (-100, 100, 0, 1),
    "sharpness":   (0, 100, 0, 1),
}

# Ayar parametrelerinin Türkçe etiketleri
ADJUSTMENT_LABELS = {
    "brightness":  "Parlaklık",
    "contrast":    "Kontrast",
    "saturation":  "Doygunluk",
    "hue":         "Ton (Hue)",
    "gamma":       "Gama",
    "exposure":    "Pozlama",
    "temperature": "Sıcaklık",
    "tint":        "Renk Tonu",
    "highlights":  "Açık Tonlar",
    "shadows":     "Koyu Tonlar",
    "clarity":     "Netlik",
    "vibrance":    "Canlılık",
    "sharpness":   "Keskinlik",
}

# ─── Filtre Tanımları ─────────────────────────────────────────────────
# Her filtre: (anahtar, Türkçe etiket)
FILTER_DEFINITIONS = [
    ("gaussian_blur",   "Gaussian Bulanıklık"),
    ("box_blur",        "Kutu Bulanıklık"),
    ("median_blur",     "Medyan Bulanıklık"),
    ("sharpen",         "Keskinleştirme"),
    ("unsharp_mask",    "Unsharp Mask"),
    ("edge_detect",     "Kenar Algılama"),
    ("emboss",          "Kabartma (Emboss)"),
    ("sepia",           "Sepya"),
    ("vintage",         "Vintage"),
    ("vignette",        "Vinyet"),
    ("hdr_effect",      "HDR Efekti"),
    ("pencil_sketch",   "Kalem Çizimi"),
    ("oil_painting",    "Yağlıboya"),
    ("pixelate",        "Pikselleştirme"),
    ("posterize",       "Posterize"),
    ("warm_filter",     "Sıcak Filtre"),
    ("cool_filter",     "Soğuk Filtre"),
    ("dramatic",        "Dramatik"),
]

# ─── Gürültü (Noise) Tanımları ────────────────────────────────────────
NOISE_TYPES = [
    ("gaussian",      "Gaussian Gürültü"),
    ("salt_pepper",   "Tuz & Biber"),
    ("poisson",       "Poisson Gürültü"),
    ("speckle",       "Speckle Gürültü"),
    ("uniform",       "Düzgün (Uniform)"),
    ("film_grain",    "Film Grain"),
    ("color_noise",   "Renk Gürültüsü"),
]

# ─── Yeniden Boyutlandırma İnterpolasyon Yöntemleri ───────────────────
INTERPOLATION_METHODS = [
    ("nearest",  "En Yakın Komşu (Nearest)"),
    ("bilinear", "Bilinear"),
    ("bicubic",  "Bicubic"),
    ("lanczos",  "Lanczos"),
    ("area",     "Alan (Area)"),
]

# ─── Renk Sabitleri ───────────────────────────────────────────────────
CANVAS_BACKGROUND = "#1a1a2e"
PANEL_BACKGROUND = "#16213e"
ACCENT_COLOR = "#0f3460"
HIGHLIGHT_COLOR = "#e94560"
TEXT_COLOR = "#eaeaea"
TEXT_SECONDARY = "#a0a0b0"
BORDER_COLOR = "#2a2a4a"
SLIDER_GROOVE = "#2a2a4a"
SLIDER_HANDLE = "#e94560"
BUTTON_HOVER = "#1a3a6a"
