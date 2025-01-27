import dash
from dash import html, Input, Output, State, callback
import dash_mantine_components as dmc
import pandas as pd
from fuzzywuzzy import process

# Sample dataset
data = {
    "Series Name": ["Rice Production", "Rice Production", "Rice Production"],
    "Province": ["Kampong Cham", "Kandal", "Phnom Penh"],
    "Year": [2020, 2020, 2020],
    "Indicator": ["Area Planted", "Area Planted", "Area Planted"],
    "Indicator Value": [135910, 89459, 7136],
    "Indicator Unit": ["Ha", "Ha", "Ha"]
}

df = pd.DataFrame(data)

# Predefined suggested questions
suggested_questions = [
    "Show rice production in [Province] for [Year].",
    "What is the area planted for rice in [Province]?",
    "Compare rice production between [Province 1] and [Province 2].",
    "List all provinces with rice production data for [Year].",
    "What is the total rice production in [Year]?"
]

# Function to generate suggestions
def generate_suggestions(user_input, suggested_questions):
    matches = process.extract(user_input, suggested_questions, limit=3)
    return [match[0] for match in matches]

# About page with suggestions autocomplete
about_page = dmc.Container(
    [
        html.H1("About Page"),
        html.P("This is the About Page of the CDRI Data Hub."),
        
        # Suggestions dropdown
        dmc.Autocomplete(
            id="suggestions-autocomplete",
            placeholder="Select a suggestion...",
            data=[{"value": question, "label": question} for question in suggested_questions],
            style={"width": "100%", "marginBottom": "20px"}
        ),
        
        # Data table to display results
        dmc.Table(
            id="data-table",
            striped=True,
            highlightOnHover=True,
            style={"marginTop": "20px"}
        )
    ],
    fluid=True,
)

# Callback to update data table based on the selected suggestion
@callback(
    Output("data-table", "children"),
    Input("suggestions-autocomplete", "value")
)
def update_table(selected_suggestion):
    if not selected_suggestion:
        return []
    
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
        filters["Year"] = 2020  # Default to 2020 for this example
    
    # Filter the dataset
    filtered_df = df
    for key, value in filters.items():
        filtered_df = filtered_df[filtered_df[key] == value]
    
    # Convert filtered DataFrame to a Dash table
    if not filtered_df.empty:
        return [
            html.Thead(html.Tr([html.Th(col) for col in filtered_df.columns])),
            html.Tbody([
                html.Tr([html.Td(filtered_df.iloc[i][col]) for col in filtered_df.columns])
                for i in range(len(filtered_df))
            ])
        ]
    else:
        return [html.P("No data found for the selected query.")]