"""
Ayarlama Paneli - Parlaklık, kontrast, doygunluk ve diğer temel
görüntü ayarlarını slider'lar ile kontrol eden panel.
Her slider gerçek zamanlı önizleme ile çalışır.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QPushButton, QLabel,
    QFrame, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal

from app.ui.components.labeled_slider import LabeledSlider
from app.utils.constants import ADJUSTMENT_RANGES, ADJUSTMENT_LABELS


class AdjustmentPanel(QWidget):
    """
    Görüntü ayarlama kontrolleri paneli.
    
    İçerdiği Ayarlar:
        - Işık: Parlaklık, Kontrast, Pozlama, Gama
        - Renk: Doygunluk, Ton, Canlılık, Sıcaklık, Renk Tonu
        - Detay: Açık Tonlar, Koyu Tonlar, Netlik, Keskinlik
    
    Sinyaller:
        adjustment_changed(str, int): (parametre_adı, değer) değiştiğinde
        reset_all_requested: Tümünü sıfırla istendiğinde
    """

    adjustment_changed = Signal(str, int)
    reset_all_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Slider referanslarını tutan sözlük
        self._sliders: dict[str, LabeledSlider] = {}
        self._setup_ui()

    def _setup_ui(self):
        """Panel arayüzünü oluşturur."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Kaydırılabilir alan ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(12, 8, 12, 8)
        self._content_layout.setSpacing(4)

        # ── Işık Ayarları Bölümü ──
        self._add_section_header("IŞIK")
        self._add_slider("brightness")
        self._add_slider("contrast")
        self._add_slider("exposure", suffix="", display_scale=0.01)
        self._add_slider("gamma", suffix="", display_scale=0.01)

        # ── Renk Ayarları Bölümü ──
        self._add_section_header("RENK")
        self._add_slider("saturation")
        self._add_slider("hue", suffix="°")
        self._add_slider("vibrance")
        self._add_slider("temperature")
        self._add_slider("tint")

        # ── Detay Ayarları Bölümü ──
        self._add_section_header("DETAY")
        self._add_slider("highlights")
        self._add_slider("shadows")
        self._add_slider("clarity")
        self._add_slider("sharpness")

        self._content_layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # ── Alt butonlar ──
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(12, 8, 12, 8)

        reset_btn = QPushButton("Tümünü Sıfırla")
        reset_btn.setObjectName("dangerButton")
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.clicked.connect(self._on_reset_all)
        btn_layout.addWidget(reset_btn)

        main_layout.addLayout(btn_layout)

    def _add_section_header(self, title: str):
        """Bölüm başlığı ekler."""
        label = QLabel(title)
        label.setObjectName("sectionTitle")
        self._content_layout.addWidget(label)

        # İnce ayırıcı çizgi
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #21262d; max-height: 1px;")
        self._content_layout.addWidget(line)

    def _add_slider(self, key: str, suffix: str = "", display_scale: float = 1.0):
        """
        Belirtilen parametre için slider oluşturur ve panele ekler.
        ADJUSTMENT_RANGES'dan aralık bilgilerini alır.
        """
        if key not in ADJUSTMENT_RANGES:
            return

        min_val, max_val, default_val, _ = ADJUSTMENT_RANGES[key]
        label = ADJUSTMENT_LABELS.get(key, key)

        slider = LabeledSlider(
            label=label,
            min_val=min_val,
            max_val=max_val,
            default_val=default_val,
            suffix=suffix,
            display_scale=display_scale,
        )
        slider.set_key(key)

        # Slider değiştiğinde ana pencereye bildir
        slider.value_changed.connect(
            lambda val, k=key: self.adjustment_changed.emit(k, val)
        )

        self._sliders[key] = slider
        self._content_layout.addWidget(slider)

    def _on_reset_all(self):
        """Tüm slider'ları varsayılan değerlere sıfırlar."""
        for key, slider in self._sliders.items():
            slider.reset_value()
        self.reset_all_requested.emit()

    # ─── Public API ───────────────────────────────────────────────

    def get_all_values(self) -> dict[str, int]:
        """Tüm slider değerlerini sözlük olarak döndürür."""
        return {key: slider.value() for key, slider in self._sliders.items()}

    def set_all_values(self, values: dict[str, int]):
        """Tüm slider'ları verilen değerlere ayarlar."""
        for key, value in values.items():
            if key in self._sliders:
                self._sliders[key].set_value(value)

    def reset_all(self):
        """Tüm slider'ları programatik olarak sıfırlar."""
        for slider in self._sliders.values():
            slider.reset_value()
