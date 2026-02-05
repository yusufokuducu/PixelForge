<p align="center">
  <img src="https://img.shields.io/badge/PixelForge-v1.0.0-blue?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTE0LjcgNi4zYTEgMSAwIDAgMCAwIDEuNGw1LjYgNS42IiAvPjxwYXRoIGQ9Im01LjcgMTAtNC0uMiIgLz48L3N2Zz4=" alt="PixelForge"/>
</p>

<h1 align="center">PixelForge</h1>

<p align="center">
  <strong>Professional Desktop Image Editing Application</strong><br>
  <em>Built with Python & Qt — real-time preview, high-performance image processing engine</em>
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/Qt-6_(PySide6)-41CD52?style=flat-square&logo=qt&logoColor=white" alt="Qt6"></a>
  <a href="#"><img src="https://img.shields.io/badge/OpenCV-4.9+-5C3EE8?style=flat-square&logo=opencv&logoColor=white" alt="OpenCV"></a>
  <a href="#"><img src="https://img.shields.io/badge/NumPy-2.0+-013243?style=flat-square&logo=numpy&logoColor=white" alt="NumPy"></a>
  <a href="#"><img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square" alt="Platform"></a>
  <a href="https://github.com/yusufokuducu/PixelForge/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"></a>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## About

**PixelForge** is a **professional-grade** desktop image editing application built entirely within the Python ecosystem. It delivers a modern dark-themed interface powered by PySide6 (Qt 6) and a **real-time** image processing pipeline driven by OpenCV + NumPy.

Every slider movement is instantly reflected in the preview — thanks to **QThread-based background processing**, the UI never freezes. The non-destructive editing architecture ensures you can always revert to the original image.

### Why PixelForge?

| Feature | Description |
|---------|-------------|
| **Real-Time Preview** | Instant feedback as you drag sliders (60ms debounce + threaded processing) |
| **18 Filters** | From Gaussian Blur to Oil Painting, Vintage to HDR |
| **7 Noise Types** | Film Grain, Poisson, Speckle and more — with grain size control |
| **13 Adjustment Parameters** | Brightness, Contrast, Exposure, Gamma, Saturation, Vibrance... |
| **Non-Destructive** | Original image is always preserved, with Undo/Redo support (30 steps) |
| **Drag & Drop** | Drop image files directly onto the window |
| **Cross-Platform** | Runs on Windows, macOS, and Linux |

---

## ✦ Features

### Adjustments
Precise control over light, color, and detail with **13 dedicated sliders**:

<table>
<tr>
<td width="33%">

**Light**
- Brightness
- Contrast
- Exposure (EV)
- Gamma Correction

</td>
<td width="33%">

**Color**
- Saturation
- Hue Shift
- Vibrance
- Temperature / Tint

</td>
<td width="33%">

**Detail**
- Highlights / Shadows
- Clarity
- Sharpness

</td>
</tr>
</table>

### Filters
**18 filters**, each with an **independent intensity slider**:

```
Blur & Sharpen              Artistic                Color & Style
──────────────              ────────                ─────────────
 Gaussian Blur               Edge Detection          Pixelate
 Box Blur                    Emboss                  Posterize
 Median Blur                 Sepia                   Warm Filter
 Sharpen                     Vintage                 Cool Filter
 Unsharp Mask                Vignette                Dramatic
                             HDR Effect
                             Pencil Sketch
                             Oil Painting
```

> Filters are **chainable** — use multiple filters simultaneously at different intensities.

### Noise Effects
A **detailed noise control panel** rarely found in other editors:

| Noise Type | Description |
|:-----------|:------------|
| **Gaussian** | Natural camera sensor noise simulation |
| **Salt & Pepper** | Random black and white pixel noise |
| **Poisson** | Low-light photography simulation |
| **Speckle** | Multiplicative noise (radar/ultrasound style) |
| **Uniform** | Evenly distributed, harsh noise |
| **Film Grain** | Analog film grain effect (luminance-dependent) |
| **Color Noise** | Independent per-channel noise |

**Additional Controls:**
- Intensity slider (0–100%)
- Monochrome / Color toggle
- Grain size (scale) control

### Transform
- **Resize** — 5 interpolation methods (Nearest, Bilinear, Bicubic, Lanczos, Area)
- **Aspect ratio lock** for proportional scaling
- **Quick scale** buttons (25%, 50%, 75%, 150%, 200%)
- **Rotation** — 90° clockwise/counter-clockwise + free angle
- **Flip** — Horizontal / Vertical mirror

### Interface & Experience
- **GitHub-inspired Dark Theme** — modern, easy on the eyes
- **Zoom & Pan** — scroll wheel to zoom, drag to pan
- **Double-click** to fit image to window
- **Keyboard shortcuts** — Ctrl+O, Ctrl+S, Ctrl+Z/Y, Ctrl+E...
- **Export** — save with format and quality options (PNG, JPEG, WebP, BMP, TIFF)

---

## ⚡ Installation

### Prerequisites
- **Python 3.10** or higher
- pip package manager

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/yusufokuducu/PixelForge.git
cd PixelForge

# 2. (Recommended) Create a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the application
python main.py
```

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `PySide6` | >= 6.6.0 | Qt 6 GUI framework |
| `opencv-python` | >= 4.9.0 | Image processing engine |
| `numpy` | >= 1.26.0 | High-performance array operations |
| `Pillow` | >= 10.2.0 | Extended image format support |

---

## ⌨ Usage

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + O` | Open image |
| `Ctrl + S` | Save |
| `Ctrl + Shift + S` | Save as |
| `Ctrl + E` | Export (with quality options) |
| `Ctrl + Z` | Undo |
| `Ctrl + Y` | Redo |
| `Ctrl + Enter` | Apply changes |
| `Ctrl + Shift + R` | Reset all |
| `Ctrl + 0` | Fit to window |
| `Ctrl + 1` | Actual size (1:1) |
| `Scroll Wheel` | Zoom in / Zoom out |
| `Drag` | Pan image |
| `Double Click` | Fit to window |

