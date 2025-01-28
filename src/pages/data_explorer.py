from dash import html, Input, Output, callback
import dash_mantine_components as dmc
import pandas as pd
from fuzzywuzzy import process
from ..utils.utils import load_data
import dash_ag_grid as dag

# Sample dataset
data = load_data(file_path="src/data/Unpivoted_Datahub_Agri_Latest.xlsx", sheet_name="Sheet1")

# Predefined suggested questions
suggested_questions = [
    "Show rice production in [Province] for [Year].",
    "What is the area planted for rice in [Province]?",
    "Compare rice production between [Province 1] and [Province 2].",
    "List all provinces with rice production data for [Year].",
    "What is the total rice production in [Year]?"
]

# About page with suggestions autocomplete
data_explorer_page = html.Main(
    [
        html.Div(
            style={
                "height": "300px",
                "backgroundImage": "url('./assets/data-explorer-background.jpg')",
                "backgroundSize": "cover",
                "backgroundPosition": "center",
                "display": "flex",
                "flexDirection": "column",
                "justifyContent": "center",
                "alignItems": "flex-start",
                "paddingLeft": "10px",
                "paddingRight": "10px"
            },
            children=[
                dmc.Stack(
                    p="lg",
                    children=[
                        dmc.Title('Data Explorer', order=1, style={'color': 'white', 'fontSize': '2rem'}),
                        dmc.Text("Explore Data, Visualizations, and Spatial Insights with Natural Language", size="xl", style={'color': 'white', 'fontSize': '1rem'}),
                        # Suggestions dropdown
                        dmc.Autocomplete(
                            id="suggestions-autocomplete",
                            placeholder="Select a suggestion...",
                            data=[{"value": question, "label": question} for question in suggested_questions],
                            style={"width": "100%", "marginBottom": "20px"}
                        ),
                    ],
                    className="animate__animated animate__fadeInUp animate__fast"
                )
            ],
        ),
        
        dmc.Container(children=[
            
            # Data table to display results using dash_ag_grid
            dag.AgGrid(
                id="data-table",
                columnDefs=[{"field": col} for col in data.columns],
                rowData=data.to_dict("records"),
                defaultColDef={"resizable": True, "sortable": True, "filter": True},
                style={"height": "400px", "marginTop": "20px"}
            )
        ], fluid=True)
        
    ],
)

# Callback to update data table based on the selected suggestion
@callback(
    Output("data-table", "rowData"),
    Output("data-table", "columnDefs"),
    Input("suggestions-autocomplete", "value")
)
def update_table(selected_suggestion):

    if not selected_suggestion:
        return [], []

    # Extract filters from the selected suggestion
    filters = {}
    if "rice production" in selected_suggestion.lower():
        filters["Series Name"] = "Rice Production"
    if "area planted" in selected_suggestion.lower():
        filters["Indicator"] = "Area Planted"
    
    # Extract province and year from the suggestion
    if "[Province]" in selected_suggestion:
        if "Kampong" in selected_suggestion:
            filters["Province"] = "Kampong Cham"
        elif "Kandal" in selected_suggestion:
            filters["Province"] = "Kandal"
        elif "Phnom Penh" in selected_suggestion:
            filters["Province"] = "Phnom Penh"
    
    if "[Year]" in selected_suggestion:
        filters["Year"] = 2020
    
    # Filter the dataset
    filtered_df = data
    for key, value in filters.items():
        filtered_df = filtered_df[filtered_df[key] == value]
    
    # Convert filtered DataFrame to a format suitable for dash_ag_grid
    if not filtered_df.empty:
        row_data = filtered_df.to_dict("records")
        column_defs = [{"field": col} for col in filtered_df.columns]
        return row_data, column_defs
    else:
        return [], []