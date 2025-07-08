import json
import re
from decimal import Decimal

def get_path_param(event, key):
    value = event.get('pathParameters', {}).get(key, '').strip()
    if not value:
        raise ValueError(f"Missing or invalid {key}")
    return value

def parse_body(event):
    try:
        return json.loads(event.get('body', '{}'))
    except Exception as e:
        print(f"JSON decode error: {e}")
        raise ValueError("Invalid JSON body")

def require_fields(data, fields):
    missing = [
        field for field in fields 
        if field not in data 
        or (isinstance(data[field], str) and data[field].strip() == '') 
        or (not isinstance(data[field], str) and not data[field])
    ]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

def validate_price(price):
    if not re.match(r'^\d+(\.\d{2})$', str(price)):
        raise ValueError("Price must be a number with exactly 2 decimal places (e.g., 12.99)")
    try:
        return Decimal(str(price))
    except:
        raise ValueError("Invalid price format")
    
def validate_order_entry(entry):
    item_id = entry.get('itemID')
    quantity = entry.get('quantity')

    if not item_id or quantity is None or quantity <= 0:
        raise ValueError('Each order item must include itemID and quantity > 0')
