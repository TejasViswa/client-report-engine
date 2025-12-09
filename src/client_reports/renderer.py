from pathlib import Path
from docxtpl import DocxTemplate


BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = BASE_DIR / "reports" / "templates"
OUTPUT_DIR = BASE_DIR / "reports" / "output"


def render_docx(template_name: str, context: dict, output_name: str | None = None) -> Path:
    """
    Render a DOCX report from a template and context data.
    """
    template_path = TEMPLATE_DIR / template_name
    if output_name is None:
        output_name = template_name.replace(".docx", "_rendered.docx")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / output_name

    doc = DocxTemplate(template_path)
    doc.render(context)
    doc.save(output_path)
    return output_path
