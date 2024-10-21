# =============================================================================
# Packages
# =============================================================================
#%%
from config import config
import requests
import pandas as pd  
from io import StringIO
#%%
# =============================================================================
# Root Directory
# =============================================================================
root_directory = 'F:/open_git/redcap' # change to your pathway
# =============================================================================
# Exporting records
# =============================================================================
# Initial data
data = {
    'token': config['api_token'],
    'content': 'record',
    'action': 'export',
    'format': 'csv',# or json
    'type': 'flat',
    'csvDelimiter': '',
    'rawOrLabel': 'raw',# or label
    'rawOrLabelHeaders': 'raw',# or label
    'exportCheckboxLabel': 'true',# or false
    'exportSurveyFields': 'true',# or false
    'exportDataAccessGroups': 'false',# or true
    'returnFormat': 'json'
}

# Sending the request to the API
r = requests.post(config['api_url'], data=data)

# Check request status
if r.status_code != 200:
    print(f"Error accessing the API: {r.status_code} - {r.text}")
else:
    try:
        # Load the CSV from the response
        df1 = pd.read_csv(StringIO(r.text), delimiter=',', low_memory=False)

#        # Specify the variables you want to exclude
        exclude_fields = [
            'name'  # Example of a column to exclude, adjust as necessary
        ]

        # Exclude the specified variables
        df1 = df1.drop(columns=exclude_fields, errors='ignore')

        # Display the first rows of the DataFrame for verification
        print(df1.head())

        # Optional: Save the DataFrame to a CSV file
        df1.to_csv('dados_redcap.csv', index=False, sep=';', encoding='utf-8')
        print("Data exported and saved to 'dados_redcap.csv'")

    except Exception as e:
        print("Error processing the data:", e)

#%%

