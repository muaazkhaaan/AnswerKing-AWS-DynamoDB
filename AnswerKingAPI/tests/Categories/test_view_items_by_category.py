import json
from unittest.mock import patch
from Categories.view_items_by_category import lambda_handler

@patch('Categories.view_items_by_category.table')
def test_lambda_handler_items_found_returns_200(mock_table):
    mock_table.query.return_value = {
        'Items': [
            {'PK': 'CATEGORY#123', 'SK': 'item#1', 'name': 'Burger', 'deleted': False},
            {'PK': 'CATEGORY#123', 'SK': 'item#2', 'name': 'Pizza', 'deleted': False}
        ]
    }

    event = {
        'pathParameters': {'category_id': '123'}
    }

    result = lambda_handler(event, {})
    body = json.loads(result['body'])

    mock_table.query.assert_called_once()

    assert result['statusCode'] == 200
    assert isinstance(body, list)
    assert body[0]['name'] == 'Burger'
    assert body[1]['name'] == 'Pizza'

@patch('Categories.view_items_by_category.table')
def test_lambda_handler_no_items_found_returns_404(mock_table):
    mock_table.query.return_value = {'Items': []}

    event = {
        'pathParameters': {'category_id': '123'}
    }

    result = lambda_handler(event, {})
    
    assert result['statusCode'] == 404
    assert 'No items found' in result['body']

def test_lambda_handler_missing_category_id_returns_400():
    event = {
        'pathParameters': {}
    }

    result = lambda_handler(event, {})
    
    assert result['statusCode'] == 400
    assert 'Missing or invalid category_id' in result['body']

@patch('Categories.view_items_by_category.table')
def test_lambda_handler_dynamodb_exception_returns_500(mock_table):
    mock_table.query.side_effect = Exception("DynamoDB failure")

    event = {
        'pathParameters': {'category_id': '123'}
    }

    result = lambda_handler(event, {})
    
    assert result['statusCode'] == 500
    assert 'DynamoDB failure' in result['body']