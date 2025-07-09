import json
from unittest.mock import patch
from decimal import Decimal
from Items.delete_items import lambda_handler

@patch('Items.delete_items.table')
def test_lambda_handler_valid_input_returns_200(mock_table):
    mock_table.query.return_value = {
        'Items': [{
            'PK': 'CATEGORY#123',
            'SK': 'item#123',
            'itemID': '123',
            'deleted': False
        }]
    }

    event = {
        'pathParameters': {'item_id': '123'}
    }

    result = lambda_handler(event, {})
    body = json.loads(result['body'])

    mock_table.update_item.assert_called_once_with(
        Key={'PK': 'CATEGORY#123', 'SK': 'item#123'},
        UpdateExpression='SET deleted = :deleted',
        ExpressionAttributeValues={':deleted': True},
        ConditionExpression='attribute_exists(PK) AND attribute_exists(SK)'
    )

    assert result['statusCode'] == 200
    assert body['message'] == 'Item deleted successfully'

@patch('Items.delete_items.table')
def test_lambda_handler_item_not_found_returns_404(mock_table):
    mock_table.query.return_value = {'Items': []}
    event = {'pathParameters': {'item_id': 'nonexistent-id'}}

    result = lambda_handler(event, {})
    body = json.loads(result['body'])

    assert result['statusCode'] == 404
    assert 'Item not found' in body['error']

@patch('Items.delete_items.table')
def test_lambda_handler_missing_item_id_returns_400(mock_table):
    event = {'pathParameters': {}}

    result = lambda_handler(event, {})
    body = json.loads(result['body'])

    assert result['statusCode'] == 400
    assert 'Missing or invalid item_id' in body['error']

@patch('Items.delete_items.table')
def test_lambda_handler_exception_returns_500(mock_table):
    mock_table.query.side_effect = Exception("Unexpected DynamoDB error")
    event = {'pathParameters': {'item_id': '123'}}

    result = lambda_handler(event, {})
    body = json.loads(result['body'])

    assert result['statusCode'] == 500
    assert 'Unexpected DynamoDB error' in body['error']