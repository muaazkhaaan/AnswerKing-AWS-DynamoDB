import boto3
from boto3.dynamodb.conditions import Key, Attr
from utils.response import success_response, error_response, handle_exception
from utils.validation import get_path_param
from utils.dynamodb_helper import DecimalEncoder

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        category_id = get_path_param(event, 'category_id')
        pk_value = f'CATEGORY#{category_id}'

        response = table.query(
            KeyConditionExpression=Key('PK').eq(pk_value) & Key('SK').begins_with('item#'),
            FilterExpression=Attr('deleted').eq(False)
        )

        items = response.get('Items', [])

        if not items:
            return error_response(404, f'No items found for category {category_id}')

        return success_response(200, items, encoder=DecimalEncoder)

    except ValueError as ve:
        return error_response(400, str(ve))
    except Exception as e:
        return handle_exception(e)