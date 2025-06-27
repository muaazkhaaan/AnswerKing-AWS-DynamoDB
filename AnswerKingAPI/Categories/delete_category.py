import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        category_id = event.get('pathParameters', {}).get('category_id', '').strip()

        if not category_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing category_id'})
            }

        # Delete category metadata
        table.delete_item(
            Key={
                'PK': f'CATEGORY#{category_id}',
                'SK': 'METADATA'
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Category deleted successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }