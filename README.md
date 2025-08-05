# shildiks
 The program converts text and label structures from photos (using computer vision recognition).

sudo apt install tesseract-ocr
Install Python dependencies:

pip install pytesseract pillow openpyxl

# Shildik OCR Dashboard

A Python-based application for automatic digit recognition from images of industrial nameplates ("shildiks"). The results can be exported to Excel or plain text format. The program uses Tesseract OCR and provides a simple GUI for user interaction.

---

## Features

- Batch processing of multiple images (40+ supported)
- Image preprocessing: cropping, contrast enhancement, filtering
- Digit-only recognition using Tesseract OCR
- Graphical user interface built with `tkinter`
- Export options: `.xlsx` or `.txt`
- Folder and file selection via dialog boxes

---

## Dependencies

Make sure the following packages and tools are installed:

### System requirements

- Python 3.7+
- Tesseract OCR engine

### Python packages

Install via pip:

```bash
pip install pytesseract pillow openpyxl

import os
import threading
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import openpyxl
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


