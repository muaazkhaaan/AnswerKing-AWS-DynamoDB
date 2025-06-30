import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        category_id = event.get('pathParameters', {}).get('category_id', '').strip()
        item_id = event.get('pathParameters', {}).get('item_id', '').strip()

        if not category_id or not item_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing category_id or item_id'})
            }

        table.update_item(
            Key={
                'PK': f'CATEGORY#{category_id}',
                'SK': f'item#{item_id}'
            },
            UpdateExpression='SET deleted = :deleted',
            ExpressionAttributeValues={':deleted': True},
            ConditionExpression='attribute_exists(PK) AND attribute_exists(SK)'
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Item deleted successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }