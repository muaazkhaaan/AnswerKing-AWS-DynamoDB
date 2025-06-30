import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

def lambda_handler(event, context):
    try:
        category_id = event.get('pathParameters', {}).get('category_id', '').strip()

        if not category_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing or invalid category ID'})
            }

        pk_value = f'CATEGORY#{category_id}'

        # Query all SKs starting with 'item#' under the given PK
        response = table.query(
            KeyConditionExpression=Key('PK').eq(pk_value) & Key('SK').begins_with('item#'),
            FilterExpression=Attr('deleted').eq(False)
        )

        items = response.get('Items', [])

        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'No items found for category {category_id}'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps(items, cls=DecimalEncoder)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }