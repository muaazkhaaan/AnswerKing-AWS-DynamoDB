import boto3
import uuid
from decimal import Decimal
from utils.validation import parse_body, require_fields, validate_price
from utils.response import success_response, error_response, handle_exception

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        body = parse_body(event)
        require_fields(body, ['name', 'category_id', 'price', 'description'])

        name = body['name'].strip()
        category_id = f"CATEGORY#{body['category_id'].strip()}"
        price = Decimal(str(body['price']))
        description = body['description'].strip()

        category_check = table.get_item(
            Key={
                'PK': category_id,
                'SK': 'METADATA'
            }
        )

        if 'Item' not in category_check:
            return error_response(400, 'Invalid category_id: does not exist')
        
        price = validate_price(price)

        item_id = str(uuid.uuid4())

        item = {
            'PK': category_id,
            'SK': f'item#{item_id}',
            'itemID': item_id,
            'name': name,
            'price': price,
            'description': description,
            'type': 'item',
            'deleted': False
        }

        table.put_item(Item=item)

        return success_response(201, {'message': 'Item created'})

    except ValueError as ve:
        return error_response(400, str(ve))
    except Exception as e:
        return handle_exception(e)