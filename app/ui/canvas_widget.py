"""
Görüntü Tuvali (Canvas) - Düzenlenen görüntünün gösterildiği ana alan.
Yakınlaştırma (zoom), kaydırma (pan) ve sığdırma (fit) desteklenir.
Mouse tekerleği ile zoom, sürükleme ile pan yapılır.
"""

import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt, QPoint, Signal, QSize
from PySide6.QtGui import QPixmap, QPainter, QWheelEvent, QMouseEvent, QPaintEvent, QColor

from app.utils.image_utils import numpy_to_qpixmap


class CanvasWidget(QWidget):
    """
    Görüntü görüntüleme tuvali.
    
    Özellikler:
        - Fare tekerleği ile yakınlaştırma/uzaklaştırma
        - Orta tuş veya sol tuş sürükleme ile kaydırma
        - Pencereye sığdırma (Fit to Window)
        - Arka plan ızgara/dama deseni (isteğe bağlı)
    
    Sinyaller:
        zoom_changed(float): Yakınlaştırma seviyesi değiştiğinde
    """

    zoom_changed = Signal(float)

    # Yakınlaştırma sınırları
    MIN_ZOOM = 0.05
    MAX_ZOOM = 20.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("canvasContainer")
        self.setMinimumSize(400, 300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Görüntü verisi
        self._pixmap: QPixmap = QPixmap()
        self._zoom: float = 1.0
        self._offset = QPoint(0, 0)

        # Sürükleme durumu
        self._dragging = False
        self._drag_start = QPoint()

        # Boş tuval etiketi
        self._empty_label = QLabel("Görüntü yüklemek için Dosya → Aç\nveya Ctrl+O kullanın", self)
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet(
            "color: #484f58; font-size: 16px; font-weight: 300;"
        )

    def set_image(self, image: np.ndarray) -> None:
        """Görüntülenen görüntüyü günceller (NumPy dizisinden)."""
        if image is None:
            self._pixmap = QPixmap()
            self._empty_label.setVisible(True)
        else:
            self._pixmap = numpy_to_qpixmap(image)
            self._empty_label.setVisible(False)
        self.update()

    def set_pixmap(self, pixmap: QPixmap) -> None:
        """Doğrudan QPixmap ile görüntü ayarlar."""
        self._pixmap = pixmap
        self._empty_label.setVisible(pixmap.isNull())
        self.update()

    def fit_to_window(self) -> None:
        """Görüntüyü pencereye sığdırır."""
        if self._pixmap.isNull():
            return

        # Kullanılabilir alan
        canvas_w = self.width() - 40  # Kenar boşlukları
        canvas_h = self.height() - 40
        img_w = self._pixmap.width()
        img_h = self._pixmap.height()

        if img_w <= 0 or img_h <= 0:
            return

        # Ölçek faktörü (en-boy oranını koru)
        scale_x = canvas_w / img_w
        scale_y = canvas_h / img_h
        self._zoom = min(scale_x, scale_y, 1.0)  # En fazla %100

        # Merkeze hizala
        self._center_image()
        self.zoom_changed.emit(self._zoom)
        self.update()

    def zoom_to_fit(self) -> None:
        """Pencereye sığdır (1:1'den büyük de olabilir)."""
        if self._pixmap.isNull():
            return

        canvas_w = self.width() - 40
        canvas_h = self.height() - 40
        img_w = self._pixmap.width()
        img_h = self._pixmap.height()

        if img_w <= 0 or img_h <= 0:
            return

        scale_x = canvas_w / img_w
        scale_y = canvas_h / img_h
        self._zoom = min(scale_x, scale_y)

        self._center_image()
        self.zoom_changed.emit(self._zoom)
        self.update()

    def zoom_actual(self) -> None:
        """Gerçek boyut (1:1 zoom)."""
        self._zoom = 1.0
        self._center_image()
        self.zoom_changed.emit(self._zoom)
        self.update()

    def _center_image(self) -> None:
        """Görüntüyü tuvalin ortasına hizalar."""
        if self._pixmap.isNull():
            return

        img_w = int(self._pixmap.width() * self._zoom)
        img_h = int(self._pixmap.height() * self._zoom)

        x = (self.width() - img_w) // 2
        y = (self.height() - img_h) // 2
        self._offset = QPoint(x, y)

    # ─── Çizim ────────────────────────────────────────────────────────

    def paintEvent(self, event: QPaintEvent) -> None:
        """Tuval çizim olayı. Arka plan ve görüntüyü çizer."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Arka plan
        painter.fillRect(self.rect(), QColor("#010409"))

        if self._pixmap.isNull():
            # Boş tuval - etiketi ortala
            self._empty_label.setGeometry(self.rect())
            painter.end()
            return

        self._empty_label.setVisible(False)

        # Görüntüyü çiz
        img_w = int(self._pixmap.width() * self._zoom)
        img_h = int(self._pixmap.height() * self._zoom)

        target_rect = self._pixmap.rect()
        target_rect.setWidth(img_w)
        target_rect.setHeight(img_h)
        target_rect.moveTopLeft(self._offset)

        painter.drawPixmap(target_rect, self._pixmap)

        # Görüntü kenarlığı (ince)
        painter.setPen(QColor("#30363d"))
        painter.drawRect(target_rect.adjusted(0, 0, -1, -1))

        painter.end()

    # ─── Fare Olayları ────────────────────────────────────────────────

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Fare tekerleği ile yakınlaştırma/uzaklaştırma."""
        if self._pixmap.isNull():
            return

        # Yakınlaştırma noktası (fare konumu)
        mouse_pos = event.position().toPoint()

        # Yakınlaştırma faktörü
        delta = event.angleDelta().y()
        if delta > 0:
            factor = 1.15
        elif delta < 0:
            factor = 1 / 1.15
        else:
            return

        new_zoom = self._zoom * factor
        new_zoom = max(self.MIN_ZOOM, min(self.MAX_ZOOM, new_zoom))

        if new_zoom == self._zoom:
            return

        # Fare noktasını merkez alarak zoom (pürüzsüz yakınlaştırma)
        old_zoom = self._zoom
        self._zoom = new_zoom

        # Offset'i fare konumuna göre ayarla
        scale_change = new_zoom / old_zoom
        new_offset_x = mouse_pos.x() - (mouse_pos.x() - self._offset.x()) * scale_change
        new_offset_y = mouse_pos.y() - (mouse_pos.y() - self._offset.y()) * scale_change
        self._offset = QPoint(int(new_offset_x), int(new_offset_y))

        self.zoom_changed.emit(self._zoom)
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Fare butonu basıldığında sürükleme başlatır."""
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.MiddleButton):
            self._dragging = True
            self._drag_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Fare hareket ettirildiğinde görüntüyü kaydırır."""
        if self._dragging:
            delta = event.pos() - self._drag_start
            self._offset += delta
            self._drag_start = event.pos()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Fare butonu bırakıldığında sürüklemeyi sonlandırır."""
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.MiddleButton):
            self._dragging = False
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Çift tıklamada pencereye sığdır."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.fit_to_window()

    def resizeEvent(self, event):
        """Pencere boyutu değiştiğinde görüntüyü yeniden ortala."""
        super().resizeEvent(event)
        if not self._pixmap.isNull():
            # Mevcut zoom'u koru ama merkeze hizala
            self._center_image()
            self.update()

    # ─── Özellikler ───────────────────────────────────────────────────

    @property
    def zoom(self) -> float:
        return self._zoom

    @property
    def has_image(self) -> bool:
        return not self._pixmap.isNull()
