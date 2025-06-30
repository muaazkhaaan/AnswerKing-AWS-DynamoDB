import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import uuid
from datetime import datetime, timezone


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        order_list = body.get('orderList', [])

        if not order_list:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing orderList'})
            }

        total_price = Decimal('0.00')

        for entry in order_list:
            item_id = entry.get('itemID')
            quantity = entry.get('quantity')

            if not item_id or quantity is None or quantity <= 0:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Each order item must include itemID and quantity > 0'})
                }

            # Query item by itemID using the GSI
            response = table.query(
                IndexName='ItemIDIndex',
                KeyConditionExpression=Key('itemID').eq(item_id)
            )

            items = response.get('Items', [])
            if not items:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': f'Item {item_id} not found'})
                }

            item = items[0]

            if item.get('deleted', True):
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Item {item_id} is marked as deleted and cannot be ordered'})
                }

            price = Decimal(str(item['price']))
            total_price += price * Decimal(str(quantity))

        order_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)

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

        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'Order created successfully',
                'orderID': order_id
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }