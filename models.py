from pydantic import BaseModel

# SCHEMAS
class User (BaseModel):
    user_id: str
    username: str
    email: str
    password: str

class Product (BaseModel):
    name: str
    description: str
    price: float
    quantity_available: int
    seller_id: str

class Token (BaseModel):
    access_token: str
    token_type: str
