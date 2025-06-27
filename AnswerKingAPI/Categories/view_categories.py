import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        response = table.scan(
            FilterExpression='#type = :category',
            ExpressionAttributeNames={'#type': 'type'},
            ExpressionAttributeValues={':category': 'category'}
        )

        categories = response.get('Items', [])

        return {
            'statusCode': 200,
            'body': json.dumps(categories)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }