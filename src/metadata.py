# =============================================================================
# Packages
# =============================================================================
#%%
from config import config
import requests
import pandas as pd  
from io import StringIO
# =============================================================================
# Root Directory
# =============================================================================
root_directory = 'F:/open_git/redcap' # change to your pathway
# =============================================================================
# Exporting metadata
# =============================================================================
# Initial data
data = {
    'token': config['api_token'],
    'content': 'metadata',
    'format': 'csv',
    'returnFormat': 'json'
}

# Make the request to the API
response = requests.post(config['api_url'], data=data)

# Check if the request was successful
if response.status_code == 200:
    # Convert the JSON response to a Python dict
    metadata_df = pd.read_csv(StringIO(response.text))
    # Print the metadata
    print(metadata_df.head())
else:
    print("Failed to retrieve metadata:", response.status_code, response.text)

# =============================================================================
# Save the metadata
# =============================================================================
metadata_df.to_csv(f'{root_directory}/results/metadat.csv', index=False, encoding='utf-8')

#%%
# =============================================================================
# Count variable types
# =============================================================================
def count_observations_by_type(df, variable):
    """
    Counts the number of observations for each type of variable.

    Parameters:
    - df: DataFrame containing the REDCap metadata.

    Returns:
    - A Series with the number of observations for each variable type.
    """
    # Count the number of occurrences for each field_type
    type_count = df[variable].value_counts()

    return type_count

# Usage
count_observations_by_type(metadata_df, 'field_type')

#%%

def create_field_type_string_and_save(metadata_df, field_type, root_directory):
    """
    Generates a comma-separated string containing the field names of a given field type
    and saves the resulting DataFrame to a CSV file.

    Parameters:
    - metadata_df: pd.DataFrame - The DataFrame containing the REDCap metadata.
    - field_type: str - The field type to filter by.
    - root_directory: str - The root directory where the CSV file will be saved.

    Returns:
    - str: A string containing the field names separated by commas.
    - pd.DataFrame: The filtered DataFrame with the fields of the specified type.
    """
    # Filter the metadata based on the provided field type
    field_type_df = metadata_df[metadata_df['field_type'].isin([field_type])][['field_name']]
    
    # Transform the 'field_name' column into a list of strings
    field_name_list = field_type_df['field_name'].tolist()
    
    # Convert the list into a single comma-separated string
    field_name_string = ', '.join(field_name_list)
    
    # Save the resulting DataFrame to a CSV file
    output_file = f"{root_directory}/results/{field_type}_fields.csv"
    field_type_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"'{field_type}' DataFrame saved at: {output_file}")
    
    return field_name_string, field_type_df

#%%
# Usage for checkbox
checkbox_string, checkbox_df = create_field_type_string_and_save(metadata_df, 'checkbox', root_directory)

# Usage for descriptive
descriptive_string, descriptive_df = create_field_type_string_and_save(metadata_df, 'descriptive', root_directory)

#%%
# =============================================================================
# Labels
# =============================================================================
# Filter variables that have options, such as checkbox, radio, or dropdown
variables_with_choices = metadata_df[metadata_df['field_type'].isin(['checkbox', 'radio', 'dropdown'])]

# Display the 'field_name' and the 'select_choices_or_calculations' options
print(variables_with_choices[['field_name', 'select_choices_or_calculations']])

# Count how many options are possible for each variable
variables_with_choices.loc[:, 'num_options'] = variables_with_choices['select_choices_or_calculations'].apply(lambda x: len(str(x).split('|')))

variables_with_choices_df = variables_with_choices[['field_name', 'form_name', 'field_type', 'field_label', 'select_choices_or_calculations', 'num_options']]

# Save variables with choices
variables_with_choices_df.to_csv(f'{root_directory}/results/variables_with_choices_labels.csv', index=False, encoding='utf-8')
#%%
# =============================================================================
# Check the number of labels for the variables of interest 
# =============================================================================
num_labels_br = variables_with_choices[
    (variables_with_choices['field_name'] == 'sex_bio') |
    (variables_with_choices['field_name'] == 'gender') |
    (variables_with_choices['field_name'] == 'comb_1') 
][['field_name', 'select_choices_or_calculations', 'num_options']]

num_labels_br.to_csv(f'{root_directory}/results/num_labels_br.csv', index=False, encoding='utf-8')
#%%
def check_variable_types(metadata_df, variables):
    """
    Checks the types of specific variables using REDCap metadata.
    
    Parameters:
    - metadata_df: pd.DataFrame - DataFrame containing REDCap metadata, including 'field_name' and 'field_type' columns.
    - variables: set - Set of variable names for which we want to check the type.

    Returns:
    - pd.DataFrame - DataFrame with two columns: 'field_name' and 'field_type', containing the types of the requested variables.
    """
    # Filter the metadata to include only the variables of interest
    variables_types = metadata_df[metadata_df['field_name'].isin(variables)][['field_name', 'field_type']]
    
    return variables_types
