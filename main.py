"""
PixelForge - Profesyonel Görsel Düzenleme Uygulaması
Ana giriş noktası (Entry Point).

Uygulama mimarisi:
    - PySide6 (Qt 6) ile modern dark theme arayüz
    - OpenCV + NumPy ile yüksek performanslı görüntü işleme
    - Thread-tabanlı arka plan işleme (UI donması önlenir)
    - Tahribatsız (non-destructive) düzenleme pipeline'ı
    - Modüler, SOLID prensiplerine uygun mimari

Çalıştırma:
    python main.py
"""

import sys
import os

# Modül yolunu ayarla (proje kök dizininden çalışması için)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app.ui.main_window import MainWindow
from app.ui.styles import DARK_THEME_QSS
from app.utils.constants import APP_NAME, APP_VERSION


def main():
    """Uygulamayı başlatır ve ana döngüyü çalıştırır."""

    # Yüksek DPI ölçekleme desteği
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("PixelForge Studio")

    # Varsayılan font ayarı
    font = QFont("Segoe UI", 10)
    font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    app.setFont(font)

    # Dark theme stil dosyasını uygula
    app.setStyleSheet(DARK_THEME_QSS)

    # Ana pencereyi oluştur ve göster
    window = MainWindow()
    window.setAcceptDrops(True)  # Sürükle-bırak desteği
    window.show()

    # Pencere açıldıktan sonra sığdır
    window._canvas.fit_to_window()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
