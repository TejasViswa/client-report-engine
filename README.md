# Client Report Engine

A Python tool for generating professional client reports from DOCX templates with JSON data. Includes a FastAPI REST API for managing clients and generating reports programmatically.

## Features

- **Template-based reports**: Use Jinja2 templating syntax in DOCX files
- **JSON data input**: Feed structured data to populate templates
- **Cross-platform PDF conversion**: Supports LibreOffice (all platforms) and docx2pdf (Windows/macOS)
- **CLI interface**: Easy command-line usage for automation
- **REST API**: FastAPI-based API for client management and report generation
- **Brand Management**: Store client brand configs (colors, fonts, logos)
- **Programmatic API**: Import and use in your Python projects

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/client_report_engine.git
cd client_report_engine

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### PDF Conversion Requirements

For PDF generation, you need one of:

- **LibreOffice** (recommended, cross-platform): Install from [libreoffice.org](https://www.libreoffice.org/) and ensure `soffice` is on your PATH
- **docx2pdf** (Windows/macOS only): Requires Microsoft Word installed

## Quick Start

### 1. Create a Template

First, generate a sample template:

```bash
python scripts/create_sample_template.py
```

This creates `reports/templates/sample_report.docx` with Jinja2 placeholders.

### 2. Prepare Your Data

Create a JSON file with your report data (see `data/sample_client.json` for an example):

```json
{
    "client_name": "Acme Corporation",
    "report_date": "December 9, 2025",
    "metrics": [
        {"name": "Revenue", "value": "$2.4M", "change": "+12%"}
    ],
    "highlights": ["Launched new product", "Achieved 99.9% uptime"]
}
```

### 3. Generate Report

```bash
# Generate DOCX only
client-report --template sample_report.docx --data data/sample_client.json

# Generate DOCX and convert to PDF
client-report --template sample_report.docx --data data/sample_client.json --pdf

# Custom output filename
client-report --template sample_report.docx --data data/sample_client.json --docx-out my_report.docx
```

## Template Syntax

Templates use [Jinja2 syntax](https://jinja.palletsprojects.com/) within DOCX files:

### Variables

```
{{ client_name }}
{{ report_date }}
{{ contact.email }}
```

### Loops

```
{% for metric in metrics %}
• {{ metric.name }}: {{ metric.value }}
{% endfor %}
```

### Conditionals

```
{% if status == "positive" %}
✓ On Track
{% else %}
✗ Needs Attention
{% endif %}
```

## Programmatic Usage

```python
from client_reports import render_docx, docx_to_pdf

# Render a report
context = {
    "client_name": "Acme Corp",
    "report_date": "2025-12-09",
    "metrics": [{"name": "Revenue", "value": "$1M"}]
}

docx_path = render_docx("sample_report.docx", context)
print(f"DOCX created: {docx_path}")

# Convert to PDF
pdf_path = docx_to_pdf(docx_path)
print(f"PDF created: {pdf_path}")
```

## REST API & Web UI

Start the server:

```bash
cd src
uvicorn api.main:app --reload
```

- **Web UI**: `http://localhost:8000` - Beautiful dashboard for managing clients and generating reports
- **API Docs**: `http://localhost:8000/docs` - Interactive Swagger documentation

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/clients` | List all clients |
| POST | `/clients` | Create/update client |
| GET | `/clients/{id}` | Get client by ID |
| DELETE | `/clients/{id}` | Delete client |
| POST | `/clients/{id}/logo` | Upload client logo |
| GET | `/templates` | List available templates |
| POST | `/reports/generate` | Generate a report |
| GET | `/reports/download/{filename}` | Download generated report |

### Example: Create Client & Generate Report

```bash
# Create a client
curl -X POST http://localhost:8000/clients \
  -H "Content-Type: application/json" \
  -d '{"client_id": "acme", "display_name": "Acme Corp", "primary_color": "#004481"}'

# Generate a report
curl -X POST http://localhost:8000/reports/generate \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "acme",
    "report_date": "December 9, 2025",
    "executive_summary": "Q4 performance review",
    "metrics": [{"name": "Revenue", "value": "$2.4M", "change": "+12%", "status": "positive"}],
    "highlights": ["Launched new product", "Expanded to EU"],
    "generate_pdf": true
  }'
```

## Project Structure

```
client_report_engine/
├── data/                       # Sample data files
│   ├── sample_client.json
│   └── brands.json             # Client brand storage
├── brands/                     # Uploaded client logos
├── reports/
│   ├── templates/              # DOCX templates
│   └── output/                 # Generated reports
├── scripts/
│   └── create_sample_template.py
├── src/
│   ├── api/                    # FastAPI REST API
│   │   ├── __init__.py
│   │   ├── main.py             # API endpoints
│   │   ├── models.py           # Pydantic models
│   │   ├── storage.py          # Brand persistence
│   │   └── static/             # Web UI frontend
│   │       ├── index.html
│   │       ├── styles.css
│   │       └── app.js
│   └── client_reports/         # Core report engine
│       ├── __init__.py
│       ├── cli.py              # Command-line interface
│       ├── pdf.py              # PDF conversion
│       └── renderer.py         # DOCX rendering
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_cli.py
│   ├── test_pdf.py
│   └── test_renderer.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## CLI Reference

```
usage: client-report [-h] --template TEMPLATE --data DATA [--docx-out DOCX_OUT] [--pdf]

Generate client reports from templates.

options:
  -h, --help           show this help message and exit
  --template TEMPLATE  Template DOCX file name, e.g. sample_report.docx
  --data DATA          JSON file with context data
  --docx-out DOCX_OUT  Output DOCX filename
  --pdf                Also convert to PDF
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/client_reports --cov-report=html

# Run specific test file
pytest tests/test_renderer.py -v
```

## API Reference

### `render_docx(template_name, context, output_name=None)`

Render a DOCX report from a template.

- **template_name**: Name of template file in `reports/templates/`
- **context**: Dictionary of data to populate the template
- **output_name**: Optional custom output filename
- **Returns**: Path to generated DOCX file

### `docx_to_pdf(input_path, output_path=None)`

Convert a DOCX file to PDF.

- **input_path**: Path to DOCX file
- **output_path**: Optional custom PDF output path
- **Returns**: Path to generated PDF file
- **Raises**: `PdfConversionError` if conversion fails

## License

MIT License - see LICENSE file for details.

