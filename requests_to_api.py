import requests


url = "http://0.0.0.0:8080/orders"


order_data = {
    "title": "New Order",
    "items": [
        {
            "id": 1,
            "name": "Item 1",
            "price": 10.99,
            "number": 2
        },
        {
            "id": 2,
            "name": "Item 2",
            "price": 5.99,
            "number": 3
        }
    ]
}


# Send the POST request
response = requests.post(url, json=order_data)
# resp=requests.get(url)
# Print the response
# print("Get:",resp)
print("-----------------------")
print("Post:", response.status_code, response.json())
 