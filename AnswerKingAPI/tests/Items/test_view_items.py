from unittest.mock import patch
from Items.view_items import lambda_handler

@patch('Items.view_items.table')
def test_lambda_handler_query_success_returns_200(mock_table):
    mock_table.query.return_value = {
        'Items': [
            {'PK': 'CATEGORY#1', 'SK': 'item#123', 'name': 'Pasta', 'type': 'item', 'deleted': False, 'description': 'description', 'itemID': '123', 'price': '5.99'},
            {'PK': 'CATEGORY#2', 'SK': 'item#456', 'name': 'Curry', 'type': 'item', 'deleted': False, 'description': 'description', 'itemID': '456', 'price': '9.99'}
        ]
    }

    result = lambda_handler({}, {})
    assert result['statusCode'] == 200
    assert 'Pasta' in result['body']
    assert 'Curry' in result['body']


@patch('Items.view_items.table')
def test_lambda_handler_query_raises_exception_returns_500_error(mock_table):
    mock_table.query.side_effect = Exception("Something went wrong")

    result = lambda_handler({}, {})
    assert result['statusCode'] == 500
    assert 'Something went wrong' in result['body']