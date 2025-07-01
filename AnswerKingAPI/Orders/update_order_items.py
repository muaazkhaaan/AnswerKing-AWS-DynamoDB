import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        order_id = event.get('pathParameters', {}).get('order_id', '').strip()
        if not order_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing or invalid order_id'})
            }

        body = json.loads(event.get('body', '{}'))
        to_add = body.get('add', [])
        to_remove = body.get('remove', [])

        response = table.get_item(
            Key={
                'PK': f'ORDER#{order_id}',
                'SK': 'METADATA'
            }
        )

        # 'Item' is the fixed key for the retrieved record in DynamoDB's get_item() response
        order = response.get('Item')
        if not order:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Order does not exist. Check the order number and try again.'})
            }

        order_list = order.get('orderList', [])
        order_map = {item['itemID']: item for item in order_list}

        # Add items
        for entry in to_add:
            item_id = entry.get('itemID')
            quantity = entry.get('quantity')

            if not isinstance(item_id, str) or not item_id.strip() or not isinstance(quantity, int) or quantity <= 0:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Invalid itemID or quantity in add list: {entry}'})
                }

            result = table.query(
                IndexName='ItemIDIndex',
                KeyConditionExpression=Key('itemID').eq(item_id)
            )

            items = result.get('Items', [])
            if not items:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': f'Item {item_id} not found'})
                }

            item_data = items[0]
            if item_data.get('deleted', True):
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Item {item_id} is marked as deleted and cannot be added'})
                }

            if item_id in order_map:
                order_map[item_id]['quantity'] += quantity
            else:
                order_map[item_id] = {
                    'itemID': item_id,
                    'quantity': quantity
                }

        # Remove items
        for entry in to_remove:
            item_id = entry.get('itemID')
            if not isinstance(item_id, str) or not item_id.strip():
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Invalid itemID in remove list: {entry}'})
                }

            order_map.pop(item_id, None)

        # Recalculate total price
        new_order_list = list(order_map.values())
        total_price = Decimal('0.00')

        for item in new_order_list:
            item_id = item['itemID']
            quantity = item['quantity']

            result = table.query(
                IndexName='ItemIDIndex',
                KeyConditionExpression=Key('itemID').eq(item_id)
            )

            db_item = result['Items'][0]
            price = Decimal(str(db_item['price']))
            total_price += price * Decimal(str(quantity))

        # Save updated order
        table.update_item(
            Key={
                'PK': f'ORDER#{order_id}',
                'SK': 'METADATA'
            },
            UpdateExpression='SET orderList = :orderList, price = :price',
            ExpressionAttributeValues={
                ':orderList': new_order_list,
                ':price': total_price
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Order updated successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }