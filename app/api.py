from fastapi import FastAPI, HTTPException, APIRouter, Path
from app.database import db
from app.models import Order, Item
from app.services import OrderService,ItemService

app = FastAPI()
router = APIRouter()

@router.get('/orders')
async def get_all_orders():
    return OrderService.get_orders(db)

@router.post("/orders", response_model=int)
async def create_new_order(order_data: dict):
    OrderService.create_order(db, order_data["title"], order_data["items"])
    return 201

@router.get('/orders/{order_id}')
async def get_order_by_id(order_id: int):
    order_data = OrderService.get_order_by_id(order_id, db)
    if order_data:
        return order_data
    else:
        raise HTTPException(status_code=404, detail="Order not found")

@router.put('/orders/{order_id}')
async def update_order(order_id: int, data:dict):
    updated_order = OrderService.update_order(order_id=order_id, db=db, title= data.get('title'),items=data.get('items'))
    if updated_order:
        return {"message": "Order updated"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update order")

@router.delete('/orders/{order_id}')
async def delete_order(order_id:int):
    OrderService.delete_order_by_id(order_id=order_id,db=db)
    return {"message": "Order deleted"}

@router.get('/stats')
async def get_stats():
    results=OrderService.calculate_stats(db=db)
    return results 

@router.get('/orders/{order_id}/items/{item_id}')
async def get_item_by_id(item_id:int, order_id:int):
    return ItemService.get_item(order_id=order_id,item_id=item_id,db=db)


@router.get('/orders/{order_id}/items')
async def get_items(order_id):
    return ItemService.get_items(order_id=order_id,db=db)

@router.post('/orders/{order_id}/items')
async def add_item( order_id:int,item_data:dict):
    ItemService.add_item_to_order(order_id,item_data=item_data,db=db)
    return True

@router.put('/orders/{order_id}/items/{item_id}')
async def update_item(order_id:int,item_id:int,item_data:dict):

    return ItemService.update_item(order_id,item_id,item_data,db)

@router.delete('/orders/{order_id}/items/{item_id}')
async def delete_item(item_id:int):
    return ItemService.delete_item(item_id,db)