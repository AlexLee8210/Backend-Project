from fastapi import status, Response, Depends, HTTPException, APIRouter
from typing import Union
from models import Product
from db.supabase import create_supabase_client

supabase = create_supabase_client()

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

def product_exists(key: str = "product_id", value: str = None):
    try:
        user = supabase.from_("products").select("*").eq(key, value).execute()
    except: # invalid key
        return False, None
    return (len(user.data) > 0, user)

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_products():
    return supabase.from_("products").select("*").execute().data

@router.get("/search", status_code=status.HTTP_200_OK)
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

@router.get("/{product_id}", status_code=status.HTTP_200_OK)
def get_product(product_id: str, response: Response):
    exists, product = product_exists(value=product_id)
    if not exists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Product not found"}
    return product.data[0]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product_listing(req: Product):
    new_product = {"name": req.name, 
                   "description": req.description, 
                   "price": req.price,
                   "quantity_available": req.quantity_available,
                   "seller_id": req.seller_id}
    supabase.from_("products").insert(new_product).execute()
    return {"message": "Product created"}

@router.put("/{product_id}", status_code=status.HTTP_200_OK)
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

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str, response: Response):
    exists = product_exists(value=product_id)[0]
    if not exists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Product not found"}
    supabase.from_("products").delete().eq("product_id", product_id).execute()
    return {"message": "Product deleted successfully"}

