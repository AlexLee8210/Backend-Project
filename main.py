from fastapi import FastAPI, status, Response, Depends, HTTPException
from typing import Union, Annotated
from db.supabase import create_supabase_client
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import User, Product, Token
from jose import JWTError, jwt
# from auth import authenticate_user, create_access_token, decode_access_token

app = FastAPI()
supabase = create_supabase_client()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# HELPERS

def exists(table: str, key: str, value: str = None):
    try:
        user = supabase.from_(table).select("*").eq(key, value).execute()
    except: # invalid key
        return False, None
    return (len(user.data) > 0, user)

def user_exists(key: str = "user_id", value: str = None):
    return exists("users", key, value)

def product_exists(key: str = "product_id", value: str = None):
    return exists("products", key, value)

# USER API ENDPOINTS
@app.get("/user/{user_id}", status_code=status.HTTP_200_OK, tags=["users"])
def get_user_profile(user_id: str, response: Response):
    exists, user = user_exists(value=user_id)
    if not exists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "User not found"}
    return user.data[0]

@app.post("/users", status_code=status.HTTP_201_CREATED, tags=["users"])
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

@app.put("/users/{user_id}", status_code=status.HTTP_200_OK, tags=["users"])
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

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["users"])
def delete_user_profile(user_id: str, response: Response):
    exists = user_exists(value=user_id)[0]
    if not exists:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"message": "User not found"}

    supabase.from_("users").delete().eq("user_id", user_id).execute()
    return {"message": "User deleted successfully"}

@app.get("/products", status_code=status.HTTP_200_OK, tags=["products"])
def get_all_products():
    return supabase.from_("products").select("*").execute().data

@app.get("/products/search", status_code=status.HTTP_200_OK, tags=["products"])
def search_products(q: Union[str, None]=None,
                    min_price: Union[float, None]=None,
                    max_price: Union[float, None]=None):
    query = supabase.from_("products").select("*")
    if q:
        query = query.ilike("name", f"%{q}%")
    if min_price:
        query = query.gte("price", min_price)
    if max_price:
        query = query.lte("price", max_price)
    res = query.execute()
    return res.data

@app.get("/products/{product_id}", status_code=status.HTTP_200_OK, tags=["products"])
def get_product(product_id: str, response: Response):
    exists, product = product_exists(value=product_id)
    if not exists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Product not found"}
    return product.data[0]

@app.post("/products", status_code=status.HTTP_201_CREATED, tags=["products"])
def create_product_listing(req: Product):
    new_product = {"name": req.name, 
                   "description": req.description, 
                   "price": req.price,
                   "quantity_available": req.quantity_available,
                   "seller_id": req.seller_id}
    supabase.from_("products").insert(new_product).execute()
    return {"message": "Product created"}

@app.put("/products/{product_id}", status_code=status.HTTP_200_OK, tags=["products"])
def update_product(product_id: str, response: Response,
                   name: Union[str, None] = None, description: Union[str, None] = None,
                   price: Union[float, None] = None, quantity_available: Union[int, None] = None):
    exists, product = product_exists(value=product_id)
    if not exists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Product not found"}
    new_product: Product = product.data[0]
    if name:
        new_product["name"] = name
    if description:
        new_product["description"] = description
    if price:
        new_product["price"] = price
    if quantity_available:
        new_product["quantity_available"] = quantity_available
    supabase.from_("products").update(new_product)\
        .eq("product_id", product_id).execute()
    return {"message": "Product updated"}

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["products"])
def delete_product(product_id: str, response: Response):
    exists = product_exists(value=product_id)[0]
    if not exists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Product not found"}
    supabase.from_("products").delete().eq("product_id", product_id).execute()
    return {"message": "Product deleted successfully"}

@app.post("/auth/token", response_model=Token, tags=["auth"])
def token(form_data: OAuth2PasswordRequestForm = Depends(oauth2_scheme)):
    try:
        # data = supabase.auth.sign_in_with_password({"email": form_data.username, "password": form_data.password})
        data = supabase.auth.sign_in_with_password({"email": "user2@email.com", "password": "a"})

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
    
@app.get("/auth/get_current_user", tags=["auth"])
def get_current_user(token: Annotated[str, Depends(token)]):
    try:
        payload = decode_access_token(token)
        username = payload.get("username")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = supabase.from_("users").select("*").eq("username", username).execute()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user