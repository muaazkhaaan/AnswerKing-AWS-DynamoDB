from decimal import Decimal
import json

# Custom JSON encoder to safely convert Decimal objects (used by DynamoDB) into strings for JSON serialization
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)