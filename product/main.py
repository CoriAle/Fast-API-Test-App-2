from fastapi import FastAPI, status, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing import List
from passlib.context import CryptContext
from . import schemas
from .database import engine, SessionLocal
from . import models

app =  FastAPI(
    title="Products API",
    description="Get Details for all the products in our website",
    terms_of_service="https://google.com",
    contact={
        "email": "test@test.com"
    }
)

crypt_context = CryptContext(schemes=['bcrypt'], deprecated= 'auto')

models.Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/products', response_model= List[schemas.DisplayProduct], tags=['Products'])
def products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return products

@app.get('/product/{id}', response_model= schemas.DisplayProduct, tags=['Products'])
def product(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= 'Product not found')
    return product

@app.delete('/product/{id}', tags=['Products'])
def delete(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).delete(synchronize_session=False)
    db.commit()
    return {'Product removed'}

@app.put('/product/{id}', tags=['Products'])
def update(id: int, request: schemas.Product, db: Session = Depends(get_db)):
    product =  db.query(models.Product).filter(models.Product.id == id)

    if not product.first(): 
        pass
    
    product.update(request.model_dump())
    db.commit()
    return {'Product successfully updated'}


@app.post('/product', status_code=status.HTTP_201_CREATED, tags=['Products'])
def add(request: schemas.Product, db: Session = Depends(get_db)):
    new_product = models.Product(name=request.name, description=request.description, price = request.price, seller_id=1)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return request


@app.post('/seller', response_model=schemas.DisplaySeller, tags=['Seller'])
def create_seller(request: schemas.Seller, db: Session = Depends(get_db)):
    hashed_pwd = crypt_context.hash(request.password)
    new_seller = models.Seller(username=request.username, email=request.email, password= hashed_pwd)
    db.add(new_seller)
    db.commit()
    db.refresh(new_seller)
    return request