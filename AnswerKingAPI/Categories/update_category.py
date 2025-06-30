import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        path_params = event.get('pathParameters', {})
        category_id = path_params.get('category_id', '').strip()
        body = json.loads(event.get('body', '{}'))

        if not category_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing or invalid category_id'})
            }

        existing = table.get_item(
            Key={
                'PK': f'CATEGORY#{category_id}',
                'SK': 'METADATA'
            }
        )

        if 'Item' not in existing:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Category not found'})
            }

        update_expr = []
        expr_attr_values = {}
        expr_attr_names = {}

        name = body.get('name')

        if name is not None:
            name = name.strip()
            if name == '':
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Category name cannot be empty'})
                }
            update_expr.append('#name = :name')
            expr_attr_names['#name'] = 'name'
            expr_attr_values[':name'] = name

        if not update_expr:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No valid fields to update'})
            }

        update_expression = 'SET ' + ', '.join(update_expr)
        update_args = {
            'Key': {'PK': f'CATEGORY#{category_id}','SK': 'METADATA'},
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expr_attr_values
        }

        if expr_attr_names:
            update_args['ExpressionAttributeNames'] = expr_attr_names

        table.update_item(**update_args)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Category updated successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }