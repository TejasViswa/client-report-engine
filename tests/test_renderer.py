"""Tests for the renderer module."""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from client_reports.renderer import render_docx, TEMPLATE_DIR, OUTPUT_DIR


class TestRenderDocx:
    """Tests for render_docx function."""
    
    @pytest.fixture
    def sample_context(self):
        """Sample context data for testing."""
        return {
            "client_name": "Test Corp",
            "report_date": "2025-01-01",
            "report_period": "Q1 2025",
            "prepared_by": "Test User",
            "executive_summary": "Test summary",
            "metrics": [
                {"name": "Revenue", "value": "$1M", "change": "+10%", "status": "positive"}
            ],
            "highlights": ["Achievement 1", "Achievement 2"],
            "recommendations": [
                {"priority": "High", "title": "Action 1", "description": "Do something"}
            ],
            "contact": {
                "name": "John Doe",
                "title": "Manager",
                "email": "john@test.com",
                "phone": "555-1234"
            }
        }
    
    @pytest.fixture
    def data_dir(self):
        """Return path to test data directory."""
        return Path(__file__).resolve().parents[1] / "data"
    
    def test_template_dir_exists(self):
        """Verify TEMPLATE_DIR is correctly configured."""
        assert TEMPLATE_DIR.name == "templates"
        assert "reports" in str(TEMPLATE_DIR)
    
    def test_output_dir_is_configured(self):
        """Verify OUTPUT_DIR is correctly configured."""
        assert OUTPUT_DIR.name == "output"
        assert "reports" in str(OUTPUT_DIR)
    
    @patch("client_reports.renderer.DocxTemplate")
    def test_render_docx_creates_output(self, mock_template_class, sample_context, tmp_path):
        """Test that render_docx creates output file."""
        mock_doc = MagicMock()
        mock_template_class.return_value = mock_doc
        
        with patch.object(Path, "mkdir"):
            with patch("client_reports.renderer.OUTPUT_DIR", tmp_path):
                result = render_docx("test.docx", sample_context)
        
        mock_doc.render.assert_called_once_with(sample_context)
        mock_doc.save.assert_called_once()
    
    @patch("client_reports.renderer.DocxTemplate")
    def test_render_docx_custom_output_name(self, mock_template_class, sample_context, tmp_path):
        """Test render_docx with custom output filename."""
        mock_doc = MagicMock()
        mock_template_class.return_value = mock_doc
        
        with patch.object(Path, "mkdir"):
            with patch("client_reports.renderer.OUTPUT_DIR", tmp_path):
                result = render_docx("test.docx", sample_context, "custom_output.docx")
        
        assert result.name == "custom_output.docx"
    
    @patch("client_reports.renderer.DocxTemplate")
    def test_render_docx_default_output_name(self, mock_template_class, sample_context, tmp_path):
        """Test render_docx generates default output filename."""
        mock_doc = MagicMock()
        mock_template_class.return_value = mock_doc
        
        with patch.object(Path, "mkdir"):
            with patch("client_reports.renderer.OUTPUT_DIR", tmp_path):
                result = render_docx("sample_report.docx", sample_context)
        
        assert result.name == "sample_report_rendered.docx"


class TestSampleData:
    """Tests for sample data files."""
    
    def test_sample_client_json_is_valid(self):
        """Verify sample_client.json is valid JSON."""
        data_file = Path(__file__).resolve().parents[1] / "data" / "sample_client.json"
        
        if data_file.exists():
            with open(data_file, "r") as f:
                data = json.load(f)
            
            assert "client_name" in data
            assert "metrics" in data
            assert isinstance(data["metrics"], list)

