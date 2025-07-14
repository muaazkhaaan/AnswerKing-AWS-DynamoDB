import boto3
import uuid
from utils.response import success_response, error_response, handle_exception
from utils.validation import parse_body, require_fields

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        body = parse_body(event)
        require_fields(body, ['name'])
        
        category_name = body.get('name', '').strip()
        if not category_name:
            return error_response(400, 'Missing category name')

        category_id = str(uuid.uuid4())

        category = {
            'PK': f'CATEGORY#{category_id}',
            'SK': 'METADATA',
            'name': category_name,
            'type': 'category',
            'deleted': False
        }

        table.put_item(Item=category)

        return success_response(201, {
            'message': 'Category created successfully',
            'category_id': category_id
        })

    except ValueError as ve:
        return error_response(400, 'Bad json')

    except Exception as e:
        return handle_exception(e)