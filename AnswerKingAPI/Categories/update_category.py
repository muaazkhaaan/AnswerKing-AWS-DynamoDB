import boto3
from utils.response import success_response, error_response, handle_exception
from utils.validation import get_path_param, parse_body

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        category_id = get_path_param(event, 'category_id')
        body = parse_body(event)

        existing = table.get_item(
            Key={
                'PK': f'CATEGORY#{category_id}',
                'SK': 'METADATA'
            }
        )

        if 'Item' not in existing:
            return error_response(404, 'Category not found')

        update_expr = []
        expr_attr_values = {}
        expr_attr_names = {}

        name = body.get('name')
        if name is not None:
            name = name.strip()
            if name == '':
                return error_response(400, 'Category name cannot be empty')
            update_expr.append('#name = :name')
            expr_attr_names['#name'] = 'name'
            expr_attr_values[':name'] = name

        if not update_expr:
            return error_response(400, 'No valid fields to update')

        update_expression = 'SET ' + ', '.join(update_expr)
        update_args = {
            'Key': {'PK': f'CATEGORY#{category_id}', 'SK': 'METADATA'},
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expr_attr_values
        }

        if expr_attr_names:
            update_args['ExpressionAttributeNames'] = expr_attr_names

        table.update_item(**update_args)

        return success_response(200, {'message': 'Category updated successfully'})

    except ValueError as ve:
        return error_response(400, str(ve))
    except Exception as e:
        return handle_exception(e)