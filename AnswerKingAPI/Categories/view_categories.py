import boto3
from boto3.dynamodb.conditions import Key, Attr
from utils.response import success_response, handle_exception

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        response = table.query(
            IndexName='type-index',
            KeyConditionExpression=Key('type').eq('category'),
            FilterExpression=Attr('deleted').eq(False)
        )

        categories = response.get('Items', [])

        return success_response(200, categories)

    except Exception as e:
        return handle_exception(e)