from fastapi import status, Response, HTTPException, APIRouter
from typing import Union
from models import User
from db.supabase import create_supabase_client

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

supabase = create_supabase_client()

def user_exists(key: str = "user_id", value: str = None):
    try:
        user = supabase.from_("users").select("*").eq(key, value).execute()
    except: # invalid key
        return False, None
    return (len(user.data) > 0, user)

@router.get("/{user_id}", status_code=status.HTTP_200_OK)
def get_user_profile(user_id: str, response: Response):
    exists, user = user_exists(value=user_id)
    if not exists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "User not found"}
    return user.data[0]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user_profile(req: User, response: Response):
    user_email = req.email.lower()
    exists = user_exists(value=user_email)[0]
    if exists:
        response.status_code = status.HTTP_200_OK
        return {"message": "User already exists"}

    new_user = {"username": req.username, "email": user_email, "password": req.password}
    supabase.from_("users")\
        .insert(new_user)\
        .execute()
    return {"message": "User created successfully"}

@router.put("/{user_id}", status_code=status.HTTP_200_OK)
def update_user_profile(user_id: str, 
                        response: Response,
                        # token: Annotated[str, Depends(oauth2_scheme)],
                        username: Union[str, None] = None, 
                        email: Union[str, None] = None):
    exists, user = user_exists(value=user_id)
    if not exists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "User not found"}
    if email:
        email_exists = user_exists(key="email", value=email)[0]
        if email_exists:
            return {"message": "Email already exists"}
    if username:
        username_exists = user_exists(key="username", value=email)[0]
        if username_exists:
            return {"message": "Username already exists"}
    
    upd_user: User = user.data[0]
    # return upd_user
    if username:
        upd_user["username"] = username
    if email:
        upd_user["email"] = email
    supabase.from_("users")\
        .update(upd_user)\
        .eq("user_id", user_id).execute()
    return {"message": "User updated successfully"}

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_profile(user_id: str, response: Response):
    exists = user_exists(value=user_id)[0]
    if not exists:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"message": "User not found"}

    supabase.from_("users").delete().eq("user_id", user_id).execute()
    return {"message": "User deleted successfully"}
