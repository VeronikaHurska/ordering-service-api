from app.models import Order, Item
from datetime import datetime
from fastapi import HTTPException

class OrderService:
    @staticmethod
    def create_order(db, title, items):
        new_order = Order(title=title)
        current_timestamp = datetime.utcnow()
        
        
        query = "INSERT INTO orders (title, created_date, updated_date) VALUES (%s, %s, %s) RETURNING id,updated_date;"
        args = (new_order.title, current_timestamp, current_timestamp)

        result = db.execute_query(query, args)
        print("////////////",result,"/////////////")

        new_order.id = result[0][0]
        new_order.updated_date = result[0][1]

        if items:
            for item_data in items:

                item = Item(order_id=new_order.id,name=item_data['name'],price=item_data['price'],number=item_data['number'])
                items_query = "INSERT INTO items (name, price, order_id,number) VALUES (%s, %s, %s,%s) RETURNING id"
                args = (item.name, item.price, item.order_id,item.number) 
                item_result = db.execute_query(items_query, args)
                item.id =  item_result[0][0]
        return new_order


    @staticmethod
    def get_orders(db):
        
        query = """
        SELECT
            o.id,
            o.created_date,
            o.updated_date,
            o.title,
            COALESCE(SUM(i.price), 0) AS total,
            ARRAY_AGG(json_build_object('id',i.id,'name', i.name, 'price', i.price,'number',i.number)) AS items
        FROM orders o
        LEFT JOIN items i ON o.id = i.order_id
        GROUP BY o.id;
        """
        results = db.execute_query(query)
        orders = []
        for order_tuple in results:
            order = {
                "id": order_tuple[0],
                "created_date": order_tuple[1],
                "updated_date": order_tuple[2],
                "title": order_tuple[3],
                "total": order_tuple[4],
                "items": [tuple(order_tuple[5])]
            }
            orders.append(order)

        return orders
    def get_order_by_id(id, db):
        query = f"""
            SELECT orders.*, items.*
            FROM orders
            LEFT JOIN items ON orders.id = items.order_id
            WHERE orders.id = {id};
        """
        result = db.execute_query(query)
        
        
        order_data = {}
        for row in result:
            order_id, created_date, updated_date, title,  item_id, item_order_id, item_name, item_price, item_number = row
            print("&&&&&&&&&&",row)
            if "order" not in order_data:
                order_data["order"] = {
                    "id": order_id,
                    "created_date": created_date,
                    "updated_date": updated_date,
                    "title": title,
                    "items": []
                }
            
            order_data["order"]["items"].append({
                "item_id": item_id,
                "name": item_name,
                "price": float(item_price),
                "number": item_number
            })

        return order_data
    
    def update_order(order_id, db, title, items):
        existing_order = OrderService.get_order_by_id(order_id, db)
        print("00000000000000",existing_order)
        if existing_order is None:
            raise HTTPException(status_code=404, detail="Order not found")

        if title is not None:
            existing_order['title'] = title
            updated_date = datetime.utcnow()
            query = "UPDATE orders SET title=%s,updated_date=%s WHERE id=%s RETURNING id;"
            db.execute_query(query, (title,updated_date, order_id))

            if items is not None:
                
                for item_data in items:
                    item_name = item_data["name"]
                    item_price = item_data["price"]
                    item_number = item_data["number"]

                    insert_item_query = f"INSERT INTO items (order_id, name, price, number) VALUES (%s, %s, %s, %s) RETURNING id;"
                    db.execute_query(insert_item_query, (order_id, item_name, item_price, item_number))


            return True
    def delete_order_by_id(order_id,db):
        db.execute_query("DELETE FROM items WHERE order_id = %s RETURNING id", (order_id,)  )
        db.execute_query("DELETE FROM orders WHERE id = %s RETURNING id;",(order_id,))
        return True 
    def calculate_stats(db):
        query='''

            WITH order_summary AS (
                SELECT
                    o.id AS order_id,
                    SUM(i.price * i.number) AS order_total,
                    COUNT(i.id) AS total_items,
                    SUM(i.number) AS total_ordered_items,
                    MAX(i.name) AS most_ordered_item_name,
                    MAX(i.number) AS most_ordered_item_number
                FROM
                    orders o
                LEFT JOIN
                    items i ON o.id = i.order_id
                GROUP BY
                    o.id
            )
            SELECT
                COUNT(os.order_id) AS total_orders,
                COALESCE(SUM(os.order_total), 0) AS total_order_price,
                COALESCE(AVG(os.order_total), 0) AS avg_order_price,
                COALESCE(SUM(os.total_items), 0) AS total_items,
                COALESCE(AVG(os.total_ordered_items), 0) AS avg_items,
                COALESCE(MAX(os.most_ordered_item_name), '') AS most_ordered_item
            FROM
                order_summary os;

            '''
        results = db.execute_query(query)
        return results


class ItemService():
    def get_item(order_id,item_id,db):
        query='SELECT * FROM items WHERE id = %s'
        return db.execute_query(query,(item_id,))
    def get_items(order_id,db):
        query='SELECT * FROM items WHERE order_id = %s'
        return db.execute_query(query,(order_id,))
    def add_item_to_order(order_id, item_data, db):
        item_name = item_data.get("name")
        item_price = item_data.get("price")
        item_number = item_data.get("number")

        if not (item_name and item_price and item_number):
            raise HTTPException(status_code=400, detail="Invalid item data")

        existing_order = OrderService.get_order_by_id(order_id, db)
        if existing_order is None:
            raise HTTPException(status_code=404, detail="Order not found")

       
        insert_item_query = "INSERT INTO items (order_id, name, price, number) VALUES (%s, %s, %s, %s) RETURNING id;"
        item_result = db.execute_query(insert_item_query, (order_id, item_name, item_price, item_number))
        item_id = item_result[0][0]

        return {"item_id": item_id, "name": item_name, "price": item_price, "number": item_number}
    def update_item(order_id, item_id, item_data, db):
        
        existing_order = OrderService.get_order_by_id(order_id, db)
        if existing_order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        
        
        existing_item = ItemService.get_item(order_id, item_id, db)
        if not existing_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        
        update_query = "UPDATE items SET name=%s, price=%s, number=%s WHERE id=%s AND order_id=%s RETURNING id;"
        update_args = (item_data["name"], item_data["price"], item_data["number"], item_id, order_id)
        db.execute_query(update_query, update_args)
        
        updated_item = {
            "item_id": item_id,
            "name": item_data["name"],
            "price": item_data["price"],
            "number": item_data["number"]
        }
        
        return updated_item
    def delete_item(item_id,db):
        return db.execute_query("DELETE FROM items WHERE id = %s RETURNING id;",(item_id,))
