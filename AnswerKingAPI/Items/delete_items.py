import boto3
from utils.validation import get_path_param
from utils.response import success_response, error_response, handle_exception

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        item_id = get_path_param(event, 'item_id')

        response = table.query(
            IndexName='ItemIDIndex',  # Use GSI to find itemID and match up keys to the itemID
            KeyConditionExpression=boto3.dynamodb.conditions.Key('itemID').eq(item_id),
            FilterExpression=boto3.dynamodb.conditions.Attr('deleted').eq(False)
        )

        items = response.get('Items', [])
        if not items:
            return error_response(404, 'Item not found')

        item = items[0] # There can only be 1 itemID per item in the table

        table.update_item(
            Key={
                'PK': item['PK'],
                'SK': item['SK']
            },
            UpdateExpression='SET deleted = :deleted',
            ExpressionAttributeValues={':deleted': True},
            ConditionExpression='attribute_exists(PK) AND attribute_exists(SK)'
        )

        return success_response(200, {'message': 'Item deleted successfully'})

    except ValueError as ve:
        return error_response(400, str(ve))
    except Exception as e:
        return handle_exception(e)