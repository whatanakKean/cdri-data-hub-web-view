
import sqlite3
from dash import html, dcc, Input, Output, State, callback
import dash
import dash_mantine_components as dmc
import dash_ag_grid as dag
import pandas as pd
from ..utils.utils import get_info, filter_data, style_handle
from dash_iconify import DashIconify
import plotly.graph_objects as go
from fuzzywuzzy import process
import plotly.express as px
import numpy as np

# Sample dataset
conn = sqlite3.connect("./src/data/data.db")
query = """
SELECT * FROM economic_data
UNION ALL
SELECT * FROM agriculture_data;
"""
data = pd.read_sql_query(query, conn)

# Predefined suggested questions
suggested_questions = [
    "Show rice production yield in Battambang.",
    "What is the area planted for rice in Kandal?"
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
                        dmc.Title('Data Hub Explorer', order=1, style={'color': 'white', 'fontSize': '2rem'}),
                        dmc.Text("Explore Data and Visualizations with Natural Language", size="xl", style={'color': 'white', 'fontSize': '1rem'}),
                        # Suggestions dropdown
                        dmc.Autocomplete(
                            id="suggestions-autocomplete",
                            placeholder="Ask anything...",
                            leftSection=DashIconify(icon="mingcute:ai-fill"),
                            data=[{"value": question, "label"   : question} for question in suggested_questions],
                            style={"width": "100%", "marginBottom": "20px"},
                        ),
                        # dmc.Box(
                        #     dmc.Button(
                        #         "Data Catalog",
                        #         variant="outline",
                        #         leftSection=DashIconify(icon="tdesign:data"),
                        #         color="white",
                        #         id="data-catalog-button",
                        #     )
                        # ),
                        dmc.Modal(
                            id="data-catalog-modal",
                            title="Data Catalog",
                            children=[
                                dmc.Text("data-catalog-modal-body"),
                            ],
                            fullScreen=True
                        )
                    ],
                    className="animate__animated animate__fadeInUp animate__fast"
                )
            ],
        ),
        
        dmc.Container(children=[
            dmc.Paper([
                dmc.Tabs(
                    children=[
                        dmc.TabsList(
                            [
                                dmc.TabsTab("Visualization", leftSection=DashIconify(icon="tabler:chart-bar"), value="graph"),
                                dmc.TabsTab("Data Hub", leftSection=DashIconify(icon="tabler:database"), value="dataview"),
                            ], 
                            grow="True",
                        ),
                        dmc.TabsPanel(                               
                            children=[
                                html.Div(id='data-explorer-graph-id'),
                            ], 
                            value="graph"
                        ),
                        dmc.TabsPanel(html.Div(id='data-explorer-dataview-id'), value="dataview"),
                    ], 
                    value="graph",
                ),
                ], shadow="xs", p="md", radius="md", withBorder=True),
        ], fluid=True),
        dcc.Store(id='data-explorer-filter-state')
    ],
)

def create_dataview(dff):
    dff = dff.dropna(axis=1, how='all')
    pivoted_data = dff.pivot_table(
        index=[col for col in dff.columns if col not in ['Indicator', 'Indicator Value']],
        columns='Indicator',
        values='Indicator Value',
        aggfunc='first'
    ).reset_index()
    
    return html.Div([
        dag.AgGrid(id='data-explorer-ag-grid', columnDefs=[{"headerName": col, "field": col} for col in pivoted_data.columns], rowData=pivoted_data.to_dict('records'), style={'height': '400px'}),
        dmc.Button("Download Data", id="data-explorer-download-button", variant="outline", color="#336666", mt="md", style={'marginLeft': 'auto', 'display': 'flex', 'justifyContent': 'flex-end'}),
        dcc.Download(id="data-explorer-download-data")
    ])

        
def create_graph(dff):
    # Aggregate data
    dff_filtered = dff.groupby('Year')['Indicator Value'].sum().reset_index()
    series_name = dff['Series Name'].unique()[0]
    indicator = dff['Indicator'].unique()[0]
    
    print(">> ", dff['Indicator'].unique())

    # Define layout
    layout = go.Layout(
        images=[dict(
            source="./assets/CDRI Logo.png",
            xref="paper", yref="paper",
            x=1, y=1.1,
            sizex=0.2, sizey=0.2,
            xanchor="right", yanchor="bottom"
        )],
        yaxis=dict(
            gridcolor='rgba(169, 169, 169, 0.7)',
            showgrid=True,
            gridwidth=0.5,
            griddash='dot',
            tickformat=',',
            rangemode='tozero',
            title=f"{indicator} ({dff['Indicator Unit'].unique()[0]})",
        ),
        font=dict(
            family='BlinkMacSystemFont',
            color='rgba(0, 0, 0, 0.7)'
        ),
        hovermode="x unified",
        plot_bgcolor='white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="right",    
            x=1
        ),
        xaxis=dict(
            tickmode='array',
            tickvals=dff_filtered['Year'].unique(),
            title="Produced By: CDRI Data Hub",
        ),
        margin=dict(t=100, b=80, l=50, r=50),
    )

    # Create figure
    fig1 = go.Figure(layout=layout)
    fig1.add_trace(go.Scatter(
        x=dff_filtered['Year'],
        y=dff_filtered['Indicator Value'],
        mode='lines+markers',
        name=indicator
    ))

    fig1.update_layout(
        title=dict(
            text = f"{series_name}: {dff['Indicator'].unique()[0]}" + (f" in {dff['Province'].unique()[0]}" if 'Province' in dff.columns and dff['Province'].nunique() == 1 else "") + (f" to {dff['Markets'].unique()[0]}" if 'Markets' in dff.columns and dff['Markets'].nunique() == 1 else "")
        )
    )

    # Return graph
    return html.Div([ 
            dcc.Graph(
                id="figure-linechart", 
                style={'minHeight': '450px'},
                figure=fig1, 
                config={
                    'displaylogo': False,
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': 'cdri_datahub_viz',
                        'height': 500,
                        'width': 800,
                        'scale': 6
                    },
                },
                responsive=True,
            ),
            dmc.Divider(size="sm"),
        ])


