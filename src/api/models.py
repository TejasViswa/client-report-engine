from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Any
from datetime import datetime


class BrandConfig(BaseModel):
    client_id: str
    display_name: str

    primary_color: Optional[str] = None      # hex, e.g. "#004481"
    secondary_color: Optional[str] = None
    font_family: Optional[str] = None        # e.g. "Roboto"
    logo_path: Optional[str] = None          # filled by backend on upload
    website_url: Optional[HttpUrl] = None    # future auto-extract
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MetricItem(BaseModel):
    name: str
    value: str
    change: str
    status: str = "neutral"  # positive, negative, neutral


class RecommendationItem(BaseModel):
    priority: str = "Medium"  # High, Medium, Low
    title: str
    description: str


class ContactInfo(BaseModel):
    name: str
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class ReportRequest(BaseModel):
    """Request body for generating a report."""
    client_id: str
    template_name: str = "sample_report.docx"
    
    # Report content
    report_date: Optional[str] = None
    report_period: Optional[str] = None
    prepared_by: Optional[str] = None
    executive_summary: Optional[str] = None
    
    metrics: list[MetricItem] = Field(default_factory=list)
    highlights: list[str] = Field(default_factory=list)
    recommendations: list[RecommendationItem] = Field(default_factory=list)
    contact: Optional[ContactInfo] = None
    
    # Extra context data (merged with above)
    extra_context: dict[str, Any] = Field(default_factory=dict)
    
    # Output options
    generate_pdf: bool = False
    output_filename: Optional[str] = None


class ReportResponse(BaseModel):
    """Response after generating a report."""
    client_id: str
    docx_path: str
    pdf_path: Optional[str] = None
    generated_at: datetime
    template_used: str
