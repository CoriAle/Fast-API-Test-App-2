from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .. import schemas
from ..database import get_db
from .. import models


router = APIRouter(
    tags=['Seller'],
    prefix='/seller',
)

crypt_context = CryptContext(schemes=['bcrypt'], deprecated= 'auto')


@router.post('/', response_model=schemas.DisplaySeller)
def create_seller(request: schemas.Seller, db: Session = Depends(get_db)):
    hashed_pwd = crypt_context.hash(request.password)
    new_seller = models.Seller(username=request.username, email=request.email, password= hashed_pwd)
    db.add(new_seller)
    db.commit()
    db.refresh(new_seller)
    return request