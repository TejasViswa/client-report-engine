"""Tests for the PDF conversion module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from client_reports.pdf import (
    docx_to_pdf,
    PdfConversionError,
    _convert_with_libreoffice,
)


class TestDocxToPdf:
    """Tests for docx_to_pdf function."""
    
    @pytest.fixture
    def mock_docx_file(self, tmp_path):
        """Create a mock DOCX file for testing."""
        docx_file = tmp_path / "test.docx"
        docx_file.write_text("mock docx content")
        return docx_file
    
    @patch("shutil.which")
    @patch("client_reports.pdf._convert_with_libreoffice")
    def test_uses_libreoffice_when_available(
        self, mock_convert, mock_which, mock_docx_file, tmp_path
    ):
        """Test that LibreOffice is preferred when available."""
        mock_which.return_value = "/usr/bin/soffice"
        expected_pdf = tmp_path / "test.pdf"
        mock_convert.return_value = expected_pdf
        
        result = docx_to_pdf(mock_docx_file)
        
        mock_convert.assert_called_once()
        assert result == expected_pdf
    
    @patch("shutil.which")
    @patch("sys.platform", "linux")
    def test_raises_error_when_no_backend_on_linux(self, mock_which, mock_docx_file):
        """Test that error is raised when no PDF backend is found on Linux."""
        mock_which.return_value = None
        
        with pytest.raises(PdfConversionError) as exc_info:
            docx_to_pdf(mock_docx_file)
        
        assert "No PDF backend found" in str(exc_info.value)
    
    def test_output_path_defaults_to_same_directory(self, mock_docx_file):
        """Test that output defaults to same directory with .pdf extension."""
        with patch("shutil.which", return_value="/usr/bin/soffice"):
            with patch("client_reports.pdf._convert_with_libreoffice") as mock_convert:
                mock_convert.return_value = mock_docx_file.with_suffix(".pdf")
                result = docx_to_pdf(mock_docx_file)
        
        assert result.suffix == ".pdf"
        assert result.stem == mock_docx_file.stem
    
    def test_custom_output_path(self, mock_docx_file, tmp_path):
        """Test conversion with custom output path."""
        custom_output = tmp_path / "custom" / "output.pdf"
        
        with patch("shutil.which", return_value="/usr/bin/soffice"):
            with patch("client_reports.pdf._convert_with_libreoffice") as mock_convert:
                mock_convert.return_value = custom_output
                result = docx_to_pdf(mock_docx_file, custom_output)
        
        # The function should create parent directories
        mock_convert.assert_called_once()


class TestLibreOfficeConversion:
    """Tests for LibreOffice conversion backend."""
    
    @pytest.fixture
    def mock_docx_file(self, tmp_path):
        """Create a mock DOCX file."""
        docx_file = tmp_path / "test.docx"
        docx_file.write_text("mock")
        return docx_file
    
    @patch("subprocess.run")
    def test_libreoffice_success(self, mock_run, mock_docx_file, tmp_path):
        """Test successful LibreOffice conversion."""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        result = _convert_with_libreoffice(mock_docx_file, tmp_path)
        
        assert result == tmp_path / "test.pdf"
        mock_run.assert_called_once()
        
        # Verify soffice was called with correct args
        call_args = mock_run.call_args[0][0]
        assert "soffice" in call_args
        assert "--headless" in call_args
        assert "--convert-to" in call_args
        assert "pdf" in call_args
    
    @patch("subprocess.run")
    def test_libreoffice_failure(self, mock_run, mock_docx_file, tmp_path):
        """Test LibreOffice conversion failure."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="Error: conversion failed"
        )
        
        with pytest.raises(PdfConversionError) as exc_info:
            _convert_with_libreoffice(mock_docx_file, tmp_path)
        
        assert "LibreOffice failed" in str(exc_info.value)


class TestPdfConversionError:
    """Tests for PdfConversionError exception."""
    
    def test_is_runtime_error(self):
        """Verify PdfConversionError is a RuntimeError."""
        assert issubclass(PdfConversionError, RuntimeError)
    
    def test_error_message(self):
        """Test error message is preserved."""
        error = PdfConversionError("Test error message")
        assert str(error) == "Test error message"

