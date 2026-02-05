"""
Dönüşüm Paneli - Yeniden boyutlandırma, döndürme, çevirme ve kırpma kontrolleri.
Boyut değişiklikleri için en-boy oranı kilitleme ve çeşitli
interpolasyon yöntemleri desteklenir.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QPushButton,
    QLabel, QSpinBox, QComboBox, QCheckBox, QFrame, QDoubleSpinBox
)
from PySide6.QtCore import Qt, Signal

from app.utils.constants import INTERPOLATION_METHODS


class TransformPanel(QWidget):
    """
    Görüntü dönüşüm kontrolleri paneli.
    
    Özellikler:
        - Genişlik/Yükseklik ile yeniden boyutlandırma
        - En-boy oranı kilitleme
        - İnterpolasyon yöntemi seçimi
        - 90° döndürme (saat yönü/ters)
        - Yatay/Dikey çevirme
        - Serbest açı döndürme
    
    Sinyaller:
        resize_requested(int, int, str): (genişlik, yükseklik, yöntem)
        rotate_requested(float): açı
        flip_requested(bool): True=yatay, False=dikey
    """

    resize_requested = Signal(int, int, str)
    rotate_requested = Signal(float)
    flip_requested = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._aspect_ratio = 1.0  # Genişlik / Yükseklik
        self._lock_aspect = True
        self._updating_size = False  # Döngüsel güncellemeyi önle
        self._setup_ui()

    def _setup_ui(self):
        """Panel arayüzünü oluşturur."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(12, 8, 12, 8)
        content_layout.setSpacing(8)

        # ═══════════════════════════════════════════════════════════
        # ── YENİDEN BOYUTLANDIRMA ──
        # ═══════════════════════════════════════════════════════════
        self._add_section_header(content_layout, "YENİDEN BOYUTLANDIRMA")

        # Mevcut boyut göstergesi
        self._current_size_label = QLabel("Mevcut: - × -")
        self._current_size_label.setStyleSheet("font-size: 11px; color: #8b949e;")
        content_layout.addWidget(self._current_size_label)

        # Genişlik
        w_layout = QHBoxLayout()
        w_label = QLabel("Genişlik:")
        w_label.setStyleSheet("font-size: 12px; min-width: 70px;")
        w_layout.addWidget(w_label)

        self._width_spin = QSpinBox()
        self._width_spin.setRange(1, 20000)
        self._width_spin.setValue(1920)
        self._width_spin.setSuffix(" px")
        self._width_spin.valueChanged.connect(self._on_width_changed)
        w_layout.addWidget(self._width_spin)
        content_layout.addLayout(w_layout)

        # En-boy oranı kilidi
        lock_layout = QHBoxLayout()
        lock_layout.addStretch()
        self._lock_checkbox = QCheckBox("En-Boy Oranını Kilitle")
        self._lock_checkbox.setChecked(True)
        self._lock_checkbox.toggled.connect(self._on_lock_toggled)
        lock_layout.addWidget(self._lock_checkbox)
        lock_layout.addStretch()
        content_layout.addLayout(lock_layout)

        # Yükseklik
        h_layout = QHBoxLayout()
        h_label = QLabel("Yükseklik:")
        h_label.setStyleSheet("font-size: 12px; min-width: 70px;")
        h_layout.addWidget(h_label)

        self._height_spin = QSpinBox()
        self._height_spin.setRange(1, 20000)
        self._height_spin.setValue(1080)
        self._height_spin.setSuffix(" px")
        self._height_spin.valueChanged.connect(self._on_height_changed)
        h_layout.addWidget(self._height_spin)
        content_layout.addLayout(h_layout)

        # İnterpolasyon yöntemi
        interp_label = QLabel("İnterpolasyon Yöntemi:")
        interp_label.setStyleSheet("font-size: 12px; color: #c9d1d9; padding-top: 4px;")
        content_layout.addWidget(interp_label)

        self._interp_combo = QComboBox()
        for key, label in INTERPOLATION_METHODS:
            self._interp_combo.addItem(label, key)
        self._interp_combo.setCurrentIndex(3)  # Varsayılan: Lanczos
        content_layout.addWidget(self._interp_combo)

        # Boyutlandırma uygula butonu
        resize_btn = QPushButton("Boyutlandırmayı Uygula")
        resize_btn.setObjectName("primaryButton")
        resize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        resize_btn.clicked.connect(self._on_resize_apply)
        content_layout.addWidget(resize_btn)

        # Hızlı boyutlandırma butonları
        quick_layout = QHBoxLayout()
        for label_text, scale in [("25%", 25), ("50%", 50), ("75%", 75), ("150%", 150), ("200%", 200)]:
            btn = QPushButton(label_text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(28)
            btn.clicked.connect(lambda checked, s=scale: self._on_quick_resize(s))
            quick_layout.addWidget(btn)
        content_layout.addLayout(quick_layout)

        # ═══════════════════════════════════════════════════════════
        # ── DÖNDÜRME ──
        # ═══════════════════════════════════════════════════════════
        self._add_section_header(content_layout, "DÖNDÜRME")

        # Hızlı döndürme butonları
        rotate_btn_layout = QHBoxLayout()

        rotate_ccw_btn = QPushButton("↺ 90° Sol")
        rotate_ccw_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rotate_ccw_btn.clicked.connect(lambda: self.rotate_requested.emit(90))
        rotate_btn_layout.addWidget(rotate_ccw_btn)

        rotate_cw_btn = QPushButton("↻ 90° Sağ")
        rotate_cw_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rotate_cw_btn.clicked.connect(lambda: self.rotate_requested.emit(-90))
        rotate_btn_layout.addWidget(rotate_cw_btn)

        content_layout.addLayout(rotate_btn_layout)

        # Serbest açı döndürme
        angle_layout = QHBoxLayout()
        angle_label = QLabel("Açı:")
        angle_label.setStyleSheet("font-size: 12px; min-width: 50px;")
        angle_layout.addWidget(angle_label)

        self._angle_spin = QDoubleSpinBox()
        self._angle_spin.setRange(-360, 360)
        self._angle_spin.setValue(0)
        self._angle_spin.setSuffix("°")
        self._angle_spin.setDecimals(1)
        self._angle_spin.setSingleStep(0.5)
        angle_layout.addWidget(self._angle_spin)

        rotate_apply_btn = QPushButton("Döndür")
        rotate_apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rotate_apply_btn.clicked.connect(
            lambda: self.rotate_requested.emit(self._angle_spin.value())
        )
        angle_layout.addWidget(rotate_apply_btn)
        content_layout.addLayout(angle_layout)

        # ═══════════════════════════════════════════════════════════
        # ── ÇEVİRME ──
        # ═══════════════════════════════════════════════════════════
        self._add_section_header(content_layout, "ÇEVİRME")

        flip_layout = QHBoxLayout()

        flip_h_btn = QPushButton("⟷ Yatay Çevir")
        flip_h_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        flip_h_btn.clicked.connect(lambda: self.flip_requested.emit(True))
        flip_layout.addWidget(flip_h_btn)

        flip_v_btn = QPushButton("⟷ Dikey Çevir")
        flip_v_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        flip_v_btn.clicked.connect(lambda: self.flip_requested.emit(False))
        flip_layout.addWidget(flip_v_btn)

        content_layout.addLayout(flip_layout)

        content_layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _add_section_header(self, layout: QVBoxLayout, title: str):
        """Bölüm başlığı ekler."""
        label = QLabel(title)
        label.setObjectName("sectionTitle")
        layout.addWidget(label)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #21262d; max-height: 1px;")
        layout.addWidget(line)

    # ─── Olay Yöneticileri ────────────────────────────────────────────

    def _on_width_changed(self, value: int):
        """Genişlik değiştiğinde yüksekliği orantılı günceller."""
        if self._updating_size or not self._lock_aspect:
            return
        self._updating_size = True
        new_height = max(1, int(value / self._aspect_ratio))
        self._height_spin.setValue(new_height)
        self._updating_size = False

    def _on_height_changed(self, value: int):
        """Yükseklik değiştiğinde genişliği orantılı günceller."""
        if self._updating_size or not self._lock_aspect:
            return
        self._updating_size = True
        new_width = max(1, int(value * self._aspect_ratio))
        self._width_spin.setValue(new_width)
        self._updating_size = False

    def _on_lock_toggled(self, checked: bool):
        """En-boy oranı kilidi değiştiğinde."""
        self._lock_aspect = checked
        if checked:
            # Mevcut değerlerden oranı güncelle
            w = self._width_spin.value()
            h = self._height_spin.value()
            if h > 0:
                self._aspect_ratio = w / h

    def _on_resize_apply(self):
        """Boyutlandırma uygula butonuna basıldığında."""
        width = self._width_spin.value()
        height = self._height_spin.value()
        method = self._interp_combo.currentData()
        self.resize_requested.emit(width, height, method)

    def _on_quick_resize(self, percentage: int):
        """Hızlı yüzde bazlı boyutlandırma."""
        current_w = self._width_spin.value()
        current_h = self._height_spin.value()
        new_w = max(1, int(current_w * percentage / 100))
        new_h = max(1, int(current_h * percentage / 100))

        self._updating_size = True
        self._width_spin.setValue(new_w)
        self._height_spin.setValue(new_h)
        self._updating_size = False

    # ─── Public API ───────────────────────────────────────────────

    def update_image_size(self, width: int, height: int):
        """Mevcut görüntü boyutunu günceller."""
        self._updating_size = True
        self._width_spin.setValue(width)
        self._height_spin.setValue(height)
        self._updating_size = False

        if height > 0:
            self._aspect_ratio = width / height

        self._current_size_label.setText(f"Mevcut: {width} × {height} px")
