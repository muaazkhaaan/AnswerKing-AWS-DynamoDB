import boto3
from utils.validation import get_path_param, parse_body, validate_price
from utils.response import success_response, error_response, handle_exception

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        category_id = get_path_param(event, 'category_id')
        item_id = get_path_param(event, 'item_id')
        body = parse_body(event)

        name = body.get('name', '').strip()
        description = body.get('description', '').strip()
        price = body.get('price', None)

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
            price_val = validate_price(price)
            update_expr.append('price = :price')
            expr_attr_values[':price'] = price_val

        if not update_expr:
            return error_response(400, 'No valid fields to update')

        existing = table.get_item(
            Key={'PK': f'CATEGORY#{category_id}', 'SK': f'item#{item_id}'}
        )
        if 'Item' not in existing:
            return error_response(404, 'Item not found')

        update_expression = 'SET ' + ', '.join(update_expr)
        update_args = {
            'Key': {'PK': f'CATEGORY#{category_id}', 'SK': f'item#{item_id}'},
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expr_attr_values
        }

        if expr_attr_names:
            update_args['ExpressionAttributeNames'] = expr_attr_names

        # **update_args to unpack the dictionary into keyword arguments
        table.update_item(**update_args)

        return success_response(200, {'message': 'Item updated successfully'})

    except ValueError as ve:
        return error_response(400, str(ve))
    except Exception as e:
        return handle_exception(e)