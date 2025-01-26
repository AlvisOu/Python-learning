from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om.connections import get_redis_connection
from redis_om import HashModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Redis connection
redis = get_redis_connection(
    host="redis-11104.c85.us-east-1-2.ec2.redns.redis-cloud.com",
    port=11104,
    password="tWzAxNYNPSu0APRMnFHllM7YS0bMB0CI",
    decode_responses=True
)

class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis

@app.get("/products")
def all():
    return [format(pk) for pk in Product.all_pks()]

def format(pk: str):
    product = Product.get(pk)
    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity
    }

@app.post("/products")
def create(product: Product):
    try:
        print(redis.ping())
        product.save()
        return product
    except Exception as e:
        return str(e)
    
@app.get("/products/{pk}")
def get(pk: str):
    return Product.get(pk)

@app.delete("/products/{pk}")
def delete(pk: str):
    return Product.delete(pk)