from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om.connections import get_redis_connection
from redis_om import HashModel
from starlette.requests import Request
import requests, time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# P.S. I am reusing the same database to not have to pay, since this is just for learning purposes
redis = get_redis_connection(
    host="redis-11104.c85.us-east-1-2.ec2.redns.redis-cloud.com",
    port=11104,
    password="tWzAxNYNPSu0APRMnFHllM7YS0bMB0CI",
    decode_responses=True
)

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str # pending, completed, refunded

    class Meta:
        database = redis

@app.get("/orders/{pk}")
def get(pk: str):
    order = Order.get(pk)
    return order

@app.post("/orders")
async def create(request: Request, background_tasks: BackgroundTasks): # The request will be id and quantity
    body = await request.json()
    req = requests.get('http://localhost:8000/products/%s' % body['id']) # communicate with the inventory service
    product = req.json()

    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.2 * product['price'],
        total=1.2 * product['price'],
        quantity=body['quantity'],
        status='pending'
    )
    order.save()
    background_tasks.add_task(order_completed, order) 
    # This will run in the background by FastAPI, and will not block this post request from returning (it will return pending)
    return order

def order_completed(order: Order):
    time.sleep(5) # Simulate a delay
    order.status = 'completed'
    order.save()
    redis.xadd('order_completed', order.dict(), '*') # This will be sent to the payment service via Redis Streams
    # * for auto generated id