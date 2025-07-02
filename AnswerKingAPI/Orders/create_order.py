import boto3
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from boto3.dynamodb.conditions import Key
from utils.validation import parse_body, validate_order_entry
from utils.response import success_response, error_response, handle_exception

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        body = parse_body(event)
        order_list = body.get('orderList', [])

        if not order_list:
            return error_response(400, 'Missing orderList')

        total_price = Decimal('0.00')

        for entry in order_list:
            validate_order_entry(entry)

            item_id = entry['itemID']
            quantity = entry['quantity']

            response = table.query(
                IndexName='ItemIDIndex',
                KeyConditionExpression=Key('itemID').eq(item_id)
            )

            items = response.get('Items', [])
            if not items:
                return error_response(404, f'Item {item_id} not found')

            item = items[0]
            if item.get('deleted', True):
                return error_response(400, f'Item {item_id} is marked as deleted and cannot be ordered')

            total_price += Decimal(str(item['price'])) * Decimal(str(quantity))

        order_id = str(uuid.uuid4())
        timestamp = str(datetime.now(timezone.utc).isoformat())

        order_item = {
            'PK': f'ORDER#{order_id}',
            'SK': 'METADATA',
            'orderList': order_list,
            'price': total_price,
            'timestamp': timestamp,
            'deleted': False,
            'type': 'order'
        }

        table.put_item(Item=order_item)

        return success_response(201, {
            'message': 'Order created successfully',
            'orderID': order_id
        })

    except ValueError as ve:
        return error_response(400, str(ve))
    except Exception as e:
        return handle_exception(e)