"""
Uygulama Tema ve Stil Tanımları - Dark Theme QSS (Qt Style Sheet).
Modern, profesyonel ve göz yormayan koyu tema.
"""

DARK_THEME_QSS = """
/* ─── Genel Uygulama Stili ──────────────────────────────────── */
QMainWindow {
    background-color: #0d1117;
    color: #e6edf3;
}

QWidget {
    background-color: transparent;
    color: #e6edf3;
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", sans-serif;
    font-size: 13px;
}

/* ─── Menü Çubuğu ──────────────────────────────────────────── */
QMenuBar {
    background-color: #161b22;
    color: #e6edf3;
    border-bottom: 1px solid #30363d;
    padding: 2px;
    spacing: 4px;
}

QMenuBar::item {
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #21262d;
}

QMenu {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 6px;
}

QMenu::item {
    padding: 8px 32px 8px 16px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #1f6feb;
}

QMenu::separator {
    height: 1px;
    background: #30363d;
    margin: 4px 8px;
}

/* ─── Araç Çubuğu ──────────────────────────────────────────── */
QToolBar {
    background-color: #161b22;
    border-bottom: 1px solid #30363d;
    padding: 4px 8px;
    spacing: 4px;
}

QToolBar QToolButton {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 8px 12px;
    color: #8b949e;
    font-weight: 500;
    font-size: 12px;
}

QToolBar QToolButton:hover {
    background-color: #21262d;
    color: #e6edf3;
}

QToolBar QToolButton:pressed {
    background-color: #30363d;
}

/* ─── Sekmeli Panel (Tab Widget) ────────────────────────────── */
QTabWidget::pane {
    border: none;
    background-color: #0d1117;
}

QTabBar::tab {
    background-color: transparent;
    color: #8b949e;
    padding: 10px 18px;
    border: none;
    border-bottom: 2px solid transparent;
    font-weight: 500;
    margin-right: 2px;
}

QTabBar::tab:selected {
    color: #e6edf3;
    border-bottom: 2px solid #1f6feb;
}

QTabBar::tab:hover:!selected {
    color: #c9d1d9;
    border-bottom: 2px solid #30363d;
}

/* ─── Kaydırma Alanı ───────────────────────────────────────── */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    border: none;
    background-color: #0d1117;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #30363d;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #484f58;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    border: none;
    background-color: #0d1117;
    height: 8px;
}

QScrollBar::handle:horizontal {
    background-color: #30363d;
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #484f58;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ─── Slider ────────────────────────────────────────────────── */
QSlider::groove:horizontal {
    border: none;
    height: 4px;
    background: #21262d;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #1f6feb;
    border: 2px solid #1f6feb;
    width: 14px;
    height: 14px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #388bfd;
    border-color: #388bfd;
}

QSlider::handle:horizontal:pressed {
    background: #58a6ff;
    border-color: #58a6ff;
}

QSlider::sub-page:horizontal {
    background: #1f6feb;
    border-radius: 2px;
}

/* ─── Etiket ────────────────────────────────────────────────── */
QLabel {
    color: #e6edf3;
    background: transparent;
}

/* ─── Düğme ─────────────────────────────────────────────────── */
QPushButton {
    background-color: #21262d;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    min-height: 18px;
}

QPushButton:hover {
    background-color: #30363d;
    border-color: #484f58;
}

QPushButton:pressed {
    background-color: #161b22;
}

QPushButton#primaryButton {
    background-color: #1f6feb;
    border-color: #1f6feb;
    color: #ffffff;
}

QPushButton#primaryButton:hover {
    background-color: #388bfd;
}

QPushButton#dangerButton {
    background-color: #da3633;
    border-color: #da3633;
    color: #ffffff;
}

QPushButton#dangerButton:hover {
    background-color: #f85149;
}

QPushButton#resetButton {
    background-color: transparent;
    border: none;
    color: #8b949e;
    padding: 4px 8px;
    font-size: 11px;
}

QPushButton#resetButton:hover {
    color: #e6edf3;
}

/* ─── ComboBox ──────────────────────────────────────────────── */
QComboBox {
    background-color: #21262d;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 12px;
    min-width: 100px;
}

QComboBox:hover {
    border-color: #484f58;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 4px;
    selection-background-color: #1f6feb;
}

/* ─── SpinBox ───────────────────────────────────────────────── */
QSpinBox, QDoubleSpinBox {
    background-color: #21262d;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 8px;
}

QSpinBox:hover, QDoubleSpinBox:hover {
    border-color: #484f58;
}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background-color: #30363d;
    border: none;
    width: 16px;
}

/* ─── CheckBox ──────────────────────────────────────────────── */
QCheckBox {
    spacing: 8px;
    color: #e6edf3;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #30363d;
    border-radius: 4px;
    background-color: #0d1117;
}

QCheckBox::indicator:checked {
    background-color: #1f6feb;
    border-color: #1f6feb;
}

QCheckBox::indicator:hover {
    border-color: #484f58;
}

/* ─── GroupBox ──────────────────────────────────────────────── */
QGroupBox {
    border: 1px solid #21262d;
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 20px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #8b949e;
}

/* ─── Durum Çubuğu ──────────────────────────────────────────── */
QStatusBar {
    background-color: #161b22;
    color: #8b949e;
    border-top: 1px solid #30363d;
    padding: 2px 8px;
    font-size: 12px;
}

QStatusBar::item {
    border: none;
}

/* ─── Ayırıcı ───────────────────────────────────────────────── */
QSplitter::handle {
    background-color: #30363d;
}

QSplitter::handle:horizontal {
    width: 1px;
}

QSplitter::handle:vertical {
    height: 1px;
}

/* ─── Araç İpucu ────────────────────────────────────────────── */
QToolTip {
    background-color: #1c2128;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}

/* ─── İlerleme Çubuğu ───────────────────────────────────────── */
QProgressBar {
    background-color: #21262d;
    border: none;
    border-radius: 4px;
    height: 4px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #1f6feb;
    border-radius: 4px;
}

/* ─── Panel Başlık Etiketi ──────────────────────────────────── */
QLabel#panelTitle {
    font-size: 14px;
    font-weight: 600;
    color: #e6edf3;
    padding: 8px 0;
}

QLabel#sectionTitle {
    font-size: 12px;
    font-weight: 600;
    color: #8b949e;
    padding: 12px 0 4px 0;
    text-transform: uppercase;
}

QLabel#valueLabel {
    font-size: 11px;
    color: #58a6ff;
    font-family: "Cascadia Code", "Consolas", monospace;
    min-width: 40px;
}

/* ─── Sağ Panel Arka Plan ───────────────────────────────────── */
QWidget#sidePanel {
    background-color: #0d1117;
    border-left: 1px solid #21262d;
}

QWidget#canvasContainer {
    background-color: #010409;
}
"""
