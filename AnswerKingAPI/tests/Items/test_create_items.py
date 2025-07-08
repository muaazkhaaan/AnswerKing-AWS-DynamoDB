import json
from unittest.mock import patch
from decimal import Decimal
from Items.create_item import lambda_handler

@patch('Items.create_item.table')
@patch('Items.create_item.uuid.uuid4')
def test_lambda_handler_valid_input_returns_201(mock_uuid, mock_table):
    mock_uuid.return_value = 'test-item-id'
    mock_table.get_item.return_value = {'Item': {'PK': 'CATEGORY#abc', 'SK': 'METADATA'}}
    
    event = {
        'body': json.dumps({
            'name': 'Test Item',
            'category_id': 'abc',
            'price': "5.99", 
            'description': 'Test description'
        })
    }

    result = lambda_handler(event, {})
    body = json.loads(result['body'])
    mock_table.put_item.assert_called_once()
    saved_item = mock_table.put_item.call_args[1]['Item']

    assert result['statusCode'] == 201
    assert body['message'] == 'Item created'
    assert saved_item['name'] == 'Test Item'
    assert saved_item['PK'] == 'CATEGORY#abc'
    assert saved_item['SK'] == 'item#test-item-id'
    assert saved_item['price'] == Decimal('5.99')
    assert saved_item['description'] == 'Test description'
    assert saved_item['type'] == 'item'
    assert saved_item['deleted'] is False
    assert saved_item['itemID'] == 'test-item-id'

@patch('Items.create_item.table')
def test_lambda_handler_missing_field_returns_400():
    event = {
        'body': json.dumps({
            'name': 'No Category',
            'price': 12,
            'description': 'Missing category_id'
        })
    }
    
    result = lambda_handler(event, {})

    assert result['statusCode'] == 400
    assert 'Missing required field' in result['body']