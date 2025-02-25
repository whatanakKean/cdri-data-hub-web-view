import pandas as pd
from dash_extensions.javascript import assign
from dash import html

# Geojson rendering logic, must be JavaScript as it is executed in clientside.
style_handle = assign("""function(feature, context) {
    const {classes, colorscale, style, colorProp} = context.hideout;  // get props from hideout
    const value = feature.properties[colorProp];  // get value that determines the color
    
    if (value === null || value === undefined) {
        // If the value is None (null or undefined), set no color (transparent)
        style.fillColor = null;  // or style.fillColor = 'transparent';
    } else if (value === 0) {
        // If value is 0, set the color to white (or any other color you want for 0 values)
        style.fillColor = '#ffffff';  // This ensures 0 values are white and no hover color change
    } else {
        // Otherwise, check the classes and apply the colorscale for non-zero values
        for (let i = 0; i < classes.length; ++i) {
            if (value > classes[i]) {
                style.fillColor = colorscale[i];  // set the fill color according to the class
            }
        }
    }
    return style;
}""")

def get_info(series_name=None, indicator=None, indicator_unit=None, feature=None, year=None, is_gis=None):
    year_text = f" in {year}" if year else ""
    if is_gis is not None:
        return [html.H4(f"GIS is not available for this dataset!")]
    
    header = [html.H4(f"")]
    
    if series_name is not None:
        header = [html.H4(f"Cambodia {series_name} {year_text}")]

    if not feature:
        return header + [html.P("Hover over a location")]
    else:
        
        # Check if the feature contains either 'name' or 'shapeName'
        feature_name = feature["properties"].get("name") or feature["properties"].get("shapeName")
        
        # If neither 'name' nor 'shapeName' exists, handle it gracefully
        if not feature_name:
            return header + [html.P("No valid name available for this feature")]

        # Handle missing indicator data
        if feature["properties"].get(indicator) is None:
            return header + [html.B(feature_name), html.Br(), "No data available"]
        
        # Return the information with the indicator value and year (if given)
        return header + [html.B(feature_name), html.Br(),
                         f"{indicator}: {feature['properties'][indicator]:,.0f} {indicator_unit[0]}", html.Br()]


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
def filter_data(data, sector=None, subsector_1=None, subsector_2=None, province=None, indicator=None, product=None, market=None, series_name=None, grade=None, occupation=None, year=None):
    # Filter by Sector, Sub-Sector (1), and Sub-Sector (2)
    filtered_data = data
    if sector is not None:
        filtered_data = filtered_data[(filtered_data["Sector"] == sector)]
    
    # Filter by Indicator if provided
    if series_name is not None:
        filtered_data = filtered_data[filtered_data["Series Name"] == series_name] 
    
    if subsector_1 is not None:
        filtered_data = filtered_data[filtered_data["Sub-Sector (1)"] == subsector_1]
    
    if indicator is not None:
        filtered_data = filtered_data[filtered_data["Indicator"] == indicator]
    
    if subsector_2 is not None:
        filtered_data = filtered_data[filtered_data["Sub-Sector (2)"] == subsector_2]
    
    if product is not None:
        filtered_data = filtered_data[filtered_data["Products"] == product] 
    
    if market is not None and market != 'All':
        filtered_data = filtered_data[filtered_data["Markets"] == market] 
    
    if grade is not None and grade != 'All':
        filtered_data = filtered_data[filtered_data["Grade"] == grade] 
        
    if occupation is not None:
        filtered_data = filtered_data[filtered_data["Occupation"] == occupation] 
    
    if year is not None:
        filtered_data = filtered_data[filtered_data["Year"] == year] 

    # Drop columns that are entirely NaN
    filtered_data = filtered_data.dropna(axis=1, how='all')

    # Filter by Province if not 'All'
    if province is None:
        return filtered_data
    if province != 'All':
        filtered_data = filtered_data[filtered_data["Province"] == province]
    

    return filtered_data




## Display Modal
# @callback(
#     [Output("info-modal", "opened"), Output("info-modal", "title"), Output("modal-content", "children")],
#     [Input("geojson", "clickData")],State('sector-dropdown', 'value'), State('subsector-1-dropdown', 'value'), 
#           State('subsector-2-dropdown', 'value'), State('province-dropdown', 'value'),
#     prevent_initial_call=True  # Prevents callback execution on load
# )
# def display_modal(feature, sector, subsector_1, subsector_2, province):
#     dff = filter_data(data, sector, subsector_1, subsector_2, province)
    
#     if feature is None:
#         raise dash.exceptions.PreventUpdate
    
#     style = {
#         "border": f"1px solid {dmc.DEFAULT_THEME['colors']['indigo'][4]}",
#         "textAlign": "center",
#     }
#     # Modal content
#     content = [
#         dmc.Grid(
#             children=[
#                 dmc.GridCol(html.Div("span=4", style=style), span="auto"),
#                 dmc.GridCol(html.Div("span=4", style=style), span=4),
#                 dmc.GridCol(html.Div("span=4", style=style), span="auto"),
#             ],
#             gutter="xl",
#         ),
#         create_dataview(dff)
#     ]

#     return True,f"{sector}: {subsector_2} {subsector_1} ", content 