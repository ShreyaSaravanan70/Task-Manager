
from fastapi import HTTPException,status,Request
from src.user.dtos import UserSchema,LoginSchema
from sqlalchemy.orm import Session
from src.user.models import UserModel
from pwdlib import PasswordHash
from sentence_transformers import SentenceTransformer
import jwt
from src.utils.settings import settings
from datetime import datetime,timedelta
from jwt.exceptions import InvalidTokenError
from src.generate_embeddings import get_embedding

password_hash = PasswordHash.recommended()

def get_password_hash(password):
    return password_hash.hash(password)

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def register(body:UserSchema, db:Session):
    is_user=db.query(UserModel).filter(UserModel.username==body.username).first()
    if is_user:
        raise HTTPException(status_code=400, detail="Username already exists..")
    
    is_user=db.query(UserModel).filter(UserModel.email==body.email).first()
    if is_user:
        raise HTTPException(status_code=400, detail="Email Address already exists..")
    
    hash_password= get_password_hash(body.password)

     # Create text for embedding
    text = f"{body.name} {body.username} {body.email}"

    embedding=get_embedding(text)

    new_user=UserModel(name=body.name,
                       username=body.username,
                       hash_password=hash_password,
                       email=body.email,
                       embedding=embedding
                       )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(body:LoginSchema, db=Session):
    user=db.query(UserModel).filter(UserModel.username==body.username).first()
    if not user:
        raise HTTPException(401, detail="Incorrect Username/Password..")

    if not verify_password(body.password,user.hash_password):
        raise HTTPException(401, detail="Incorrect Username/Password..")
    
    exp_time= datetime.now() + timedelta(minutes=settings.EXP_TIME)
    
    token=jwt.encode({"_id":user.id, "exp":exp_time.timestamp()}, settings.SECRET_KEY, settings.ALGORITHM)

    return{"token":token}

def is_authenticated(request: Request, db: Session):
    try:
        token=request.headers.get("authorization")
        if not token:
            raise HTTPException(401, detail="You are unnathorized")
        token=token.split(" ")[-1]

        data= jwt.decode(token,settings.SECRET_KEY, settings.ALGORITHM)
        user_id=data.get("_id")
        # exp_time=int(data.get("exp"))

        # current_time=datetime.now().timestamp()
        # if current_time > exp_time:
        #     raise HTTPException(401, detail="You are unnathorized")
        
        user=db.query(UserModel).filter(UserModel.id==user_id).first()
        if not user:
            raise HTTPException(401, detail="You are unnathorized")
        
        return user
    except InvalidTokenError:
        raise HTTPException(401, detail="You are unnathorized")