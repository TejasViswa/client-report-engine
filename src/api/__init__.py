"""
FastAPI-based REST API for the Client Report Engine.
"""

from .main import app
from .models import BrandConfig, ReportRequest, ReportResponse
from .storage import BrandStorage

__all__ = ["app", "BrandConfig", "ReportRequest", "ReportResponse", "BrandStorage"]

