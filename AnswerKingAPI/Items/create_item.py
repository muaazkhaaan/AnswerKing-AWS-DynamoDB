import json
import boto3
import uuid
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        name = body.get('name', '').strip()
        category_id = body.get('category_id', '').strip()
        price = body.get('price')
        description = body.get('description', '').strip()

        if not all([name, category_id, price, description]):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields'})
            }

        category_check = table.get_item(
            Key={
                'PK': category_id,
                'SK': 'METADATA'
            }
        )

        if 'Item' not in category_check:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid category_id: does not exist'})
            }

        item_id = str(uuid.uuid4())

        item = {
            'PK': category_id,
            'SK': f'item#{item_id}',
            'itemID': item_id,
            'name': name,
            'price': Decimal(str(price)),
            'description': description,
            'type': 'item',
            'deleted': False
        }

        table.put_item(Item=item)

        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'Item created'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }