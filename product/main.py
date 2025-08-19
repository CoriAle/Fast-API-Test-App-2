from fastapi import FastAPI, status, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing import List
from . import schemas
from .database import engine, SessionLocal
from . import models

app =  FastAPI()

models.Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/products', response_model= List[schemas.DisplayProduct])
def products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return products

@app.get('/product/{id}', response_model= schemas.DisplayProduct)
def product(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= 'Product not found')
    return product

@app.delete('/product/{id}')
def delete(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).delete(synchronize_session=False)
    db.commit()
    return {'Product removed'}

@app.put('/product/{id}')
def update(id: int, request: schemas.Product, db: Session = Depends(get_db)):
    product =  db.query(models.Product).filter(models.Product.id == id)

    if not product.first(): 
        pass
    
    product.update(request.model_dump())
    db.commit()
    return {'Product successfully updated'}


@app.post('/product', status_code=status.HTTP_201_CREATED)
def add(request: schemas.Product, db: Session = Depends(get_db)):
    new_product = models.Product(name=request.name, description=request.description, price = request.price)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return request