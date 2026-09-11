import csv
import json

input_file = 'results (2).csv'
output_file = 'covenant_master_spreadsheet.csv'

clean_rows = []
# We will collect all unique column names here
all_columns = set(['Registration_Type', 'Timestamp']) 

print("Reading raw DynamoDB data...")

with open(input_file, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    
    for row in reader:
        pk = row.get('pk', '')
        timestamp = row.get('timestamp', '')
        raw_data = row.get('data', '{}')
        
        # Start a fresh, clean row
        clean_row = {
            'Registration_Type': 'Teacher' if 'Teacher' in str(pk) else 'Learner',
            'Timestamp': timestamp
        }
        
        try:
            user_data = json.loads(raw_data)
            
            for key, value in user_data.items():
                # Strip out the DynamoDB {'S': '...'} or {'N': '...'} wrappers
                if isinstance(value, dict):
                    # Get the actual text inside the dictionary
                    clean_text = list(value.values())[0] if value else ""
                    clean_row[key] = clean_text
                else:
                    # If it's already normal text, just keep it
                    clean_row[key] = str(value).strip()
                    
                all_columns.add(key)
                
        except json.JSONDecodeError:
            continue
            
        clean_rows.append(clean_row)

# Sort the columns alphabetically, but keep Type and Timestamp at the very front
fieldnames = ['Registration_Type', 'Timestamp'] + sorted(list(all_columns - {'Registration_Type', 'Timestamp'}))

print("Writing clean spreadsheet...")

# Write the flattened data to a new CSV file
with open(output_file, mode='w', encoding='utf-8', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(clean_rows)

print(f"Success! Open '{output_file}' in Excel or Google Sheets.")