import pandas as pd
from dash_extensions.javascript import assign
from dash import html

# Geojson rendering logic, must be JavaScript as it is executed in clientside.
style_handle = assign("""function(feature, context){
    const {classes, colorscale, style, colorProp} = context.hideout;  // get props from hideout
    const value = feature.properties[colorProp];  // get value the determines the color
    for (let i = 0; i < classes.length; ++i) {
        if (value > classes[i]) {
            style.fillColor = colorscale[i];  // set the fill color according to the class
        }
    }
    return style;
}""")
def get_info(feature=None):
    header = [html.H4("Cambodia Export")]
    
    if not feature:
        return header + [html.P("Hoover over a country")]
    else:
        if feature["properties"].get("quantity") is None:  # Handle missing data
            return header + [html.B(feature["properties"]["name"]), html.Br(), "No data available"]
        return header + [html.B(feature["properties"]["name"]), html.Br(),
                    f"Quantity: {feature['properties']['quantity']} KG", html.Br(),
                    f"Value: {feature['properties']['value']} USD"] 


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


# Data filter function
def filter_data(data, sector, subsector_1, subsector_2, province):
    filtered_data = data[(data["Sector"] == sector) & (data["Sub-Sector (1)"] == subsector_1) & (data["Sub-Sector (2)"] == subsector_2)]
    filtered_data = filtered_data.dropna(axis=1, how='all')
    
    # Filter Province
    if province != 'All':
        filtered_data = filtered_data[filtered_data["Province"] == province]

    return filtered_data