"""
Client Report Engine - Generate professional reports from templates.
"""

from .renderer import render_docx, TEMPLATE_DIR, OUTPUT_DIR
from .pdf import docx_to_pdf, PdfConversionError
from .cli import main

__version__ = "1.0.0"
__all__ = [
    "render_docx",
    "docx_to_pdf",
    "PdfConversionError",
    "TEMPLATE_DIR",
    "OUTPUT_DIR",
    "main",
]

