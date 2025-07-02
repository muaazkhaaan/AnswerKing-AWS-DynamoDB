import boto3
from utils.validation import get_path_param
from utils.response import success_response, error_response, handle_exception

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        category_id = get_path_param(event, 'category_id')
        item_id = get_path_param(event, 'item_id')

        table.update_item(
            Key={
                'PK': f'CATEGORY#{category_id}',
                'SK': f'item#{item_id}'
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