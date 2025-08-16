from sqlalchemy.orm import Session
from . import models, schemas

def get_brand_by_website_url(db: Session, website_url: str):
    return db.query(models.Brand).filter(models.Brand.website_url == website_url).first()

def create_brand(db: Session, brand: schemas.BrandCreate):
    db_brand = models.Brand(website_url=brand.website_url)
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand

def update_brand(db: Session, db_brand: models.Brand, brand_data: dict):
    for key, value in brand_data.items():
        setattr(db_brand, key, value)
    db.commit()
    db.refresh(db_brand)
    return db_brand