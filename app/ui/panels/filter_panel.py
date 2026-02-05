"""
Filtre Paneli - Görüntü filtrelerini slider ile kontrol eden panel.
Her filtre bağımsız yoğunluk kontrolüne sahiptir.
Filtreler aynı anda birden fazla aktif olabilir (zincirleme).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QPushButton,
    QLabel, QFrame, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal

from app.ui.components.labeled_slider import LabeledSlider
from app.utils.constants import FILTER_DEFINITIONS


class FilterPanel(QWidget):
    """
    Filtre kontrolleri paneli.
    Her filtre 0-100 arası yoğunluk slider'ı ile kontrol edilir.
    0 = Filtre kapalı, 100 = Tam yoğunluk.
    
    Sinyaller:
        filter_changed(str, int): (filtre_adı, yoğunluk) değiştiğinde
        reset_all_requested: Tümünü sıfırla istendiğinde
    """

    filter_changed = Signal(str, int)
    reset_all_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
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
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(12, 8, 12, 8)
        content_layout.setSpacing(4)

        # ── Bulanıklık ve Keskinleştirme ──
        self._add_section_header(content_layout, "BULANIKLIK & KESKİNLEŞTİRME")
        for key, label in FILTER_DEFINITIONS[:5]:
            self._add_filter_slider(content_layout, key, label)

        # ── Sanatsal Filtreler ──
        self._add_section_header(content_layout, "SANATSAL")
        for key, label in FILTER_DEFINITIONS[5:13]:
            self._add_filter_slider(content_layout, key, label)

        # ── Renk ve Stil Filtreleri ──
        self._add_section_header(content_layout, "RENK & STİL")
        for key, label in FILTER_DEFINITIONS[13:]:
            self._add_filter_slider(content_layout, key, label)

        content_layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # ── Alt butonlar ──
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(12, 8, 12, 8)

        reset_btn = QPushButton("Tüm Filtreleri Sıfırla")
        reset_btn.setObjectName("dangerButton")
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.clicked.connect(self._on_reset_all)
        btn_layout.addWidget(reset_btn)

        main_layout.addLayout(btn_layout)

    def _add_section_header(self, layout: QVBoxLayout, title: str):
        """Bölüm başlığı ekler."""
        label = QLabel(title)
        label.setObjectName("sectionTitle")
        layout.addWidget(label)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #21262d; max-height: 1px;")
        layout.addWidget(line)

    def _add_filter_slider(self, layout: QVBoxLayout, key: str, label: str):
        """Bir filtre için yoğunluk slider'ı ekler."""
        slider = LabeledSlider(
            label=label,
            min_val=0,
            max_val=100,
            default_val=0,
            suffix="%",
        )
        slider.set_key(key)

        # Slider değiştiğinde sinyal gönder
        slider.value_changed.connect(
            lambda val, k=key: self.filter_changed.emit(k, val)
        )

        self._sliders[key] = slider
        layout.addWidget(slider)

    def _on_reset_all(self):
        """Tüm filtre slider'larını sıfırlar."""
        for slider in self._sliders.values():
            slider.reset_value()
        self.reset_all_requested.emit()

    # ─── Public API ───────────────────────────────────────────────

    def get_all_values(self) -> dict[str, int]:
        """Tüm filtre yoğunluk değerlerini döndürür."""
        return {key: slider.value() for key, slider in self._sliders.items()}

    def get_active_filters(self) -> dict[str, int]:
        """Yalnızca aktif (>0) filtreleri döndürür."""
        return {
            key: slider.value()
            for key, slider in self._sliders.items()
            if slider.value() > 0
        }

    def reset_all(self):
        """Tüm slider'ları programatik olarak sıfırlar."""
        for slider in self._sliders.values():
            slider.reset_value()
