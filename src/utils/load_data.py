import pandas as pd

def load_data(file_path="src/data/Datahub_Agri_Latest.xlsx", sheet_name="Database"):
    """
    Reads data from an Excel file into a Pandas DataFrame.

    Parameters:
        file_path (str): The path to the Excel file.
        sheet_name (str): The name of the sheet to read. Default is 'database'.

    Returns:
        pd.DataFrame: A DataFrame containing the data from the specified Excel sheet.
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
