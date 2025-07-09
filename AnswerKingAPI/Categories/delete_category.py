import boto3
from botocore.exceptions import ClientError
from utils.response import success_response, error_response, handle_exception
from utils.validation import get_path_param

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AnswerKingDB')

def lambda_handler(event, context):
    try:
        category_id = get_path_param(event, 'category_id')

        table.update_item(
            Key={
                'PK': f'CATEGORY#{category_id}',
                'SK': 'METADATA'
            },
            UpdateExpression='SET deleted = :deleted',
            ExpressionAttributeValues={':deleted': True},
            ConditionExpression='attribute_exists(PK) AND attribute_exists(SK)'
        )

        return success_response(200, {'message': 'Category deleted successfully'})

    except ValueError as ve:
        return error_response(400, str(ve))
    
    except ClientError as ce:
        if 'Error' in ce.response and 'Code' in ce.response['Error'] and ce.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return error_response(400, 'Category not found or already deleted')
        return handle_exception(ce)
        
    except Exception as e:
        return handle_exception(e)