# app/models.py

from sqlalchemy import Column, Integer, String, JSON, Text
from .database import Base

class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    website_url = Column(String(255), unique=True, index=True)
    product_catalog = Column(JSON)
    hero_products = Column(JSON)
    privacy_policy = Column(Text) 
    return_policy = Column(Text) 
    faqs = Column(JSON)
    social_handles = Column(JSON)
    contact_details = Column(JSON)
    brand_context = Column(Text)
    important_links = Column(JSON)