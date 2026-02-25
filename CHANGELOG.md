# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-02-25

### Added
- **Initial Release**
- Professional desktop image editing application
- 18 image filters (Gaussian Blur, Box Blur, Median Blur, Sharpen, Unsharp Mask, Edge Detection, Emboss, Sepia, Vintage, Vignette, HDR Effect, Pencil Sketch, Oil Painting, Pixelate, Posterize, Warm Filter, Cool Filter, Dramatic)
- 7 noise types (Gaussian, Salt & Pepper, Poisson, Speckle, Uniform, Film Grain, Color Noise)
- 13 adjustment parameters (Brightness, Contrast, Saturation, Hue, Gamma, Exposure, Temperature, Tint, Highlights, Shadows, Clarity, Vibrance, Sharpness)
- Non-destructive editing with Undo/Redo support (30 steps)
- Real-time preview with 60ms debounce
- Background processing with QThread
- Drag & drop image support
- Cross-platform (Windows, macOS, Linux)

### Tech Stack
- Python 3.10+
- PySide6 (Qt 6)
- OpenCV 4.9+
- NumPy
- Pillow
