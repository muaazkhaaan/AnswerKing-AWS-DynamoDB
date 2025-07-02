from unittest.mock import patch
from Categories.view_categories import lambda_handler

@patch('Categories.view_categories.table')
def test_lambda_handler_success(mock_table):
    mock_table.query.return_value = {
        'Items': [
            {'PK': 'CATEGORY#1', 'SK': 'METADATA', 'name': 'Starters', 'type': 'category', 'deleted': False},
            {'PK': 'CATEGORY#2', 'SK': 'METADATA', 'name': 'Mains', 'type': 'category', 'deleted': False}
        ]
    }

    result = lambda_handler({}, {})
    assert result['statusCode'] == 200
    assert 'Starters' in result['body']
    assert 'Mains' in result['body']

@patch('Categories.view_categories.table')
def test_lambda_handler_failure(mock_table):
    mock_table.query.side_effect = Exception("Something went wrong")

    result = lambda_handler({}, {})
    assert result['statusCode'] == 500
    assert 'Something went wrong' in result['body']
