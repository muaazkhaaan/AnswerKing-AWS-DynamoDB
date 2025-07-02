import boto3
from utils.response import success_response, handle_exception
from utils.dynamodb_helper import DecimalEncoder
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        response = table.query(
            IndexName='type-index',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('type').eq('item'),
            FilterExpression=Attr('deleted').eq(False)
        )

        items = response.get('Items', [])
        return success_response(200, items, encoder=DecimalEncoder)

    except Exception as e:
        return handle_exception(e)
