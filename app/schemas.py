# app/schemas.py

from pydantic import BaseModel
from typing import List, Dict, Optional

class BrandBase(BaseModel):
    website_url: str

class BrandCreate(BrandBase):
    pass

class Brand(BrandBase):
    id: int
    product_catalog: Optional[List[Dict]] = None
    hero_products: Optional[List[Dict]] = None
    privacy_policy: Optional[str] = None
    return_policy: Optional[str] = None
    faqs: Optional[List[Dict]] = None
    social_handles: Optional[Dict[str, str]] = None
    contact_details: Optional[Dict[str, str]] = None
    brand_context: Optional[str] = None
    important_links: Optional[Dict[str, str]] = None

    class Config:
        from_attributes = True