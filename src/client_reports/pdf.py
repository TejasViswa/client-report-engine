import sys
import subprocess
import shutil
from pathlib import Path


class PdfConversionError(RuntimeError):
    pass


def _convert_with_libreoffice(docx_path: Path, output_dir: Path) -> Path:
    result = subprocess.run(
        [
            "soffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_dir),
            str(docx_path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise PdfConversionError(f"LibreOffice failed: {result.stderr}")
    return output_dir / (docx_path.stem + ".pdf")


def _convert_with_docx2pdf(docx_path: Path, pdf_path: Path) -> Path:
    try:
        from docx2pdf import convert
    except ImportError as exc:
        raise PdfConversionError("docx2pdf not installed") from exc

    convert(str(docx_path), str(pdf_path))
    if not pdf_path.exists():
        raise PdfConversionError("docx2pdf did not create output file")
    return pdf_path


def docx_to_pdf(input_path: str | Path, output_path: str | Path | None = None) -> Path:
    """
    Cross-platform DOCX → PDF conversion.

    Prefers LibreOffice (soffice) if available; otherwise uses docx2pdf on Windows/macOS.
    """
    docx_path = Path(input_path).resolve()
    if output_path is None:
        pdf_path = docx_path.with_suffix(".pdf")
    else:
        pdf_path = Path(output_path).resolve()

    output_dir = pdf_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Prefer LibreOffice if present on PATH
    if shutil.which("soffice"):
        return _convert_with_libreoffice(docx_path, output_dir)

    # Fallback: docx2pdf (typically requires Word on Windows/macOS)
    if sys.platform in {"win32", "darwin"}:
        return _convert_with_docx2pdf(docx_path, pdf_path)

    raise PdfConversionError(
        "No PDF backend found. Install LibreOffice (soffice on PATH) or docx2pdf."
    )