#%%
def check_missing_variables(variables_set, metadata_df):
    """
    Compares a set of variables with the metadata_df and identifies which variables are missing.

    Parameters:
    - variables_set: set - Set of variables you want to check.
    - metadata_df: pd.DataFrame - DataFrame of the metadata exported from REDCap.

    Returns:
    - dict with lists of missing variables: missing variables, `_complete` variables, `___` variables (checkbox), and `timestamp` variables.
    """
    # Extract the set of variable names from the metadata
    metadata_variables = set(metadata_df['field_name'].unique())

    # Missing variables
    missing_variables = variables_set - metadata_variables

    # Categorize missing variables
    complete_variables = {var for var in missing_variables if var.endswith('_complete')}
    checkbox_variables = {var for var in missing_variables if '___' in var}
    timestamp_variables = {var for var in missing_variables if 'timestamp' in var.lower()}
    other_missing = missing_variables - complete_variables - checkbox_variables - timestamp_variables

    return {
        "complete_variables": list(complete_variables),
        "checkbox_variables": list(checkbox_variables),
        "timestamp_variables": list(timestamp_variables),
        "other_missing": list(other_missing)
    }

#%% 

# Example of a variable set 
variables_set = {
    'sex_bio', 'gender',
    'monthly_income', 'marital_status',
    'height', 'weight', 'timestamp_col'
} 
# Usage 
result = check_missing_variables(variables_set, metadata_df)
#%%
import matplotlib.pyplot as plt
import seaborn as sns

def generate_missing_variables_report(variables_set, metadata_df, output_directory):
    """
    Generates a report of missing variables and visualizes their categories (e.g., _complete, checkbox, timestamp).
    
    Parameters:
    - variables_set: set - Set of variables to check.
    - metadata_df: pd.DataFrame - DataFrame of metadata exported from REDCap.
    - output_directory: str - Directory to save the report and visualizations.
    
    Returns:
    - None: Saves the report and visualizations to the specified directory.
    """
    # Call the function to check missing variables
    result = check_missing_variables(variables_set, metadata_df)

    # Save the missing variables to a CSV report
    pd.DataFrame({key: pd.Series(value) for key, value in result.items()}).to_csv(f'{output_directory}/missing_variables_report.csv', index=False)

    # Plot a bar chart to show the count of missing variables in each category
    missing_counts = {key: len(value) for key, value in result.items()}
    
    plt.figure(figsize=(8, 5))
    plt.bar(missing_counts.keys(), missing_counts.values(), color='skyblue')
    plt.title('Summary of Missing Variables by Category')
    plt.ylabel('Count of Missing Variables')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_directory}/missing_variables_summary.png')
    plt.show()

# Usage
variables_set = (f'{root_directory}/data/differences1.csv')
generate_missing_variables_report(variables_set, metadata_df, f'{root_directory}/results/')
#%%
def visualize_field_type_distribution(metadata_df, output_directory):
    """
    Visualizes the distribution of field types in the REDCap metadata.

    Parameters:
    - metadata_df: pd.DataFrame - DataFrame of metadata exported from REDCap.
    - output_directory: str - Directory to save the visualizations.
    
    Returns:
    - None: Saves the plot as a PNG.
    """
    # Count the occurrences of each field type
    field_type_counts = metadata_df['field_type'].value_counts()

    # Plot the distribution
    plt.figure(figsize=(10, 6))
    sns.barplot(x=field_type_counts.index, y=field_type_counts.values, palette='viridis')
    plt.title('Distribution of Field Types in Metadata')
    plt.xlabel('Field Type')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_directory}/field_type_distribution.png')
    plt.show()

# Usage
visualize_field_type_distribution(metadata_df, f'{root_directory}/results/')

#%%
# 1. Use the core function to check for missing variables

# Load the CSV file containing the variable names
variables_df = pd.read_csv(f'{root_directory}/data/differences1.csv')

# Convert the variable column into a set (assuming variable names are in the first column)
variables_set = set(variables_df.iloc[:, 0])

missing_variables_result = check_missing_variables(variables_set, metadata_df)

# 2. Generate a report and visualization for missing variables
generate_missing_variables_report(variables_set, metadata_df, f'{root_directory}/results/')

# 3. Visualize the distribution of field types
visualize_field_type_distribution(metadata_df, f'{root_directory}/results/')

