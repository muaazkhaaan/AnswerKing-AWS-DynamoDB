import json
import boto3
from decimal import Decimal
import re

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        path_params = event.get('pathParameters', {})
        category_id = path_params.get('category_id', '').strip()
        item_id = path_params.get('item_id', '').strip()

        # ValidateIDs
        if not category_id or not item_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing category_id or item_id'})
            }

        # Parse request
        body = json.loads(event.get('body', '{}'))
        name = body.get('name', '').strip()
        description = body.get('description', '').strip()
        price = body.get('price', None)

        # Validate fields
        update_expr = []
        expr_attr_values = {}
        expr_attr_names = {}

        if name:
            update_expr.append('#name = :name')
            expr_attr_names['#name'] = 'name'
            expr_attr_values[':name'] = name

        if description:
            update_expr.append('description = :desc')
            expr_attr_values[':desc'] = description

        if price is not None:
            # Price validation
            if not re.match(r'^\d+(\.\d{2})$', str(price)):
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Price must be a number with exactly 2 decimal places (e.g., 12.99)'})
                }

            try:
                price_val = Decimal(str(price))
                update_expr.append('price = :price')
                expr_attr_values[':price'] = price_val
            except:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Invalid price format'})
                }

        if not update_expr:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No valid fields to update'})
            }

        # Check if item exists first
        existing = table.get_item(
            Key={'PK': f'CATEGORY#{category_id}', 'SK': f'item#{item_id}'}
        )
        if 'Item' not in existing:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Item not found'})
            }

        # Perform update
        update_expression = 'SET ' + ', '.join(update_expr)
        update_args = {
            'Key': {'PK': f'CATEGORY#{category_id}', 'SK': f'item#{item_id}'},
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expr_attr_values
        }
        if expr_attr_names:
            update_args['ExpressionAttributeNames'] = expr_attr_names

        table.update_item(**update_args)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Item updated successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }