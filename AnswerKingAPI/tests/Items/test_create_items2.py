import json
from decimal import Decimal
import pytest
from Items.create_item import lambda_handler

@pytest.fixture
def valid_event():
    return {
        'body': json.dumps({
            'name': 'Test Item',
            'category_id': 'abc',
            'price': "5.99", 
            'description': 'Test description'
        })
    }

@pytest.fixture
def missing_field_event():
    return {
        'body': json.dumps({
            'name': 'No Category',
            'price': '12.00',
            'description': 'Missing category_id'
        })
    }

@pytest.fixture
def invalid_category_event():
    return {
        'body': json.dumps({
            'name': 'Item',
            'category_id': 'nonexistent',
            'price': '5.00',
            'description': 'Test'
        })
    }

@pytest.fixture
def mock_table(mocker):
    return mocker.patch('Items.create_item.table')

@pytest.fixture
def mock_uuid(mocker):
    return mocker.patch('Items.create_item.uuid.uuid4')

class TestCreateItemLambda:

    def test_valid_input_returns_201(self, mock_table, mock_uuid, valid_event):
        mock_uuid.return_value = 'test-item-id'
        mock_table.get_item.return_value = {'Item': {'PK': 'CATEGORY#abc', 'SK': 'METADATA'}}

        result = lambda_handler(valid_event, {})
        saved_item = mock_table.put_item.call_args[1]['Item']

        expected_item = {
            'name': 'Test Item',
            'PK': 'CATEGORY#abc',
            'SK': 'item#test-item-id',
            'price': Decimal('5.99'),
            'description': 'Test description',
            'type': 'item',
            'deleted': False,
            'itemID': 'test-item-id'
        }

        assert result['statusCode'] == 201
        assert 'valid_event' in result['body']
        #assert saved_item == expected_item

    def test_missing_field_returns_400(self, mock_table, missing_field_event):
        result = lambda_handler(missing_field_event, {})
        assert result['statusCode'] == 400
        assert 'Missing required field' in result['body']

    def test_invalid_category_id_returns_400(self, mock_table, invalid_category_event):
        mock_table.get_item.return_value = {}
        result = lambda_handler(invalid_category_event, {})
        assert result['statusCode'] == 400
        assert 'Invalid category_id' in result['body']

    def test_unexpected_exception_returns_500(self, mock_table, valid_event):
        mock_table.get_item.side_effect = Exception("DynamoDB failure")
        result = lambda_handler(valid_event, {})
        assert result['statusCode'] == 500
        assert 'DynamoDB failure' in result['body']