from fastapi import APIRouter, status, Response, Depends, HTTPException
from typing import Union, Annotated
from db.supabase import create_supabase_client
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import Token
from jose import JWTError, jwt

SECRET_KEY = "my_key"
ALGORITHM = "HS256"

supabase = create_supabase_client()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/token", response_model=Token)
def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends(oauth2_scheme)]):
    print("iojoiasios")
    try:
        print("oiaisj")
        data = supabase.auth.sign_in_with_password({"email": form_data.username, "password": form_data.password})
        # data = supabase.auth.sign_in_with_password({"email": "user2@email.com", "password": "a"})
        print(data)
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
    
# @router.get("/get_current_user")
# def get_current_user(token: Annotated[str, Depends(token)]):
#     try:
#         payload = decode_access_token(token)
#         username = payload.get("username")
#     except JWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     user = supabase.from_("users").select("*").eq("username", username).execute()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return user

# def authenticate_user(username: str, password: str):
#     user: User = supabase.from_("users").select("*").eq("username", username).execute().data[0]
#     if not user:
#         return False
#     if not password == user.password:
#         return False
#     return user

