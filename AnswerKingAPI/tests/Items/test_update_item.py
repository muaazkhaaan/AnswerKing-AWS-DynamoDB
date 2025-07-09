import json
from decimal import Decimal
from unittest.mock import patch, MagicMock
from Items.update_item import lambda_handler

@patch('Items.update_item.table')
def test_lambda_handler_valid_update_returns_200(mock_table):
    mock_table.query.return_value = {
        'Items': [{
            'PK': 'CATEGORY#123',
            'SK': 'item#123',
            'itemID': '123',
            'deleted': False
        }]
    }

    event = {
        'pathParameters': {'item_id': '123'},
        'body': json.dumps({
            'name': 'Updated Name',
            'description': 'Updated description',
            'price': '19.99' 
        })
    }
    result = lambda_handler(event, {})
    body = json.loads(result['body'])

    mock_table.update_item.assert_called_once_with(
        Key={'PK': 'CATEGORY#123', 'SK': 'item#123'},
        UpdateExpression='SET #name = :name, description = :desc, price = :price',
        ExpressionAttributeNames={'#name': 'name'},
        ExpressionAttributeValues={
            ':name': 'Updated Name',
            ':desc': 'Updated description', 
            ':price': Decimal('19.99')    
        }
    )

    assert result['statusCode'] == 200
    assert body['message'] == 'Item updated successfully'

@patch('Items.update_item.table')
def test_update_only_name_returns_200(mock_table):
    mock_table.query.return_value = {
        'Items': [{
            'PK': 'CATEGORY#123', 
            'SK': 'item#123', 
            'itemID': '123',
            'deleted': False
        }]
    }

    event = {
        'pathParameters': {'item_id': '123'},
        'body': json.dumps({'name': 'Just A New Name'})
    }
    
    result = lambda_handler(event, {})
    body = json.loads(result['body'])

    mock_table.update_item.assert_called_once_with(
        Key={'PK': 'CATEGORY#123', 'SK': 'item#123'},
        UpdateExpression='SET #name = :name',
        ExpressionAttributeNames={'#name': 'name'},
        ExpressionAttributeValues={':name': 'Just A New Name'}
    )
    
    assert result['statusCode'] == 200
    assert body['message'] == 'Item updated successfully'

@patch('Items.update_item.table')
def test_lambda_handler_missing_all_fields_returns_400(mock_table):
    event = {
        'pathParameters': {'item_id': '123'},
        'body': json.dumps({})
    }

    result = lambda_handler(event, {})
    body = json.loads(result['body'])

    assert result['statusCode'] == 400
    assert 'No valid fields to update' in body['error']

@patch('Items.update_item.table')
def test_lambda_handler_invalid_price_format_1dp_returns_400(mock_table):
    event = {
        'pathParameters': {'item_id': '123'},
        'body': json.dumps({
            'price': '12.9' 
        })
    }

    result = lambda_handler(event, {})
    body = json.loads(result['body'])

    assert result['statusCode'] == 400
    assert 'Price must be a POSITIVE number with exactly 2 decimal places' in body['error']

@patch('Items.update_item.table')
def test_lambda_handler_invalid_price_format_too_many_dp_returns_400(mock_table):
    event = {
        'pathParameters': {'item_id': '123'},
        'body': json.dumps({
            'price': '12.999' 
        })
    }

    result = lambda_handler(event, {})
    body = json.loads(result['body'])

    assert result['statusCode'] == 400
    assert 'Price must be a POSITIVE number with exactly 2 decimal places' in body['error']

@patch('Items.update_item.table')
def test_lambda_handler_negative_price_returns_400(mock_table):
    event = {
        'pathParameters': {'item_id': '123'},
        'body': json.dumps({
            'price': '-10.00'
        })
    }

    result = lambda_handler(event, {})
    body = json.loads(result['body'])

    assert result['statusCode'] == 400
    assert 'Price must be a POSITIVE number with exactly 2 decimal places' in body['error']

@patch('Items.update_item.table')
def test_lambda_handler_item_not_found_returns_404(mock_table):
    mock_table.query.return_value = {'Items': []}

    event = {
        'pathParameters': {'item_id': 'notfound'},
        'body': json.dumps({'name': 'Something'})
    }

    result = lambda_handler(event, {})
    body = json.loads(result['body'])

    assert result['statusCode'] == 404
    assert 'Item not found' in body['error']


@patch('Items.update_item.table')
def test_lambda_handler_unexpected_exception_returns_500(mock_table):
    mock_table.query.side_effect = Exception("Something went wrong")

    event = {
        'pathParameters': {'item_id': '123'},
        'body': json.dumps({'name': 'Name'})
    }

    result = lambda_handler(event, {})
    body = json.loads(result['body'])

    assert result['statusCode'] == 500
    assert 'Something went wrong' in body['error']