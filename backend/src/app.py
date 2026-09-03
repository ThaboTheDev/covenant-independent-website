import json
import os
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['TABLE_NAME']
table = dynamodb.Table(TABLE_NAME)

def get_cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST"
    }

def register_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        role = body.get('role', 'Parent') # 'Parent' or 'Teacher'
        email = body.get('email')
        
        # Basic validation
        if not email:
            return {
                "statusCode": 400,
                "headers": get_cors_headers(),
                "body": json.dumps({"error": "Email is required"})
            }
        
        # Build the DynamoDB item
        item = {
            'pk': f"TYPE#{role}",
            'sk': f"EMAIL#{email}",
            'timestamp': datetime.utcnow().isoformat(),
            'data': body  # Stores all form fields automatically
        }
        
        # Write to On-Demand table (Handles 1,000+ concurrent requests safely)
        table.put_item(Item=item)
        
        return {
            "statusCode": 200,
            "headers": get_cors_headers(),
            "body": json.dumps({
                "message": "Registration successful", 
                "pk": item['pk'], 
                "sk": item['sk']
            })
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": get_cors_headers(),
            "body": json.dumps({"error": str(e)})
        }