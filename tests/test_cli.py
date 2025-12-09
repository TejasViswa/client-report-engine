"""Tests for the CLI module."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from client_reports.cli import main


class TestCLI:
    """Tests for CLI functionality."""
    
    @pytest.fixture
    def sample_context(self):
        """Sample context data."""
        return {
            "client_name": "Test Corp",
            "report_date": "2025-01-01"
        }
    
    @pytest.fixture
    def mock_json_file(self, tmp_path, sample_context):
        """Create a mock JSON data file."""
        json_file = tmp_path / "data.json"
        json_file.write_text(json.dumps(sample_context))
        return json_file
    
    @patch("client_reports.cli.render_docx")
    @patch("sys.argv", ["cli", "--template", "test.docx", "--data", "data.json"])
    def test_main_docx_only(self, mock_render, sample_context, tmp_path, capsys):
        """Test main function generates DOCX only."""
        mock_render.return_value = tmp_path / "output.docx"
        
        with patch("builtins.open", mock_open(read_data=json.dumps(sample_context))):
            main()
        
        mock_render.assert_called_once()
        captured = capsys.readouterr()
        assert "DOCX generated" in captured.out
    
    @patch("client_reports.cli.docx_to_pdf")
    @patch("client_reports.cli.render_docx")
    @patch("sys.argv", ["cli", "--template", "test.docx", "--data", "data.json", "--pdf"])
    def test_main_with_pdf(self, mock_render, mock_pdf, sample_context, tmp_path, capsys):
        """Test main function with PDF conversion."""
        docx_path = tmp_path / "output.docx"
        pdf_path = tmp_path / "output.pdf"
        mock_render.return_value = docx_path
        mock_pdf.return_value = pdf_path
        
        with patch("builtins.open", mock_open(read_data=json.dumps(sample_context))):
            main()
        
        mock_render.assert_called_once()
        mock_pdf.assert_called_once_with(docx_path)
        captured = capsys.readouterr()
        assert "PDF generated" in captured.out
    
    @patch("client_reports.cli.render_docx")
    @patch("sys.argv", ["cli", "--template", "test.docx", "--data", "data.json", "--docx-out", "custom.docx"])
    def test_main_custom_output(self, mock_render, sample_context, tmp_path):
        """Test main function with custom output filename."""
        mock_render.return_value = tmp_path / "custom.docx"
        
        with patch("builtins.open", mock_open(read_data=json.dumps(sample_context))):
            main()
        
        # Check that custom output name was passed
        call_args = mock_render.call_args
        assert call_args[0][2] == "custom.docx"


class TestCLIArguments:
    """Tests for CLI argument parsing."""
    
    @patch("sys.argv", ["cli"])
    def test_missing_required_args(self):
        """Test that missing required args cause error."""
        with pytest.raises(SystemExit):
            main()
    
    @patch("sys.argv", ["cli", "--template", "test.docx"])
    def test_missing_data_arg(self):
        """Test that missing --data arg causes error."""
        with pytest.raises(SystemExit):
            main()
    
    @patch("sys.argv", ["cli", "--data", "data.json"])
    def test_missing_template_arg(self):
        """Test that missing --template arg causes error."""
        with pytest.raises(SystemExit):
            main()