### Quick Start

1. **Load an Image** — `Ctrl+O` or drag & drop a file onto the window
2. **Edit** — Use the sliders in the right panel tabs (Adjustments / Filters / Noise / Transform)
3. **Preview** — Every slider change is instantly rendered on the canvas
4. **Apply** — `Ctrl+Enter` to permanently bake in current edits
5. **Save** — `Ctrl+S` or `Ctrl+E` to export in your preferred format

---

## ⚙ Architecture

PixelForge follows **SOLID principles** with a modular, layered architecture:

```
pixelforge/
│
├── main.py                              # Entry point
├── requirements.txt                     # Dependencies
│
├── app/
│   ├── core/                            # Business Logic Layer
│   │   ├── image_processor.py           # Central pipeline manager
│   │   ├── filter_engine.py             # 18 filters (static methods)
│   │   ├── noise_engine.py              # 7 noise types
│   │   ├── transform_engine.py          # Geometric transformations
│   │   └── history_manager.py           # Undo/Redo stack
│   │
│   ├── ui/                              # Presentation Layer
│   │   ├── main_window.py               # Main window + menus + toolbar
│   │   ├── canvas_widget.py             # Zoom/Pan-enabled canvas
│   │   ├── styles.py                    # Dark theme QSS
│   │   ├── components/
│   │   │   └── labeled_slider.py        # Reusable slider widget
│   │   ├── panels/
│   │   │   ├── adjustment_panel.py      # Adjustment controls
│   │   │   ├── filter_panel.py          # Filter controls
│   │   │   ├── noise_panel.py           # Noise controls
│   │   │   └── transform_panel.py       # Transform controls
│   │   └── dialogs/
│   │       └── resize_dialog.py         # Export dialog
│   │
│   ├── workers/                         # Background Processing Layer
│   │   └── processing_worker.py         # QThread-based worker
│   │
│   └── utils/                           # Utility Layer
│       ├── constants.py                 # Centralized constants
│       └── image_utils.py               # NumPy ↔ Qt conversions
```

### Processing Pipeline

```
                    ┌─────────────┐
                    │  Original   │
                    │   Image     │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ Adjustments  │  Brightness, Contrast, Gamma,
                    │              │  Saturation, Exposure...
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Filters    │  Blur, Sharpen, Sepia,
                    │              │  HDR, Vintage...
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │    Noise     │  Gaussian, Film Grain,
                    │              │  Salt & Pepper...
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Result     │──→ Canvas (Preview)
                    │              │──→ File (Full Resolution)
                    └─────────────┘
```

### Performance Strategy

```
  Slider Change
         │
         ▼
  ┌──────────────┐     60ms        ┌───────────────┐
  │   Debounce   │ ──────────────→ │   QThread      │
  │   Timer      │    delay        │   Worker       │
  └──────────────┘                 └───────┬───────┘
                                           │
                                   Processes on preview
                                   (max 1920×1080)
                                           │
                                   ┌───────▼───────┐
                                   │  Signal/Slot   │
                                   │  delivers      │
                                   │  result to UI  │
                                   └───────────────┘
```

- **Debounce (60ms):** Prevents slider spam, only processes the last value
- **QThread:** Image processing runs in the background — UI thread never blocks
- **Preview Mode:** Real-time operations run on a downscaled copy
- **Full Resolution:** Original size processing only on save/apply

---

## 🛠 Tech Stack

<table>
<tr>
<td align="center" width="25%">
<strong>PySide6</strong><br>
<sub>Qt 6 GUI Framework</sub><br>
<sub>Modern widgets, QSS theming, signal/slot</sub>
</td>
<td align="center" width="25%">
<strong>OpenCV</strong><br>
<sub>Image Processing</sub><br>
<sub>Filters, transforms, color spaces</sub>
</td>
<td align="center" width="25%">
<strong>NumPy</strong><br>
<sub>Numerical Computing</sub><br>
<sub>Vectorized ops, fast array manipulation</sub>
</td>
<td align="center" width="25%">
<strong>Pillow</strong><br>
<sub>Format Support</sub><br>
<sub>Wide image format compatibility</sub>
</td>
</tr>
</table>

---

## 🤝 Contributing

Contributions make this project better! Follow the steps below to get involved:

```bash
# 1. Fork the repository
# 2. Create a feature branch
git checkout -b feature/awesome-feature

# 3. Commit your changes
git commit -m "feat: add new filter"

# 4. Push your branch
git push origin feature/awesome-feature

# 5. Open a Pull Request
```

### Contribution Areas

- **New Filters** — Add new image effects and processing algorithms
- **Performance** — Optimize processing speed and memory usage
- **UI/UX** — Suggest or implement interface improvements
- **Documentation** — Improve or translate documentation
- **Bug Fixes** — Report bugs or submit patches

---

## 📄 License

This project is licensed under the [MIT License](LICENSE). See the `LICENSE` file for details.

---

<p align="center">
  Unleash your creativity with <strong>PixelForge</strong>.<br>
  <sub>Built by <a href="https://github.com/yusufokuducu">@yusufokuducu</a></sub>
</p>

<p align="center">
  <a href="https://github.com/yusufokuducu/PixelForge/issues">Report Bug</a> •
  <a href="https://github.com/yusufokuducu/PixelForge/issues">Request Feature</a> •
  <a href="https://github.com/yusufokuducu/PixelForge/stargazers">Give a Star ⭐</a>
</p>
