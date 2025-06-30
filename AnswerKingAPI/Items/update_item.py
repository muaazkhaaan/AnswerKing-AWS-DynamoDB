import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    print(event)
    try:
        path_params = event.get('pathParameters', {})
        category_id = path_params.get('category_id', '').strip()
        item_id = path_params.get('item_id', '').strip()
        body = json.loads(event.get('body', '{}'))

        existing = table.get_item(
            Key={
                'PK': f'CATEGORY#{category_id}',
                'SK': f'item#{item_id}'
            }
        )

        if 'Item' not in existing:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Item not found'})
            }

        update_expr = []
        expr_attr_values = {}
        expr_attr_names = {}

        if 'name' in body:
            update_expr.append('#name = :name')
            expr_attr_names['#name'] = 'name'
            expr_attr_values[':name'] = body['name']

        if 'price' in body:
            update_expr.append('price = :price')
            expr_attr_values[':price'] = Decimal(str(body['price']))

        if 'description' in body:
            update_expr.append('description = :desc')
            expr_attr_values[':desc'] = body['description']

        if not update_expr:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No valid fields to update'})
            }

        update_expression = 'SET ' + ', '.join(update_expr)

        kwargs = {
            'Key': {
                'PK': f'CATEGORY#{category_id}',
                'SK': f'item#{item_id}'
            },
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expr_attr_values
        }

        if expr_attr_names:
            kwargs['ExpressionAttributeNames'] = expr_attr_names

        table.update_item(**kwargs)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Item updated successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }