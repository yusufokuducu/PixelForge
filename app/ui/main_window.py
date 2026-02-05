"""
Ana Uygulama Penceresi - Tüm UI bileşenlerini ve iş mantığını birleştiren
merkezi modül. Menü, araç çubuğu, tuval, paneller ve durum çubuğu burada
oluşturulur ve bağlanır.
"""

import os
import numpy as np
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTabWidget,
    QToolBar, QStatusBar, QFileDialog, QMessageBox, QSplitter,
    QLabel, QApplication, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QSize, Slot
from PySide6.QtGui import QAction, QKeySequence, QIcon

from app.core.image_processor import ImageProcessor
from app.workers.processing_worker import ProcessingThread
from app.ui.canvas_widget import CanvasWidget
from app.ui.panels.adjustment_panel import AdjustmentPanel
from app.ui.panels.filter_panel import FilterPanel
from app.ui.panels.noise_panel import NoisePanel
from app.ui.panels.transform_panel import TransformPanel
from app.ui.dialogs.resize_dialog import ExportDialog
from app.utils.constants import (
    APP_NAME, APP_VERSION, SUPPORTED_IMAGE_FORMATS,
    SAVE_IMAGE_FORMATS, SLIDER_DEBOUNCE_MS
)
from app.utils.image_utils import get_image_info


