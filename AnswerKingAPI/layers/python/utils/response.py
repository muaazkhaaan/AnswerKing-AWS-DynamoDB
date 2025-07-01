import json

def success_response(status, body_dict):
    return {
        'statusCode': status,
        'body': json.dumps(body_dict)
    }

def error_response(status, message):
    return {
        'statusCode': status,
        'body': json.dumps({'error': message})
    }