"""
Etiketli Slider Bileşeni - Parametre adı, slider ve değer göstergesi.
Tüm düzenleme panellerinde kullanılan temel kontrol elemanı.
Sıfırlama butonu ile hızlı varsayılan değere dönüş sağlanır.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QSlider, QLabel, QPushButton
)
from PySide6.QtCore import Qt, Signal


class LabeledSlider(QWidget):
    """
    Etiket + Slider + Değer göstergesi + Sıfırla butonu içeren bileşik widget.
    
    Sinyaller:
        value_changed(int): Slider değeri değiştiğinde tetiklenir
    """

    value_changed = Signal(int)

    def __init__(
        self,
        label: str,
        min_val: int = 0,
        max_val: int = 100,
        default_val: int = 0,
        suffix: str = "",
        display_scale: float = 1.0,
        parent=None
    ):
        """
        Parametreler:
            label: Gösterilecek etiket metni
            min_val: Slider minimum değeri
            max_val: Slider maksimum değeri
            default_val: Varsayılan (başlangıç) değer
            suffix: Değer sonrasına eklenecek metin (ör. '%', '°')
            display_scale: Gösterim için çarpan (ör. gamma 100→1.0)
        """
        super().__init__(parent)
        self._default_val = default_val
        self._suffix = suffix
        self._display_scale = display_scale
        self._key = ""  # Parametre anahtarı (opsiyonel)

        self._setup_ui(label, min_val, max_val, default_val)

    def _setup_ui(self, label: str, min_val: int, max_val: int, default_val: int):
        """UI bileşenlerini oluşturur ve yerleştirir."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(2)

        # ── Üst satır: Etiket + Değer + Sıfırla ──
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        # Parametre etiketi
        self._label = QLabel(label)
        self._label.setStyleSheet("font-size: 12px; color: #c9d1d9;")
        top_row.addWidget(self._label)

        top_row.addStretch()

        # Değer göstergesi
        self._value_label = QLabel(self._format_value(default_val))
        self._value_label.setObjectName("valueLabel")
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        top_row.addWidget(self._value_label)

        # Sıfırlama butonu
        self._reset_btn = QPushButton("⟲")
        self._reset_btn.setObjectName("resetButton")
        self._reset_btn.setToolTip("Varsayılana sıfırla")
        self._reset_btn.setFixedSize(20, 20)
        self._reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._reset_btn.clicked.connect(self.reset_value)
        # Varsayılan değerdeyse gizle
        self._reset_btn.setVisible(default_val != default_val)  # Başlangıçta gizli
        top_row.addWidget(self._reset_btn)

        layout.addLayout(top_row)

        # ── Alt satır: Slider ──
        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setMinimum(min_val)
        self._slider.setMaximum(max_val)
        self._slider.setValue(default_val)
        self._slider.setFixedHeight(22)

        # Slider değeri değiştiğinde güncelle
        self._slider.valueChanged.connect(self._on_value_changed)

        layout.addWidget(self._slider)

    def _on_value_changed(self, value: int):
        """Slider değeri değiştiğinde çağrılır."""
        self._value_label.setText(self._format_value(value))
        # Sıfırla butonunu göster/gizle
        self._reset_btn.setVisible(value != self._default_val)
        # Dışarıya sinyal gönder
        self.value_changed.emit(value)

    def _format_value(self, value: int) -> str:
        """Değeri gösterim formatına dönüştürür."""
        if self._display_scale != 1.0:
            display = value * self._display_scale
            return f"{display:.2f}{self._suffix}"
        return f"{value}{self._suffix}"

    def reset_value(self):
        """Slider'ı varsayılan değere sıfırlar."""
        self._slider.setValue(self._default_val)

    # ─── Public API ───────────────────────────────────────────────

    def value(self) -> int:
        """Mevcut slider değerini döndürür."""
        return self._slider.value()

    def set_value(self, value: int):
        """Slider değerini programatik olarak ayarlar."""
        self._slider.setValue(value)

    def set_key(self, key: str):
        """Parametre anahtarını ayarlar (processor ile eşleştirme için)."""
        self._key = key

    def key(self) -> str:
        """Parametre anahtarını döndürür."""
        return self._key

    @property
    def default_value(self) -> int:
        return self._default_val

    def is_at_default(self) -> bool:
        """Slider varsayılan değerde mi kontrolü."""
        return self._slider.value() == self._default_val
