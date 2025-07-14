import json
from unittest.mock import patch
from Categories.create_category import lambda_handler

@patch('Categories.create_category.table')
@patch('Categories.create_category.uuid.uuid4')
def test_lambda_handler_valid_input_returns_201(mock_uuid, mock_table):
    mock_uuid.return_value = 'test-category-id'
    event = {
        'body': json.dumps({'name': 'Drinks'})
    }

    result = lambda_handler(event, {})
    body = json.loads(result['body'])
    mock_table.put_item.assert_called_once()
    saved_item = mock_table.put_item.call_args[1]['Item']
    
    assert result['statusCode'] == 201
    assert body['message'] == 'Category created successfully'
    assert body['category_id'] == 'test-category-id'
    assert saved_item['name'] == 'Drinks'
    assert saved_item['PK'] == 'CATEGORY#test-category-id'
    assert saved_item['type'] == 'category'
    assert saved_item['deleted'] is False

@patch('Categories.create_category.table')
def test_lambda_handler_blank_name_returns_400(mock_table):
    event = {
        'body': json.dumps({'name': '   '})  # whitespace only
    }

    result = lambda_handler(event, {})
    mock_table.put_item.assert_not_called()
    
    assert result['statusCode'] == 400
    assert 'Bad json' in result['body']

@patch('Categories.create_category.table')
def test_lambda_handler_invalid_json_returns_400(mock_table):
    event = {
        'body': '{bad json}'  # malformed JSON
    }

    result = lambda_handler(event, {})
    assert result['statusCode'] == 400
    assert 'error' in result['body']

@patch('Categories.create_category.table')
@patch('Categories.create_category.uuid.uuid4')
def test_lambda_handler_dynamodb_failure_returns_500(mock_uuid, mock_table):
    mock_uuid.return_value = 'fail-id'
    mock_table.put_item.side_effect = Exception("DynamoDB error")
    
    event = {
        'body': json.dumps({'name': 'Sides'})
    }

    result = lambda_handler(event, {})
    assert result['statusCode'] == 500
    assert 'DynamoDB error' in result['body']