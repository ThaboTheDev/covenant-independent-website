import json
import os
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['TABLE_NAME']
table = dynamodb.Table(TABLE_NAME)
ADMIN_SECRET = os.environ['ADMIN_SECRET']

def get_cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type, x-admin-key",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
    }

def register_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        role = body.get('role', 'Unknown')
        
        # Save to database
        item = {
            'pk': f"TYPE#{role}",
            'sk': f"TS#{datetime.utcnow().isoformat()}",
            'timestamp': datetime.utcnow().isoformat(),
            'data': body
        }
        table.put_item(Item=item)
        
        return {
            "statusCode": 200,
            "headers": get_cors_headers(),
            "body": json.dumps({"message": "Registration successful"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": get_cors_headers(),
            "body": json.dumps({"error": str(e)})
        }

def get_registrations_handler(event, context):
    try:
        headers = event.get('headers', {})
        # Check security passcode
        client_key = headers.get('x-admin-key') or headers.get('X-Admin-Key')
        
        if client_key != ADMIN_SECRET:
            return {
                "statusCode": 401,
                "headers": get_cors_headers(),
                "body": json.dumps({"error": "Unauthorized access"})
            }
        
        # Fetch all records safely
        items = []
        response = table.scan()
        items.extend(response.get('Items', []))
        
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
            
        return {
            "statusCode": 200,
            "headers": get_cors_headers(),
            "body": json.dumps({"registrations": items})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": get_cors_headers(),
            "body": json.dumps({"error": str(e)})
        }