import csv
import smtplib
import time
import json
from email.mime.text import MIMEText

# Your Google Credentials
GMAIL_ADDRESS = "covenantprivateadmin@gmail.com"
GMAIL_APP_PASSWORD = "gczu bwld khwv xidl"

with open('results (1).csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    
    # Connect to Google's secure SMTP server
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        
        for row in reader:
            pk = row.get('pk', '')
            raw_data = row.get('data', '{}')
            
            try:
                user_data = json.loads(raw_data)
                
                # --- FIX: Extract the email from DynamoDB's {'S': '...'} format ---
                raw_email = user_data.get('email', '')
                if isinstance(raw_email, dict):
                    user_email = raw_email.get('S', '')
                else:
                    user_email = str(raw_email).strip()
                    
            except json.JSONDecodeError:
                print("Could not read data column for a row, skipping...")
                continue
            
            if not user_email or user_email == "None":
                continue

            # Check the pk column to see if it is a Teacher or Learner
            if "Teacher" in str(pk):
                msg_body = "Dear Applicant,\n\nThank you for submitting your employment application to Covenant Private School. Our administration team will review your details shortly.\n\nWarm regards,\nCovenant Private School"
            else:
                msg_body = "Dear Parent/Guardian,\n\nThank you for registering your child with Covenant Private School. We have securely received your admission details.\n\nWarm regards,\nCovenant Private School"

            msg = MIMEText(msg_body)
            msg['Subject'] = 'Registration Confirmation - Covenant Private School'
            msg['From'] = f"Covenant Admissions <{GMAIL_ADDRESS}>"
            msg['To'] = user_email
            
            try:
                server.send_message(msg)
                print(f"Sent successfully to {user_email}")
                # Pause for 2 seconds to avoid spam filters
                time.sleep(2) 
            except Exception as e:
                print(f"Failed to send to {user_email}: {e}")

print("All confirmation emails sent successfully!")