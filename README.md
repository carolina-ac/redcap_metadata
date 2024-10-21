# REDCap Metadata Management and Analysis

This repository contains a script for exporting and analyzing metadata from REDCap using the API. The script enables users to export metadata, count variable types, and generate detailed reports, including the handling of missing variables and the visualization of field type distributions.

## Features

- **Export REDCap Metadata**: Use the REDCap API to extract metadata and store it in CSV format.
- **Count Variable Types**: Functions to count occurrences of each field type within the metadata.
- **Generate Field Type Reports**: Save field names for specific types (e.g., checkbox, descriptive) into CSV files.
- **Check for Missing Variables**: Identify variables that are missing in the metadata and categorize them (_complete, checkbox, timestamp).
- **Missing Variables Report**: Automatically generate CSV reports and visualizations for missing variables.
- **Visualize Field Type Distribution**: Create bar charts to display the distribution of different field types within the metadata.

## Dependencies

```bash
pip install requests pandas matplotlib seaborn
```

These libraries are required for fetching and processing data, as well as generating visualizations.

### Important:
- **Do not forget to add the `config.py` file to your `.gitignore`** to avoid exposing sensitive information like API tokens. 
- An example configuration file (`config.py`) is provided in the directory for reference.