from fastapi import APIRouter, status, Response, Depends, HTTPException
from typing import Union, Annotated
from db.supabase import create_supabase_client
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import Token, User

supabase = create_supabase_client()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/token")
def token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    try:
        data = supabase.auth.sign_in_with_password({"email": form_data.username, "password": form_data.password})
        if not data:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = data.session.access_token
        return {"access_token": access_token, "token_type": "bearer"}
    except:
        return {"message": "Could not authenticate user"}

@router.get("/get_current_user")
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    decoded_token = supabase.auth._decode_jwt(token)
    user = supabase.from_("users").select("*").eq("user_id", decoded_token["sub"]).execute()
    return user.data[0]
