import json
import os
import smtplib
import boto3
from datetime import datetime
from email.mime.text import MIMEText

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
        user_email = body.get('email', '')
        
        # 1. Save to database
        item = {
            'pk': f"TYPE#{role}",
            'sk': f"TS#{datetime.utcnow().isoformat()}",
            'timestamp': datetime.utcnow().isoformat(),
            'data': body
        }
        table.put_item(Item=item)
        
        # 2. Send the free confirmation email
        if user_email:
            try:
                # Customize the message based on who is registering
                if role == "Teacher":
                    msg_body = f"Dear Applicant,\n\nThank you for submitting your employment application to Covenant Private School. Our administration team will review your details shortly.\n\nWarm regards,\nCovenant Private School"
                else:
                    msg_body = f"Dear Parent/Guardian,\n\nThank you for registering your child with Covenant Private School. We have securely received your admission details.\n\nWarm regards,\nCovenant Private School"

                msg = MIMEText(msg_body)
                msg['Subject'] = 'Registration Confirmation - Covenant Private School'
                msg['From'] = f"Covenant Admissions <{os.environ['SENDER_EMAIL']}>"
                msg['To'] = user_email

                # Connect to Gmail's secure SMTP server
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(os.environ['SENDER_EMAIL'], os.environ['SENDER_PASSWORD'])
                    server.send_message(msg)
            except Exception as email_error:
                # If the email fails (e.g., fake email address), print to AWS logs but don't crash the app
                print(f"Failed to send email to {user_email}: {email_error}")

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