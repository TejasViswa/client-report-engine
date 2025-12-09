"""Tests for the FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import json

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from api.main import app
from api.models import BrandConfig
from api.storage import BrandStorage


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def temp_storage(tmp_path):
    """Create temporary storage for tests."""
    storage_path = tmp_path / "test_brands.json"
    return BrandStorage(storage_path)


@pytest.fixture
def sample_brand():
    """Sample brand configuration."""
    return {
        "client_id": "test_corp",
        "display_name": "Test Corporation",
        "primary_color": "#004481",
        "secondary_color": "#ffffff",
        "font_family": "Roboto",
    }


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestClientEndpoints:
    """Tests for client/brand management endpoints."""
    
    def test_create_client(self, client, sample_brand):
        """Test creating a new client."""
        response = client.post("/clients", json=sample_brand)
        assert response.status_code == 200
        data = response.json()
        assert data["client_id"] == sample_brand["client_id"]
        assert data["display_name"] == sample_brand["display_name"]
    
    def test_get_client_not_found(self, client):
        """Test getting non-existent client returns 404."""
        response = client.get("/clients/nonexistent")
        assert response.status_code == 404
    
    def test_list_clients(self, client, sample_brand):
        """Test listing all clients."""
        # Create a client first
        client.post("/clients", json=sample_brand)
        
        response = client.get("/clients")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_delete_client_not_found(self, client):
        """Test deleting non-existent client returns 404."""
        response = client.delete("/clients/nonexistent")
        assert response.status_code == 404


class TestLogoUpload:
    """Tests for logo upload endpoint."""
    
    def test_upload_logo_client_not_found(self, client):
        """Test uploading logo for non-existent client returns 404."""
        # Create a fake file
        files = {"file": ("logo.png", b"fake image content", "image/png")}
        response = client.post("/clients/nonexistent/logo", files=files)
        assert response.status_code == 404


class TestTemplatesEndpoint:
    """Tests for templates listing."""
    
    def test_list_templates(self, client):
        """Test listing available templates."""
        response = client.get("/templates")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert isinstance(data["templates"], list)


class TestReportGeneration:
    """Tests for report generation endpoint."""
    
    @patch("api.main.render_docx")
    def test_generate_report_client_not_found(self, mock_render, client):
        """Test generating report for non-existent client returns 404."""
        request_data = {
            "client_id": "nonexistent",
            "template_name": "sample_report.docx",
        }
        response = client.post("/reports/generate", json=request_data)
        assert response.status_code == 404
    
    def test_download_report_not_found(self, client):
        """Test downloading non-existent report returns 404."""
        response = client.get("/reports/download/nonexistent.docx")
        assert response.status_code == 404


class TestBrandStorage:
    """Tests for BrandStorage class."""
    
    def test_create_and_get(self, temp_storage, sample_brand):
        """Test creating and retrieving a brand."""
        brand = BrandConfig(**sample_brand)
        saved = temp_storage.upsert(brand)
        
        assert saved.client_id == brand.client_id
        assert saved.created_at is not None
        
        retrieved = temp_storage.get(brand.client_id)
        assert retrieved is not None
        assert retrieved.display_name == brand.display_name
    
    def test_update_existing(self, temp_storage, sample_brand):
        """Test updating an existing brand."""
        brand = BrandConfig(**sample_brand)
        temp_storage.upsert(brand)
        
        # Update
        updated_brand = BrandConfig(
            client_id=sample_brand["client_id"],
            display_name="Updated Name",
        )
        saved = temp_storage.upsert(updated_brand)
        
        assert saved.display_name == "Updated Name"
        assert saved.created_at is not None  # preserved
        assert saved.updated_at is not None
    
    def test_delete(self, temp_storage, sample_brand):
        """Test deleting a brand."""
        brand = BrandConfig(**sample_brand)
        temp_storage.upsert(brand)
        
        assert temp_storage.delete(brand.client_id) is True
        assert temp_storage.get(brand.client_id) is None
    
    def test_delete_nonexistent(self, temp_storage):
        """Test deleting non-existent brand returns False."""
        assert temp_storage.delete("nonexistent") is False
    
    def test_get_all(self, temp_storage):
        """Test getting all brands."""
        brand1 = BrandConfig(client_id="corp1", display_name="Corp 1")
        brand2 = BrandConfig(client_id="corp2", display_name="Corp 2")
        
        temp_storage.upsert(brand1)
        temp_storage.upsert(brand2)
        
        all_brands = temp_storage.get_all()
        assert len(all_brands) == 2
    
    def test_update_logo(self, temp_storage, sample_brand):
        """Test updating logo path."""
        brand = BrandConfig(**sample_brand)
        temp_storage.upsert(brand)
        
        updated = temp_storage.update_logo(brand.client_id, "/path/to/logo.png")
        assert updated.logo_path == "/path/to/logo.png"
    
    def test_persistence(self, tmp_path, sample_brand):
        """Test that data persists across storage instances."""
        storage_path = tmp_path / "persist_test.json"
        
        # Create and save
        storage1 = BrandStorage(storage_path)
        brand = BrandConfig(**sample_brand)
        storage1.upsert(brand)
        
        # Load in new instance
        storage2 = BrandStorage(storage_path)
        retrieved = storage2.get(brand.client_id)
        
        assert retrieved is not None
        assert retrieved.display_name == brand.display_name

