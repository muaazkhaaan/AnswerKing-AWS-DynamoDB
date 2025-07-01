def get_path_param(event, key):
    value = event.get('pathParameters', {}).get(key, '').strip()
    if not value:
        raise ValueError(f"Missing {key}")
    return value