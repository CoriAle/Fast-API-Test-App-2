from fastapi import FastAPI
from . import schemas
from .database import engine
from . import models

app =  FastAPI()

models.Base.metadata.create_all(engine)

@app.post('/product')
def add(product: schemas.Product):
    return product