"""
Dışa Aktarma Diyalogu - Görüntüyü kaydetmeden önce kalite ve
format ayarlarını yapma imkanı sunar.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QPushButton, QComboBox
)
from PySide6.QtCore import Qt


class ExportDialog(QDialog):
    """
    Dışa aktarma kalite ve format ayarları diyalogu.
    JPEG kalitesi, PNG sıkıştırma seviyesi gibi parametreleri kontrol eder.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dışa Aktar")
        self.setFixedSize(400, 250)
        self._quality = 95
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Başlık
        title = QLabel("Dışa Aktarma Ayarları")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        # Format seçimi
        format_layout = QHBoxLayout()
        format_label = QLabel("Format:")
        format_label.setMinimumWidth(80)
        format_layout.addWidget(format_label)

        self._format_combo = QComboBox()
        self._format_combo.addItems(["PNG", "JPEG", "WebP", "BMP", "TIFF"])
        self._format_combo.currentTextChanged.connect(self._on_format_changed)
        format_layout.addWidget(self._format_combo)
        layout.addLayout(format_layout)

        # Kalite slider'ı
        quality_layout = QHBoxLayout()
        quality_label = QLabel("Kalite:")
        quality_label.setMinimumWidth(80)
        quality_layout.addWidget(quality_label)

        self._quality_slider = QSlider(Qt.Orientation.Horizontal)
        self._quality_slider.setRange(1, 100)
        self._quality_slider.setValue(95)
        self._quality_slider.valueChanged.connect(self._on_quality_changed)
        quality_layout.addWidget(self._quality_slider)

        self._quality_value = QLabel("95%")
        self._quality_value.setObjectName("valueLabel")
        self._quality_value.setMinimumWidth(40)
        quality_layout.addWidget(self._quality_value)
        layout.addLayout(quality_layout)

        # Bilgi metni
        self._info_label = QLabel("PNG: Kayıpsız sıkıştırma (kalite = sıkıştırma seviyesi)")
        self._info_label.setStyleSheet("font-size: 11px; color: #8b949e;")
        self._info_label.setWordWrap(True)
        layout.addWidget(self._info_label)

        layout.addStretch()

        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        export_btn = QPushButton("Dışa Aktar")
        export_btn.setObjectName("primaryButton")
        export_btn.clicked.connect(self.accept)
        btn_layout.addWidget(export_btn)
        layout.addLayout(btn_layout)

    def _on_quality_changed(self, value: int):
        self._quality = value
        self._quality_value.setText(f"{value}%")

    def _on_format_changed(self, format_name: str):
        info_map = {
            "PNG": "PNG: Kayıpsız sıkıştırma (kalite = sıkıştırma seviyesi)",
            "JPEG": "JPEG: Kayıplı sıkıştırma (yüksek kalite = büyük dosya)",
            "WebP": "WebP: Modern format, iyi sıkıştırma oranı",
            "BMP": "BMP: Sıkıştırmasız format (kalite ayarı etkisizdir)",
            "TIFF": "TIFF: Profesyonel format, büyük dosya boyutu",
        }
        self._info_label.setText(info_map.get(format_name, ""))

    @property
    def quality(self) -> int:
        return self._quality

    @property
    def format_extension(self) -> str:
        fmt = self._format_combo.currentText().lower()
        return fmt if fmt != "jpeg" else "jpg"
