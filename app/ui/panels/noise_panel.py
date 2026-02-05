"""
Gürültü (Noise) Paneli - Detaylı gürültü efekti kontrolleri.
Farklı gürültü türleri, yoğunluk, monokrom/renkli seçimi ve
ölçek parametresi ile profesyonel gürültü ekleme imkanı sağlar.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QPushButton, QLabel,
    QComboBox, QCheckBox, QFrame, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal

from app.ui.components.labeled_slider import LabeledSlider
from app.utils.constants import NOISE_TYPES


class NoisePanel(QWidget):
    """
    Gürültü efekti kontrol paneli.
    
    Kontroller:
        - Gürültü türü seçimi (ComboBox)
        - Yoğunluk slider'ı (0-100)
        - Monokrom/Renkli toggle (CheckBox)
        - Ölçek slider'ı (tanecik boyutu)
    
    Sinyaller:
        noise_changed(dict): Tüm gürültü parametreleri değiştiğinde
        reset_requested: Sıfırlama istendiğinde
    """

    noise_changed = Signal(dict)
    reset_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
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
        content_layout.setSpacing(8)

        # ── Bölüm başlığı ──
        header = QLabel("GÜRÜLTÜ EFEKTİ")
        header.setObjectName("sectionTitle")
        content_layout.addWidget(header)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #21262d; max-height: 1px;")
        content_layout.addWidget(line)

        # ── Gürültü Türü Seçimi ──
        type_label = QLabel("Gürültü Türü")
        type_label.setStyleSheet("font-size: 12px; color: #c9d1d9; padding-top: 4px;")
        content_layout.addWidget(type_label)

        self._type_combo = QComboBox()
        for key, label in NOISE_TYPES:
            self._type_combo.addItem(label, key)
        self._type_combo.currentIndexChanged.connect(self._on_param_changed)
        content_layout.addWidget(self._type_combo)

        # ── Yoğunluk Slider'ı ──
        self._intensity_slider = LabeledSlider(
            label="Yoğunluk",
            min_val=0,
            max_val=100,
            default_val=0,
            suffix="%",
        )
        self._intensity_slider.value_changed.connect(self._on_param_changed)
        content_layout.addWidget(self._intensity_slider)

        # ── Ölçek Slider'ı ──
        self._scale_slider = LabeledSlider(
            label="Tanecik Boyutu",
            min_val=10,
            max_val=100,
            default_val=10,
            suffix="",
            display_scale=0.1,
        )
        self._scale_slider.value_changed.connect(self._on_param_changed)
        content_layout.addWidget(self._scale_slider)

        # ── Monokrom Seçeneği ──
        self._mono_checkbox = QCheckBox("Monokrom (Gri Tonlamalı)")
        self._mono_checkbox.setChecked(True)
        self._mono_checkbox.toggled.connect(self._on_param_changed)
        content_layout.addWidget(self._mono_checkbox)

        # ── Bilgi Metni ──
        info_frame = QFrame()
        info_frame.setStyleSheet(
            "background-color: #161b22; border: 1px solid #21262d; "
            "border-radius: 6px; padding: 8px;"
        )
        info_layout = QVBoxLayout(info_frame)

        info_title = QLabel("Gürültü Türleri Hakkında")
        info_title.setStyleSheet("font-weight: 600; font-size: 11px; color: #58a6ff;")
        info_layout.addWidget(info_title)

        info_texts = [
            "• Gaussian: Doğal sensör gürültüsü",
            "• Tuz & Biber: Rastgele siyah-beyaz noktalar",
            "• Poisson: Düşük ışık simülasyonu",
            "• Speckle: Radar/ultrason gürültüsü",
            "• Uniform: Eşit dağılımlı gürültü",
            "• Film Grain: Analog film tanecikleri",
            "• Renk Gürültüsü: Kanal bazlı gürültü",
        ]
        for text in info_texts:
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 11px; color: #8b949e; padding: 1px 0;")
            lbl.setWordWrap(True)
            info_layout.addWidget(lbl)

        content_layout.addWidget(info_frame)
        content_layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # ── Alt butonlar ──
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(12, 8, 12, 8)

        reset_btn = QPushButton("Gürültüyü Sıfırla")
        reset_btn.setObjectName("dangerButton")
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.clicked.connect(self._on_reset)
        btn_layout.addWidget(reset_btn)

        main_layout.addLayout(btn_layout)

    def _on_param_changed(self, *args):
        """Herhangi bir parametre değiştiğinde sinyal gönderir."""
        params = self.get_params()
        self.noise_changed.emit(params)

    def _on_reset(self):
        """Tüm gürültü parametrelerini sıfırlar."""
        self._type_combo.setCurrentIndex(0)
        self._intensity_slider.reset_value()
        self._scale_slider.reset_value()
        self._mono_checkbox.setChecked(True)
        self.reset_requested.emit()

    # ─── Public API ───────────────────────────────────────────────

    def get_params(self) -> dict:
        """Mevcut tüm gürültü parametrelerini sözlük olarak döndürür."""
        return {
            "type": self._type_combo.currentData(),
            "intensity": self._intensity_slider.value(),
            "monochrome": self._mono_checkbox.isChecked(),
            "scale": self._scale_slider.value() / 10.0,
        }

    def reset_all(self):
        """Programatik sıfırlama."""
        self._on_reset()