# Callback to update data table based on the selected suggestion
@callback(
    [Output("data-explorer-dataview-id", "children"),
    Output("data-explorer-graph-id", "children"),
    Output("data-explorer-filter-state", "data")],
    Input("suggestions-autocomplete", "value")
)
def update_data(selected_suggestion):
    if not selected_suggestion:
        # Default content when no question is entered
        default_message = dmc.Alert(
            "Please enter a question in the search bar above to explore data visualizations and tables.",
            title="Welcome to the CDRI Data Hub Explorer!",
            color="blue",
            variant="light",
            style={'margin': '20px'}
        )
        return default_message, default_message, {}

    # Extract filters from the selected suggestion
    filters = {}
    
    # Store original and lowercase versions of Series Name
    lower_series_name = {name.lower(): name for name in data['Series Name'].unique() if name is not None}
    match_series_name = process.extractOne(selected_suggestion.lower(), lower_series_name.keys(), score_cutoff=50)
    if match_series_name:
        best_match_lower, score = match_series_name
        filters["Series Name"] = lower_series_name[best_match_lower]
        
    # Store original and lowercase versions of Indicator
    lower_indicator = {name.lower(): name for name in data['Indicator'].unique() if name is not None}
    match_indicator = process.extractOne(selected_suggestion.lower(), lower_indicator.keys(), score_cutoff=50)
    if match_indicator:
        best_match_lower, score = match_indicator
        filters["Indicator"] = lower_indicator[best_match_lower]
    
    # Store original and lowercase versions of Province
    lower_indicator = {name.lower(): name for name in data['Province'].unique() if name is not None}
    match_indicator = process.extractOne(selected_suggestion.lower(), lower_indicator.keys(), score_cutoff=50)
    if match_indicator:
        best_match_lower, score = match_indicator
        filters["Province"] = lower_indicator[best_match_lower]
    
    # Store original and lowercase versions of Markets
    lower_indicator = {name.lower(): name for name in data['Markets'].unique() if name is not None}
    match_indicator = process.extractOne(selected_suggestion.lower(), lower_indicator.keys(), score_cutoff=50)
    if match_indicator:
        best_match_lower, score = match_indicator
        filters["Markets"] = lower_indicator[best_match_lower]
        
    # Store original and lowercase versions of Products
    lower_indicator = {name.lower(): name for name in data['Products'].unique() if name is not None}
    match_indicator = process.extractOne(selected_suggestion.lower(), lower_indicator.keys(), score_cutoff=50)
    if match_indicator:
        best_match_lower, score = match_indicator
        filters["Products"] = lower_indicator[best_match_lower]
    
    # Filter the dataset
    filtered_df = data
    for key, value in filters.items():
        if key in filtered_df.columns:
            # Apply the filter temporarily
            temp_df = filtered_df[filtered_df[key] == value]
            
            if not temp_df.empty:
                # If the filtered data is not empty, apply the filter
                filtered_df = temp_df
    
    # return create_dataview(filtered_df), create_graph(filtered_df), filtered_df.to_dict('records')
    return create_dataview(filtered_df), create_graph(filtered_df), filtered_df.to_dict('records')

@callback(Output("data-explorer-download-data", "data"), Input("data-explorer-download-button", "n_clicks"), State('data-explorer-filter-state', 'data'))
def download_data(n_clicks, filtered_df):
    if n_clicks is None: return dash.no_update
    filtered_df = pd.DataFrame(filtered_df)
    return dict(content=filtered_df.to_csv(index=False), filename="data.csv", type="application/csv")


# Callback to handle opening and closing the modal
@callback(
    Output("data-catalog-modal", "opened"),
    Input("data-catalog-button", "n_clicks"),
    State("data-catalog-modal", "opened"),
    prevent_initial_call=True
)
def toggle_modal(n_clicks, opened):
    if n_clicks:
        return not opened
    return opened