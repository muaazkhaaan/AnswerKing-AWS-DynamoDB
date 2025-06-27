import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

# Decimal encoder for JSON
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    try:
        response = table.scan(
            FilterExpression="begins_with(SK, :itemPrefix)",
            ExpressionAttributeValues={":itemPrefix": "item#"}
        )

        items = response.get('Items', [])

        return {
            'statusCode': 200,
            'body': json.dumps(items, cls=DecimalEncoder)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }