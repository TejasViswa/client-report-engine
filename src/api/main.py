from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from datetime import datetime

from .models import BrandConfig, ReportRequest, ReportResponse
from .storage import storage
from client_reports import render_docx, docx_to_pdf, PdfConversionError

app = FastAPI(
    title="Client Report Engine API",
    description="Generate professional client reports from templates",
    version="1.0.0",
)

# Static files directory
STATIC_DIR = Path(__file__).parent / "static"
BRANDS_DIR = Path("brands")
BRANDS_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ============ Frontend ============

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    """Serve the web UI."""
    index_path = STATIC_DIR / "index.html"
    return index_path.read_text()


# ============ Brand/Client Endpoints ============

@app.get("/clients", response_model=list[BrandConfig])
def list_clients():
    """List all registered clients."""
    return storage.get_all()


@app.get("/clients/{client_id}", response_model=BrandConfig)
def get_client(client_id: str):
    """Get a client by ID."""
    brand = storage.get(client_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Client not found")
    return brand


@app.post("/clients", response_model=BrandConfig)
def upsert_client(brand: BrandConfig):
    """Create or update a client brand configuration."""
    return storage.upsert(brand)


@app.delete("/clients/{client_id}")
def delete_client(client_id: str):
    """Delete a client."""
    if not storage.delete(client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client deleted", "client_id": client_id}


@app.post("/clients/{client_id}/logo", response_model=BrandConfig)
def upload_logo(client_id: str, file: UploadFile = File(...)):
    """Upload a logo for a client."""
    if not storage.exists(client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    
    ext = Path(file.filename).suffix or ".png"
    logo_path = BRANDS_DIR / f"{client_id}_logo{ext}"
    
    with open(logo_path, "wb") as f:
        f.write(file.file.read())
    
    brand = storage.update_logo(client_id, str(logo_path))
    return brand


# ============ Report Generation Endpoints ============

@app.post("/reports/generate", response_model=ReportResponse)
def generate_report(request: ReportRequest):
    """Generate a report for a client."""
    # Get client brand config
    brand = storage.get(request.client_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Build context from brand + request
    context = {
        "client_name": brand.display_name,
        "report_date": request.report_date or datetime.now().strftime("%B %d, %Y"),
        "report_period": request.report_period or "",
        "prepared_by": request.prepared_by or "",
        "executive_summary": request.executive_summary or "",
        "metrics": [m.model_dump() for m in request.metrics],
        "highlights": request.highlights,
        "recommendations": [r.model_dump() for r in request.recommendations],
        "contact": request.contact.model_dump() if request.contact else {},
        # Brand styling context
        "brand": {
            "primary_color": brand.primary_color,
            "secondary_color": brand.secondary_color,
            "font_family": brand.font_family,
            "logo_path": brand.logo_path,
        },
        # Merge any extra context
        **request.extra_context,
    }
    
    # Generate output filename
    output_name = request.output_filename
    if not output_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"{request.client_id}_report_{timestamp}.docx"
    
    # Render DOCX
    try:
        docx_path = render_docx(request.template_name, context, output_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to render report: {e}")
    
    # Optionally convert to PDF
    pdf_path = None
    if request.generate_pdf:
        try:
            pdf_path = docx_to_pdf(docx_path)
        except PdfConversionError as e:
            raise HTTPException(status_code=500, detail=f"PDF conversion failed: {e}")
    
    return ReportResponse(
        client_id=request.client_id,
        docx_path=str(docx_path),
        pdf_path=str(pdf_path) if pdf_path else None,
        generated_at=datetime.utcnow(),
        template_used=request.template_name,
    )


@app.get("/reports/download/{filename}")
def download_report(filename: str):
    """Download a generated report file."""
    # Check in output directory
    from client_reports import OUTPUT_DIR
    
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")
    
    media_type = "application/pdf" if filename.endswith(".pdf") else \
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type,
    )


@app.get("/templates")
def list_templates():
    """List available report templates."""
    from client_reports import TEMPLATE_DIR
    
    templates = []
    if TEMPLATE_DIR.exists():
        templates = [f.name for f in TEMPLATE_DIR.glob("*.docx")]
    
    return {"templates": templates}


# ============ Health Check ============

@app.get("/health")
def health_check():
    """API health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
