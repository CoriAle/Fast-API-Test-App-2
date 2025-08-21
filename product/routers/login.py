from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from .. import schemas, models
from ..database import get_db

SECRET_KEY = '5a0551332edcbaca752950b6ae120c4d8f15c74536b1cfff200333a5d2b12640'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 20

oauth2_schema  = OAuth2PasswordBearer(tokenUrl='login')


def generate_token(data: dict):
    to_encode = data.copy()
    expiration = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expiration})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


router=APIRouter(
    tags=['Login']
)

crypt_context = CryptContext(schemes=['bcrypt'], deprecated= 'auto')

@router.post('/login', response_model=schemas.Token)
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print(request)
    seller = db.query(models.Seller).filter(models.Seller.username == request.username).first()

    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail ='User name not found or is not valid')
    elif not crypt_context.verify(request.password, seller.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Provided password is not valid')
    access_token = generate_token(data={'sub': seller.username})
    return schemas.Token(access_token= access_token, token_type= 'bearer')

def get_current_user(token: str = Depends(oauth2_schema)):
    credentials_expection = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid auth credentials', headers={'WWW-Authenticate': 'Bearer'})
    try:
        payload = jwt.decode(token,  SECRET_KEY, algorithms=[ALGORITHM])
        username:str = payload.get('sub')
        if username is None:
            raise credentials_expection
        token_data = schemas.TokenData(username=username)
        return token_data
    except JWTError:
        raise credentials_expection

