from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, utils, auth
from ..database import get_db
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=schemas.ShowUser)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_pwd = utils.hash_password(user.password)
    new_user = models.User(username=user.username, email=user.email, password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# @router.post("/login")
# def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.username == form_data.username).first()
#     if not user or not utils.verify_password(form_data.password, user.password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     token = auth.create_access_token({"sub": user.username})
#     return {"access_token": token, "token_type": "bearer"}

@router.post("/login")
def login(data: schemas.LoginRequest, db:Session =Depends(get_db)):
    user = db.query(models.User).filter(models.User.username==data.username).first()
    if not user or not utils.verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid Credentials")
    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token,
           "token_type": "bearer", 
           "login_type_received": data.login_type}