class MainWindow(QMainWindow):
    """
    PixelForge ana penceresi.
    
    Sorumluluklar:
        - Menü ve araç çubuğu oluşturma
        - Panel ve tuval yerleşimi
        - ImageProcessor ve Worker yönetimi
        - Sinyal-slot bağlantıları
        - Klavye kısayolları
    """

    def __init__(self):
        super().__init__()

        # ── Merkezi bileşenler ──
        self._processor = ImageProcessor()
        self._processing_thread = ProcessingThread()
        self._processing_thread.worker.set_processor(self._processor)

        # Debounce zamanlayıcısı (slider değişikliklerini geciktir)
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(SLIDER_DEBOUNCE_MS)
        self._debounce_timer.timeout.connect(self._request_processing)

        # İşleme durum takibi
        self._is_processing = False

        self._setup_window()
        self._create_actions()
        self._create_menus()
        self._create_toolbar()
        self._create_central_ui()
        self._create_status_bar()
        self._connect_signals()

        # Worker thread'i başlat
        self._processing_thread.start()

    def _setup_window(self):
        """Pencere özelliklerini ayarlar."""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1200, 750)
        self.resize(1600, 900)

        # Pencereyi ekranın ortasına konumla
        screen = QApplication.primaryScreen()
        if screen:
            screen_rect = screen.availableGeometry()
            x = (screen_rect.width() - self.width()) // 2
            y = (screen_rect.height() - self.height()) // 2
            self.move(x, y)

    # ═══════════════════════════════════════════════════════════════
    # ── EYLEMLER (Actions) ──
    # ═══════════════════════════════════════════════════════════════

    def _create_actions(self):
        """Menü ve araç çubuğu eylemlerini oluşturur."""

        # ── Dosya Eylemleri ──
        self._open_action = QAction("Aç...", self)
        self._open_action.setShortcut(QKeySequence.StandardKey.Open)
        self._open_action.setToolTip("Görüntü dosyası aç (Ctrl+O)")
        self._open_action.triggered.connect(self._on_open)

        self._save_action = QAction("Kaydet", self)
        self._save_action.setShortcut(QKeySequence.StandardKey.Save)
        self._save_action.setToolTip("Görüntüyü kaydet (Ctrl+S)")
        self._save_action.triggered.connect(self._on_save)
        self._save_action.setEnabled(False)

        self._save_as_action = QAction("Farklı Kaydet...", self)
        self._save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self._save_as_action.triggered.connect(self._on_save_as)
        self._save_as_action.setEnabled(False)

        self._export_action = QAction("Dışa Aktar...", self)
        self._export_action.setShortcut(QKeySequence("Ctrl+E"))
        self._export_action.triggered.connect(self._on_export)
        self._export_action.setEnabled(False)

        self._quit_action = QAction("Çıkış", self)
        self._quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self._quit_action.triggered.connect(self.close)

        # ── Düzenleme Eylemleri ──
        self._undo_action = QAction("Geri Al", self)
        self._undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self._undo_action.triggered.connect(self._on_undo)
        self._undo_action.setEnabled(False)

        self._redo_action = QAction("Yeniden Yap", self)
        self._redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self._redo_action.triggered.connect(self._on_redo)
        self._redo_action.setEnabled(False)

        self._apply_action = QAction("Değişiklikleri Uygula", self)
        self._apply_action.setShortcut(QKeySequence("Ctrl+Return"))
        self._apply_action.triggered.connect(self._on_apply_changes)
        self._apply_action.setEnabled(False)

        self._reset_action = QAction("Tümünü Sıfırla", self)
        self._reset_action.setShortcut(QKeySequence("Ctrl+Shift+R"))
        self._reset_action.triggered.connect(self._on_reset_all)
        self._reset_action.setEnabled(False)

        # ── Görünüm Eylemleri ──
        self._fit_action = QAction("Pencereye Sığdır", self)
        self._fit_action.setShortcut(QKeySequence("Ctrl+0"))
        self._fit_action.triggered.connect(self._on_fit_to_window)

        self._zoom_fit_action = QAction("Sığdır (Büyüt)", self)
        self._zoom_fit_action.setShortcut(QKeySequence("Ctrl+9"))
        self._zoom_fit_action.triggered.connect(self._on_zoom_fit)

        self._actual_size_action = QAction("Gerçek Boyut (1:1)", self)
        self._actual_size_action.setShortcut(QKeySequence("Ctrl+1"))
        self._actual_size_action.triggered.connect(self._on_actual_size)

    def _create_menus(self):
        """Menü çubuğunu oluşturur."""
        menu_bar = self.menuBar()

        # ── Dosya Menüsü ──
        file_menu = menu_bar.addMenu("Dosya")
        file_menu.addAction(self._open_action)
        file_menu.addSeparator()
        file_menu.addAction(self._save_action)
        file_menu.addAction(self._save_as_action)
        file_menu.addAction(self._export_action)
        file_menu.addSeparator()
        file_menu.addAction(self._quit_action)

        # ── Düzenleme Menüsü ──
        edit_menu = menu_bar.addMenu("Düzenle")
        edit_menu.addAction(self._undo_action)
        edit_menu.addAction(self._redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self._apply_action)
        edit_menu.addAction(self._reset_action)

        # ── Görünüm Menüsü ──
        view_menu = menu_bar.addMenu("Görünüm")
        view_menu.addAction(self._fit_action)
        view_menu.addAction(self._zoom_fit_action)
        view_menu.addAction(self._actual_size_action)

    def _create_toolbar(self):
        """Ana araç çubuğunu oluşturur."""
        toolbar = QToolBar("Ana Araçlar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        toolbar.addAction(self._open_action)
        toolbar.addAction(self._save_action)
        toolbar.addSeparator()
        toolbar.addAction(self._undo_action)
        toolbar.addAction(self._redo_action)
        toolbar.addSeparator()
        toolbar.addAction(self._apply_action)
        toolbar.addAction(self._reset_action)
        toolbar.addSeparator()
        toolbar.addAction(self._fit_action)
        toolbar.addAction(self._actual_size_action)

        self.addToolBar(toolbar)

    # ═══════════════════════════════════════════════════════════════
    # ── MERKEZİ ARAYÜZ ──
    # ═══════════════════════════════════════════════════════════════

    def _create_central_ui(self):
        """Merkezi arayüz düzenini oluşturur: Tuval + Sağ Panel."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Ayırıcı (splitter) ile tuval ve panel arasında boyut ayarı
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── Sol: Görüntü Tuvali ──
        self._canvas = CanvasWidget()
        splitter.addWidget(self._canvas)

        # ── Sağ: Düzenleme Panelleri ──
        right_panel = QWidget()
        right_panel.setObjectName("sidePanel")
        right_panel.setFixedWidth(360)
        right_panel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Sekmeli panel (Tab Widget)
        self._tab_widget = QTabWidget()

        # Ayarlamalar sekmesi
        self._adjustment_panel = AdjustmentPanel()
        self._tab_widget.addTab(self._adjustment_panel, "Ayarlar")

        # Filtreler sekmesi
        self._filter_panel = FilterPanel()
        self._tab_widget.addTab(self._filter_panel, "Filtreler")

        # Gürültü sekmesi
        self._noise_panel = NoisePanel()
        self._tab_widget.addTab(self._noise_panel, "Gürültü")

        # Dönüşüm sekmesi
        self._transform_panel = TransformPanel()
        self._tab_widget.addTab(self._transform_panel, "Dönüşüm")

        right_layout.addWidget(self._tab_widget)
        splitter.addWidget(right_panel)

        # Splitter boyut oranları
        splitter.setStretchFactor(0, 1)  # Tuval esnek
        splitter.setStretchFactor(1, 0)  # Panel sabit

        main_layout.addWidget(splitter)

    def _create_status_bar(self):
        """Durum çubuğunu oluşturur."""
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

        # Dosya bilgisi
        self._file_label = QLabel("Dosya yüklenmedi")
        self._status_bar.addWidget(self._file_label)

        # Esnek boşluk
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._status_bar.addWidget(spacer)

        # Boyut bilgisi
        self._size_label = QLabel("")
        self._status_bar.addPermanentWidget(self._size_label)

        # Zoom bilgisi
        self._zoom_label = QLabel("100%")
        self._zoom_label.setMinimumWidth(60)
        self._status_bar.addPermanentWidget(self._zoom_label)

        # İşleme göstergesi
        self._processing_label = QLabel("")
        self._processing_label.setStyleSheet("color: #58a6ff;")
        self._status_bar.addPermanentWidget(self._processing_label)

    # ═══════════════════════════════════════════════════════════════
    # ── SİNYAL BAĞLANTILARI ──
    # ═══════════════════════════════════════════════════════════════

    def _connect_signals(self):
        """Tüm sinyal-slot bağlantılarını kurar."""

        # ── Ayarlama paneli sinyalleri ──
        self._adjustment_panel.adjustment_changed.connect(self._on_adjustment_changed)
        self._adjustment_panel.reset_all_requested.connect(self._on_reset_adjustments)

        # ── Filtre paneli sinyalleri ──
        self._filter_panel.filter_changed.connect(self._on_filter_changed)
        self._filter_panel.reset_all_requested.connect(self._on_reset_filters)

        # ── Gürültü paneli sinyalleri ──
        self._noise_panel.noise_changed.connect(self._on_noise_changed)
        self._noise_panel.reset_requested.connect(self._on_reset_noise)

        # ── Dönüşüm paneli sinyalleri ──
        self._transform_panel.resize_requested.connect(self._on_resize)
        self._transform_panel.rotate_requested.connect(self._on_rotate)
        self._transform_panel.flip_requested.connect(self._on_flip)

        # ── Worker sinyalleri ──
        self._processing_thread.worker.processing_started.connect(self._on_processing_started)
        self._processing_thread.worker.processing_finished.connect(self._on_processing_finished)
        self._processing_thread.worker.error_occurred.connect(self._on_processing_error)

        # ── Tuval sinyalleri ──
        self._canvas.zoom_changed.connect(self._on_zoom_changed)

    # ═══════════════════════════════════════════════════════════════
    # ── DOSYA İŞLEMLERİ ──
    # ═══════════════════════════════════════════════════════════════

    @Slot()
    def _on_open(self):
        """Dosya aç diyalogu ile görüntü yükler."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Görüntü Aç", "", SUPPORTED_IMAGE_FORMATS
        )
        if not file_path:
            return

        if self._processor.load_image(file_path):
            # Başarılı yükleme
            self._update_canvas_from_original()
            self._update_ui_state()
            self._update_status_bar()
            self._canvas.fit_to_window()

            # Dönüşüm panelini güncelle
            w, h = self._processor.image_size
            self._transform_panel.update_image_size(w, h)

            # Panelleri sıfırla
            self._adjustment_panel.reset_all()
            self._filter_panel.reset_all()
            self._noise_panel.reset_all()

            file_name = os.path.basename(file_path)
            self.setWindowTitle(f"{APP_NAME} - {file_name}")
            self._status_bar.showMessage(f"Yüklendi: {file_name}", 3000)
        else:
            QMessageBox.warning(
                self, "Hata",
                f"Görüntü yüklenemedi:\n{file_path}"
            )

    @Slot()
    def _on_save(self):
        """Mevcut dosya yoluna kaydeder."""
        if self._processor.file_path:
            if self._processor.save_image(self._processor.file_path):
                self._status_bar.showMessage("Kaydedildi.", 3000)
            else:
                QMessageBox.warning(self, "Hata", "Dosya kaydedilemedi!")
        else:
            self._on_save_as()

    @Slot()
    def _on_save_as(self):
        """Farklı kaydet diyalogu."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Farklı Kaydet", "", SAVE_IMAGE_FORMATS
        )
        if file_path:
            if self._processor.save_image(file_path):
                self.setWindowTitle(f"{APP_NAME} - {os.path.basename(file_path)}")
                self._status_bar.showMessage(f"Kaydedildi: {file_path}", 3000)
            else:
                QMessageBox.warning(self, "Hata", "Dosya kaydedilemedi!")

    @Slot()
    def _on_export(self):
        """Dışa aktarma diyalogu ile kalite ayarlı kaydetme."""
        dialog = ExportDialog(self)
        if dialog.exec():
            ext = dialog.format_extension
            quality = dialog.quality

            file_path, _ = QFileDialog.getSaveFileName(
                self, "Dışa Aktar", f"export.{ext}",
                f"{ext.upper()} (*.{ext})"
            )
            if file_path:
                if self._processor.save_image(file_path, quality):
                    self._status_bar.showMessage(
                        f"Dışa aktarıldı: {file_path} (Kalite: {quality}%)", 3000
                    )
                else:
                    QMessageBox.warning(self, "Hata", "Dışa aktarma başarısız!")

    # ═══════════════════════════════════════════════════════════════
    # ── DÜZENLEME İŞLEMLERİ ──
    # ═══════════════════════════════════════════════════════════════

    @Slot(str, int)
    def _on_adjustment_changed(self, key: str, value: int):
        """Ayarlama slider'ı değiştiğinde çağrılır."""
        self._processor.set_adjustment(key, value)
        self._schedule_processing()

    @Slot(str, int)
    def _on_filter_changed(self, filter_name: str, intensity: int):
        """Filtre slider'ı değiştiğinde çağrılır."""
        self._processor.set_filter(filter_name, intensity)
        self._schedule_processing()

    @Slot(dict)
    def _on_noise_changed(self, params: dict):
        """Gürültü parametreleri değiştiğinde çağrılır."""
        self._processor.set_noise_params(**params)
        self._schedule_processing()

    def _on_reset_adjustments(self):
        """Ayarlamaları sıfırla."""
        for key in self._processor._adjustments:
            default = 100 if key == "gamma" else 0
            self._processor.set_adjustment(key, default)
        self._schedule_processing()

    def _on_reset_filters(self):
        """Filtreleri sıfırla."""
        self._processor._filters.clear()
        self._schedule_processing()

    def _on_reset_noise(self):
        """Gürültüyü sıfırla."""
        self._processor.set_noise_params(
            type="gaussian", intensity=0, monochrome=True, scale=1.0
        )
        self._schedule_processing()

    @Slot()
    def _on_apply_changes(self):
        """Mevcut değişiklikleri kalıcı olarak uygular."""
        if not self._processor.has_image:
            return

        self._processor.apply_current_changes()
        self._update_canvas_from_original()

        # Tüm panelleri sıfırla
        self._adjustment_panel.reset_all()
        self._filter_panel.reset_all()
        self._noise_panel.reset_all()

        self._update_ui_state()
        self._update_status_bar()
        self._status_bar.showMessage("Değişiklikler uygulandı.", 2000)

    @Slot()
    def _on_reset_all(self):
        """Tüm düzenlemeleri sıfırlar (orijinal görüntüye dön)."""
        self._adjustment_panel.reset_all()
        self._filter_panel.reset_all()
        self._noise_panel.reset_all()

        self._on_reset_adjustments()
        self._on_reset_filters()
        self._on_reset_noise()

    # ── Geri Al / Yeniden Yap ──

    @Slot()
    def _on_undo(self):
        """Geri al."""
        if self._processor.undo():
            self._update_canvas_from_original()
            self._adjustment_panel.reset_all()
            self._filter_panel.reset_all()
            self._noise_panel.reset_all()
            self._update_ui_state()
            self._update_status_bar()
            self._status_bar.showMessage("Geri alındı.", 1500)

    @Slot()
    def _on_redo(self):
        """Yeniden yap."""
        if self._processor.redo():
            self._update_canvas_from_original()
            self._adjustment_panel.reset_all()
            self._filter_panel.reset_all()
            self._noise_panel.reset_all()
            self._update_ui_state()
            self._update_status_bar()
            self._status_bar.showMessage("Yeniden yapıldı.", 1500)

    # ═══════════════════════════════════════════════════════════════
    # ── DÖNÜŞÜM İŞLEMLERİ ──
    # ═══════════════════════════════════════════════════════════════

    @Slot(int, int, str)
    def _on_resize(self, width: int, height: int, method: str):
        """Görüntüyü yeniden boyutlandırır."""
        if not self._processor.has_image:
            return

        self._processor.apply_resize(width, height, method)
        self._update_canvas_from_original()
        self._canvas.fit_to_window()

        w, h = self._processor.image_size
        self._transform_panel.update_image_size(w, h)
        self._update_ui_state()
        self._update_status_bar()
        self._status_bar.showMessage(f"Boyutlandırıldı: {w}×{h}", 2000)

    @Slot(float)
    def _on_rotate(self, angle: float):
        """Görüntüyü döndürür."""
        if not self._processor.has_image:
            return

        self._processor.apply_rotation(angle)
        self._update_canvas_from_original()
        self._canvas.fit_to_window()

        w, h = self._processor.image_size
        self._transform_panel.update_image_size(w, h)
        self._update_ui_state()
        self._update_status_bar()
        self._status_bar.showMessage(f"Döndürüldü: {angle}°", 2000)

    @Slot(bool)
    def _on_flip(self, horizontal: bool):
        """Görüntüyü çevirir."""
        if not self._processor.has_image:
            return

        self._processor.apply_flip(horizontal)
        self._update_canvas_from_original()
        direction = "Yatay" if horizontal else "Dikey"
        self._status_bar.showMessage(f"{direction} çevrildi.", 2000)
        self._update_ui_state()

    # ═══════════════════════════════════════════════════════════════
    # ── GÖRÜNÜM İŞLEMLERİ ──
    # ═══════════════════════════════════════════════════════════════

    @Slot()
    def _on_fit_to_window(self):
        self._canvas.fit_to_window()

    @Slot()
    def _on_zoom_fit(self):
        self._canvas.zoom_to_fit()

    @Slot()
    def _on_actual_size(self):
        self._canvas.zoom_actual()

    @Slot(float)
    def _on_zoom_changed(self, zoom: float):
        self._zoom_label.setText(f"{zoom * 100:.0f}%")

    # ═══════════════════════════════════════════════════════════════
    # ── İŞLEME YÖNETİMİ ──
    # ═══════════════════════════════════════════════════════════════

    def _schedule_processing(self):
        """
        Debounce mekanizması ile işleme talebini zamanlar.
        Her slider değişikliğinde zamanlayıcı sıfırlanır,
        böylece yalnızca son değişiklik işlenir.
        """
        if not self._processor.has_image:
            return
        self._debounce_timer.start()

    def _request_processing(self):
        """Debounce süresi dolduktan sonra işleme talebini worker'a gönderir."""
        self._processing_thread.request_processing()

    @Slot()
    def _on_processing_started(self):
        """İşleme başladığında çağrılır."""
        self._is_processing = True
        self._processing_label.setText("İşleniyor...")

    @Slot(np.ndarray)
    def _on_processing_finished(self, result: np.ndarray):
        """İşleme tamamlandığında sonucu tuvale yansıtır."""
        self._is_processing = False
        self._processing_label.setText("")
        self._canvas.set_image(result)
        self._update_ui_state()

    @Slot(str)
    def _on_processing_error(self, error: str):
        """İşleme hatası olduğunda."""
        self._is_processing = False
        self._processing_label.setText("")
        self._status_bar.showMessage(f"Hata: {error}", 5000)

    # ═══════════════════════════════════════════════════════════════
    # ── YARDIMCI METOTLAR ──
    # ═══════════════════════════════════════════════════════════════

    def _update_canvas_from_original(self):
        """Tuvali orijinal önizleme görüntüsü ile günceller."""
        preview = self._processor.preview_original
        if preview is not None:
            self._canvas.set_image(preview)

    def _update_ui_state(self):
        """Buton ve menü durumlarını günceller."""
        has_image = self._processor.has_image

        self._save_action.setEnabled(has_image)
        self._save_as_action.setEnabled(has_image)
        self._export_action.setEnabled(has_image)
        self._apply_action.setEnabled(has_image)
        self._reset_action.setEnabled(has_image)
        self._undo_action.setEnabled(self._processor.can_undo())
        self._redo_action.setEnabled(self._processor.can_redo())

    def _update_status_bar(self):
        """Durum çubuğu bilgilerini günceller."""
        if not self._processor.has_image:
            self._file_label.setText("Dosya yüklenmedi")
            self._size_label.setText("")
            return

        # Dosya adı
        if self._processor.file_path:
            name = os.path.basename(self._processor.file_path)
            self._file_label.setText(name)
        else:
            self._file_label.setText("Kaydedilmemiş")

        # Boyut bilgisi
        info = get_image_info(self._processor.original)
        self._size_label.setText(
            f"{info.get('width', 0)}×{info.get('height', 0)} | "
            f"{info.get('megapixels', '')} | {info.get('size', '')}"
        )

    # ═══════════════════════════════════════════════════════════════
    # ── PENCERE OLAYLARI ──
    # ═══════════════════════════════════════════════════════════════

    def closeEvent(self, event):
        """Pencere kapatılırken temizlik yapar."""
        # Bekleyen değişiklik kontrolü
        if self._processor.has_pending_changes():
            reply = QMessageBox.question(
                self, "Kaydedilmemiş Değişiklikler",
                "Uygulanmamış değişiklikler var. Çıkmak istiyor musunuz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return

        # Worker thread'i temizle
        self._processing_thread.stop()
        event.accept()

    def dragEnterEvent(self, event):
        """Sürükle-bırak: dosya türü kontrolü."""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(
                    ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.webp')
                ):
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event):
        """Sürükle-bırak: dosyayı yükle."""
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(
                ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.webp')
            ):
                if self._processor.load_image(file_path):
                    self._update_canvas_from_original()
                    self._update_ui_state()
                    self._update_status_bar()
                    self._canvas.fit_to_window()

                    w, h = self._processor.image_size
                    self._transform_panel.update_image_size(w, h)
                    self._adjustment_panel.reset_all()
                    self._filter_panel.reset_all()
                    self._noise_panel.reset_all()

                    self.setWindowTitle(
                        f"{APP_NAME} - {os.path.basename(file_path)}"
                    )
                break
