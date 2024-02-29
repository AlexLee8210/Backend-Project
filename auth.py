from fastapi import FastAPI, status, Response, Depends, HTTPException
from typing import Union, Annotated
from db.supabase import create_supabase_client
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import User
from jose import JWTError, jwt

SECRET_KEY = "my_key"
ALGORITHM = "HS256"

supabase = create_supabase_client()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(username: str, password: str):
    user: User = supabase.from_("users").select("*").eq("username", username).execute().data[0]
    if not user:
        return False
    if not password == user.password:
        return False
    return user

