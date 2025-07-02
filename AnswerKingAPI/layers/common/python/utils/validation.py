import json

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
    missing = [field for field in fields if not data.get(field, '').strip()]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")