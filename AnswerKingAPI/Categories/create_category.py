import json
import boto3
import uuid

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        category_name = body.get('name', '').strip()

        if not category_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing category name'})
            }

        category_id = str(uuid.uuid4())

        category = {
            'PK': f'CATEGORY#{category_id}',
            'SK': 'METADATA',
            'name': category_name,
            'type': 'category',
            'deleted': False
        }

        table.put_item(Item=category)

        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'Category created successfully',
                'category_id': category_id
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }