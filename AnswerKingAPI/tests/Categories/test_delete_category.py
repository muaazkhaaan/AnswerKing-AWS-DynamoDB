import json
from botocore.exceptions import ClientError
from unittest.mock import patch, MagicMock
from Categories.delete_category import lambda_handler

@patch('Categories.delete_category.table')
def test_lambda_handler_valid_input_returns_200(mock_table):
    event = {
        'pathParameters': {'category_id': '123'}
    }

    result = lambda_handler(event, {})
    body = json.loads(result['body'])

    mock_table.update_item.assert_called_once_with(
        Key={'PK': 'CATEGORY#123', 'SK': 'METADATA'},
        UpdateExpression='SET deleted = :deleted',
        ExpressionAttributeValues={':deleted': True},
        ConditionExpression='attribute_exists(PK) AND attribute_exists(SK)'
    )

    assert result['statusCode'] == 200
    assert body['message'] == 'Category deleted successfully'

@patch('Categories.delete_category.table')
def test_lambda_handler_missing_category_id_returns_400(mock_table):
    event = {
        'pathParameters': {}
    }

    result = lambda_handler(event, {})
    assert result['statusCode'] == 400
    assert 'Missing or invalid category_id' in result['body']

@patch('Categories.delete_category.table')
def test_lambda_handler_category_not_found_returns_400(mock_table):
    mock_table.update_item.side_effect = ClientError(
        error_response={
            'Error': {
                'Code': 'ConditionalCheckFailedException',
                'Message': 'The conditional request failed'
            }
        },
        operation_name='UpdateItem'
    )

    event = {
        'pathParameters': {'category_id': 'nonexistent'}
    }

    result = lambda_handler(event, {})
    body = json.loads(result['body'])

    assert result['statusCode'] == 400
    assert 'not found or already deleted' in body['error'].lower()

@patch('Categories.delete_category.table')
def test_lambda_handler_generic_exception_returns_500(mock_table):
    mock_table.update_item.side_effect = Exception("Something went wrong")

    event = {
        'pathParameters': {'category_id': '123'}
    }

    result = lambda_handler(event, {})
    assert result['statusCode'] == 500
    assert 'Something went wrong' in result['body']