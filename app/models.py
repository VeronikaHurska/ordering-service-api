class Item:
    def __init__(self, name, price, order_id,number):
        self.id = None
        self.name = name
        self.price = price
        self.order_id = order_id
        self.number = number

    def set_order(self, order):
        self.order = order



class Order:
    def __init__(self, title):
        self.id = None
        self.created_date = None  
        self.updated_date = None
        self.title = title
        
        self.items = []

    def add_item(self, item):
        self.items.append(item)
