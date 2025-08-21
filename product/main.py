from fastapi import FastAPI
from .database import engine
from . import models
from .routers import product, seller, login

app =  FastAPI(
    title="Products API",
    description="Get Details for all the products in our website",
    terms_of_service="https://google.com",
    contact={
        "email": "test@test.com"
    },
)

app.include_router(product.router)
app.include_router(seller.router)
app.include_router(login.router)

models.Base.metadata.create_all(engine)

