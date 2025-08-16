from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas, services
from .database import SessionLocal, engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/fetch-brand-data/", response_model=schemas.Brand)
def fetch_brand_data(brand: schemas.BrandCreate, db: Session = Depends(get_db)):
    db_brand = crud.get_brand_by_website_url(db, website_url=brand.website_url)
    if not db_brand:
        db_brand = crud.create_brand(db=db, brand=brand)

    brand_data = services.get_brand_data(brand.website_url)
    if not brand_data:
        raise HTTPException(status_code=404, detail="Website not found")

    updated_brand = crud.update_brand(db=db, db_brand=db_brand, brand_data=brand_data)
    return updated_brand