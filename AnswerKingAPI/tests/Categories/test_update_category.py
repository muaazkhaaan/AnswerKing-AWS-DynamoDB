import json
from unittest.mock import patch
from Categories.update_category import lambda_handler

@patch('Categories.update_category.table')
def test_lambda_handler_valid_update_returns_200(mock_table):
    mock_table.get_item.return_value = {
        'Item': {
            'PK': 'CATEGORY#test-id',
            'SK': 'METADATA',
            'name': 'Old Name'
        }
    }

    event = {
        'pathParameters': {'category_id': 'test-id'},
        'body': json.dumps({'name': 'New Name'})
    }

    result = lambda_handler(event, {})
    body = json.loads(result['body'])

    mock_table.update_item.assert_called_once_with(
        Key={'PK': 'CATEGORY#test-id', 'SK': 'METADATA'},
        UpdateExpression='SET #name = :name',
        ExpressionAttributeNames={'#name': 'name'},
        ExpressionAttributeValues={':name': 'New Name'}
    )
    
    assert result['statusCode'] == 200
    assert body['message'] == 'Category updated successfully'

@patch('Categories.update_category.table')
def test_lambda_handler_category_not_found_returns_404(mock_table):
    mock_table.get_item.return_value = {}

    event = {
        'pathParameters': {'category_id': 'fake-id'}
    }

    result = lambda_handler(event, {})
    
    assert result['statusCode'] == 404
    assert 'Category not found' in result['body']

@patch('Categories.update_category.table')
def test_lambda_handler_blank_name_returns_400(mock_table):
    mock_table.get_item.return_value = {
        'Item': {
            'PK': 'CATEGORY#test-id',
            'SK': 'METADATA'
        }
    }

    event = {
        'pathParameters': {'category_id': 'test-id'},
        'body': json.dumps({'name': '   '})
    }

    result = lambda_handler(event, {})
    
    assert result['statusCode'] == 400
    assert 'Category name cannot be empty' in result['body']

@patch('Categories.update_category.table')
def test_lambda_handler_no_fields_to_update_returns_400(mock_table):
    mock_table.get_item.return_value = {
        'Item': {
            'PK': 'CATEGORY#test-id',
            'SK': 'METADATA'
        }
    }

    event = {
        'pathParameters': {'category_id': 'test-id'},
        'body': json.dumps({})
    }

    result = lambda_handler(event, {})
    
    assert result['statusCode'] == 400
    assert 'No valid fields to update' in result['body']

@patch('Categories.update_category.table')
def test_lambda_handler_exception_returns_500(mock_table):
    mock_table.get_item.side_effect = Exception("Unexpected error")

    event = {
        'pathParameters': {'category_id': 'test-id'}
    }

    result = lambda_handler(event, {})
    
    assert result['statusCode'] == 500
    assert 'Unexpected error' in result['body']