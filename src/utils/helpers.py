from fastapi import HTTPException, Request,Depends
from src.user.models import UserModel
import jwt
from src.utils.settings import settings
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from src.utils.db import get_db


def is_authenticated(request: Request, db: Session=Depends(get_db)):
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