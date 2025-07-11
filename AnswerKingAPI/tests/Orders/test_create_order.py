import json
from decimal import Decimal
from unittest.mock import patch
from Orders.create_order import lambda_handler

@patch('Orders.create_order.table')
@patch('Orders.create_order.uuid.uuid4')
@patch('Orders.create_order.datetime')
def test_lambda_handler_valid_order_returns_201(mock_datetime, mock_uuid, mock_table):
    mock_datetime.now.return_value.isoformat.return_value = '2025-07-08T12:00:00+00:00'
    mock_uuid.return_value = 'test-order-id'

    mock_table.query.return_value = {
        'Items': [{
            'PK': 'CATEGORY#123',
            'SK': 'item#123',
            'itemID': '123',
            'price': "10.00",
            'deleted': False
        }]
    }

    event = {
        'body': json.dumps({
            'orderList': [
                {'itemID': '123', 'quantity': 2}
            ]
        })
    }

    result = lambda_handler(event, {})
    body = json.loads(result['body'])

    mock_table.put_item.assert_called_once_with(
        Item={
            'PK': 'ORDER#test-order-id',
            'SK': 'METADATA',
            'orderList': [{'itemID': '123', 'quantity': 2}],
            'price': Decimal('20.00'),
            'timestamp': '2025-07-08T12:00:00+00:00',
            'deleted': False,
            'type': 'order'
        }
    )

    assert result['statusCode'] == 201
    assert body['message'] == 'Order created successfully'
    assert body['orderID'] == 'test-order-id'

'''
Additional tests to do: 
Send in a balnk orderList, use invalid itemID, check that we cannot pass in <=0 as quantitiy and 500 error
'''