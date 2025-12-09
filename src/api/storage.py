"""
Persistent storage for brand configurations.
Uses JSON file storage for simplicity - can be swapped for a database.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from .models import BrandConfig


class BrandStorage:
    """JSON file-based storage for brand configurations."""
    
    def __init__(self, storage_path: str | Path = "data/brands.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, BrandConfig] = {}
        self._load()
    
    def _load(self) -> None:
        """Load brands from JSON file."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._cache = {
                    k: BrandConfig(**v) for k, v in data.items()
                }
            except (json.JSONDecodeError, Exception):
                self._cache = {}
        else:
            self._cache = {}
    
    def _save(self) -> None:
        """Persist brands to JSON file."""
        data = {k: v.model_dump(mode="json") for k, v in self._cache.items()}
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
    
    def get(self, client_id: str) -> Optional[BrandConfig]:
        """Get a brand by client_id."""
        return self._cache.get(client_id)
    
    def get_all(self) -> list[BrandConfig]:
        """Get all brands."""
        return list(self._cache.values())
    
    def upsert(self, brand: BrandConfig) -> BrandConfig:
        """Create or update a brand configuration."""
        now = datetime.utcnow()
        
        existing = self._cache.get(brand.client_id)
        if existing:
            # Update: preserve created_at, update updated_at
            brand = brand.model_copy(update={
                "created_at": existing.created_at,
                "updated_at": now,
            })
        else:
            # Create: set both timestamps
            brand = brand.model_copy(update={
                "created_at": now,
                "updated_at": now,
            })
        
        self._cache[brand.client_id] = brand
        self._save()
        return brand
    
    def update_logo(self, client_id: str, logo_path: str) -> Optional[BrandConfig]:
        """Update the logo path for a client."""
        brand = self._cache.get(client_id)
        if brand:
            brand = brand.model_copy(update={
                "logo_path": logo_path,
                "updated_at": datetime.utcnow(),
            })
            self._cache[client_id] = brand
            self._save()
        return brand
    
    def delete(self, client_id: str) -> bool:
        """Delete a brand configuration."""
        if client_id in self._cache:
            del self._cache[client_id]
            self._save()
            return True
        return False
    
    def exists(self, client_id: str) -> bool:
        """Check if a client exists."""
        return client_id in self._cache


# Global storage instance
storage = BrandStorage()

