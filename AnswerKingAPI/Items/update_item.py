import boto3
from boto3.dynamodb.conditions import Key
from utils.validation import get_path_param, parse_body, validate_price
from utils.response import success_response, error_response, handle_exception

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        item_id = get_path_param(event, 'item_id')
        body = parse_body(event)

        name = body.get('name', '').strip()
        description = body.get('description', '').strip()
        price = body.get('price', None)

        update_expr = []
        expr_attr_values = {}
        expr_attr_names = {}

        # Prepare placeholders and values to update the item's name safely, avoiding reserved word conflicts
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

        response = table.query(
            IndexName='ItemIDIndex',
            KeyConditionExpression=Key('itemID').eq(item_id),
            FilterExpression=Key('deleted').eq(False)
        )

        items = response.get('Items', [])
        if not items:
            return error_response(404, 'Item not found')

        item = items[0]

        update_expression = 'SET ' + ', '.join(update_expr)
        update_args = {
            'Key': {'PK': item['PK'], 'SK': item['SK']},
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expr_attr_values
        } # Prepare the update parameters with the item's keys, update expression, and attribute values.

        if expr_attr_names:
            update_args['ExpressionAttributeNames'] = expr_attr_names

        table.update_item(**update_args) # **unpack the dictionary and send all arguments to the function

        return success_response(200, {'message': 'Item updated successfully'})

    except ValueError as ve:
        return error_response(400, str(ve))
    except Exception as e:
        return handle_exception(e)