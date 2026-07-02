import logging
from datetime import datetime, timedelta
from typing import Optional,List
from fastapi import Depends, HTTPException, Header, status, FastAPI, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
import jwt

from blog_jwt import ALGORITHM

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SECRET_KEY = "SECRET_KEY FOR E-COMMERCE"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#APP INITIALIZATION 

app = FastAPI(title = "E-commerce API",
              description = "API for managing products, cart, orders, and reviews", 
              version = "1.0.0")


# DATA MODELS

class ProductBase(BaseModel):
    name: str = Field(..., example="Sample Product")
    description: Optional[str] = Field(None, example="Product description")
    price: float = Field(..., example=19.99)
    stock: int = Field(..., example=100)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Updated Product Name")
    description: Optional[str] = Field(None, example="Updated Product Description")
    price: Optional[float] = Field(None, example=29.99)
    stock: Optional[int] = Field(None, example=50)

class Product(ProductBase):
    id: int

    model_config = {
        "from_attributes": True
        }

class CartItemCreate(BaseModel):
    product_id: int = Field(..., example=1)
    quantity: int = Field(..., example=2)

class OrderItem(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int

class OrderResponse(BaseModel):
    order_id: int
    items: List[OrderItem]  #Explicitly define list items with a Pydantic schema
    total_price: float
    status: str


class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating must be between 1 and 5", example=5)
    comment: str = Field(..., example="Amazing product! Highly recommend.")

class ReviewResponse(BaseModel):
    review_id: int
    product_id: int
    rating: int
    comment: str

# sIMULATED DATABASES

products_db = {
    1: {"id": 1, "name": "Wireless Mouse", "description": "Ergonomic mouse", "price": 25.99, "stock": 50},
    2: {"id": 2, "name": "Mechanical Keyboard", "description": "RGB Backlit", "price": 89.99, "stock": 20}
}
next_product_id = 3
cart_db = {}
orders_db = {}
next_order_id = 1
reviews_db = {}
next_review_id = 1
    
                    # AUTHENTICATION AND AUTHORIZATION 

def verify_admin(x_role: str = Header(..., description="Simulated role header")):
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return x_role

                             # PRODUCT ENDPOINT

@app.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, x_role: str = Depends(verify_admin)):
    global next_product_id
    new_product = {
        "id": next_product_id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock
    }
    products_db[next_product_id] = new_product
    next_product_id += 1
    return new_product

@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, product: ProductUpdate, x_role: str = Depends(verify_admin)):
    existing_product = products_db.get(product_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    updated_product = existing_product.copy()
    if product.name is not None:
        updated_product["name"] = product.name
    if product.description is not None:
        updated_product["description"] = product.description
    if product.price is not None:
        updated_product["price"] = product.price
    if product.stock is not None:
        updated_product["stock"] = product.stock
    
    products_db[product_id] = updated_product
    return updated_product

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, x_role: str = Depends(verify_admin)):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    del products_db[product_id]
    return None


@app.get("/products", response_model=List[Product])
def get_products():
    logger.debug("Fetching all products")
    return list(products_db.values())

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    logger.debug(f"Fetching product with ID: {product_id}")
    product = products_db.get(product_id)
    if not product:
        logger.error(f"Product with ID {product_id} not found")
        raise HTTPException(status_code=404, detail="Product not found")
    return product

                            # CART ENDPOINTS 

@app.post("/cart/items", status_code=status.HTTP_201_CREATED)
def add_to_cart(item: CartItemCreate):
    product = products_db.get(item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if item.quantity > product["stock"]:
        raise HTTPException(status_code=400, detail="Not enough stock available")
    
    cart_item = {
        "product_id": item.product_id,
        "quantity": item.quantity
    }
    # If already in cart, increment quantity. Otherwise, set it.
    if item.product_id in cart_db:
        # Optional: You'd also want to verify the combined total doesn't exceed stock!
        cart_db[item.product_id] += item.quantity
    else:
        cart_db[item.product_id] = item.quantity

@app.get("/cart")
def get_cart():
    items_list = []
    grand_total = 0.0
    
    # 1. Loop through your flat cart dictionary
    for product_id, quantity in cart_db.items():
        product = products_db.get(product_id)
        
        if product:  # Defensive check in case a product was deleted from DB
            subtotal = product["price"] * quantity
            grand_total += subtotal
            
            # 2. Build the item summary structure
            items_list.append({
                "product_id": product_id,
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity,
                "subtotal": round(subtotal, 2)
            })
            
    # 3. Return everything structured neatly at the root level
    return {
        "items": items_list,
        "grand_total": round(grand_total, 2)
    }

@app.put("/cart/items/{product_id}")
def update_cart_item(product_id: int, quantity: int = Query(..., gt=-1, description="New quantity, 0 removes item")):
    if product_id not in cart_db:
        raise HTTPException(status_code=404, detail="Item not in cart")
    
    if quantity <= 0:
        del cart_db[product_id]  # Drop if zero
    else:
        cart_db[product_id] = quantity  # Overwrites completely
            
    return {"message": "Cart updated"}

@app.delete("/cart/items/{product_id}")
def remove_cart_item(product_id: int):
    if product_id not in cart_db:
        raise HTTPException(status_code=404, detail="Item not in cart")
    del cart_db[product_id]
    return {"message": "Item removed from cart"}
    
                            # ORDER ENDPOINTS 

@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order():
    global next_order_id
    if not cart_db:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    
    for product_id, quantity in cart_db.items():
        product = products_db.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {product_id} no longer exists")
        if product["stock"] < quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product['name']}")

    order_items = []
    total_price = 0.0
    
    for product_id, quantity in cart_db.items():
        product = products_db[product_id]  # Guaranteed to exist now
        subtotal = product["price"] * quantity
        total_price += subtotal
        
        # Deduct inventory safely
        product["stock"] -= quantity
        
        order_items.append({
            "product_id": product_id,
            "name": product["name"],
            "price": product["price"],
            "quantity": quantity
        })
    
    # Save to our simulated database
    new_order = {
        "order_id": next_order_id,
        "items": order_items,
        "total_price": round(total_price, 2),
        "status": "pending"
    }
    orders_db[next_order_id] = new_order
    next_order_id += 1
    
    # Wipe the workspace clean
    cart_db.clear()
    return new_order

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.put("/orders/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: int):
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order["status"] != "pending":
        raise HTTPException(status_code=400, detail="Only pending orders can be canceled")
    
    # Restock the products
    for item in order["items"]:
        product = products_db.get(item["product_id"])
        if product:
            product["stock"] += item["quantity"]
    
    order["status"] = "canceled"
    return order

                            # REVIEW ENDPOINTS

@app.post("/products/{product_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def add_review(product_id: int, review: ReviewCreate):
    global next_review_id
    product = products_db.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    new_review = {
        "review_id": next_review_id,
        "product_id": product_id,
        "rating": review.rating,
        "comment": review.comment
    }
    reviews_db[next_review_id] = new_review
    next_review_id += 1
    return new_review

@app.delete("/products/{product_id}/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(product_id: int, review_id: int, x_role: str = Depends(verify_admin)):
    review = reviews_db.get(review_id)
    if not review or review["product_id"] != product_id:
        raise HTTPException(status_code=404, detail="Review not found for this product")
    
    del reviews_db[review_id]


#Run the application using: uvicorn E-commerce_api:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("E-commerce_api:app", host="127.0.0.1", port=8000, reload = True)


