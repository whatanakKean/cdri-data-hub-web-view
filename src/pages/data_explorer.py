
import sqlite3
from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
import dash_ag_grid as dag
import pandas as pd
from ..utils.utils import get_info, filter_data, style_handle
from dash_iconify import DashIconify
import plotly.graph_objects as go
from fuzzywuzzy import process

# Sample dataset
conn = sqlite3.connect("./src/data/data.db")
data = pd.read_sql_query(f"SELECT * FROM agriculture_data;", conn)

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
            dmc.Paper([
                dmc.Tabs(
                    children=[
                        dmc.TabsList(
                            [
                                # dmc.TabsTab("Map View", leftSection=DashIconify(icon="tabler:map"), value="map"),
                                dmc.TabsTab("Visualization", leftSection=DashIconify(icon="tabler:chart-bar"), value="graph"),
                                dmc.TabsTab("Data Hub", leftSection=DashIconify(icon="tabler:database"), value="dataview"),
                            ], 
                            grow="True",
                        ),
                        # dmc.TabsPanel(
                        #     children=[
                        #         html.Div(id='data-explorer-map-id'),
                        #         dmc.Box(
                        #             style={"paddingTop": "2px", "paddingBottom": "10px"},
                        #             children=[
                        #                 dmc.Slider(
                        #                     id="year-slider",
                        #                     step=1
                        #                 )
                        #             ]
                        #         )       
                        #     ], 
                        #     value="map"
                        # ),
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
        ], fluid=True)
    ],
)

def create_dataview(dff):
    # pivoted_data = dff.pivot_table(
    #     index=[col for col in dff.columns if col not in ['Indicator', 'Indicator Value']],
    #     columns='Indicator',
    #     values='Indicator Value',
    #     aggfunc='first'
    # ).reset_index()
    
    return html.Div([
        dag.AgGrid(id='data-explorer-ag-grid', columnDefs=[{"headerName": col, "field": col} for col in dff.columns], rowData=dff.to_dict('records'), style={'height': '400px'}),
        dmc.Button("Download Data", id="download-button", variant="outline", color="#336666", mt="md", style={'marginLeft': 'auto', 'display': 'flex', 'justifyContent': 'flex-end'}),
        # dcc.Download(id="data-explorer-download-data")
    ])

        
def create_graph(dff):
    # Aggregate data
    dff_filtered = dff.groupby('Year')['Indicator Value'].sum().reset_index()
    series_name = dff['Series Name'].unique()[0]
    indicator = dff['Indicator'].unique()[0]

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
        # annotations=[ 
        #     dict(
        #         x=0.5,
        #         y=-0.15, 
        #         xref="paper", yref="paper",
        #         text="Produced By: CDRI Data Hub",
        #         showarrow=False,
        #         font=dict(size=12, color='rgba(0, 0, 0, 0.7)'),
        #         align='center'
        #     ),
        # ],
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
    title_text = f"{series_name}: {dff['Indicator'].unique()[0]}"
    fig1.update_layout(
        title=dict(
            text=title_text,
        ),
    )

    # Return graph
    return html.Div([ 
            dcc.Graph(
                id="figure-linechart", 
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
            dmc.Alert(
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                title="Description",
                color="green"
            ),
        ])

# Callback to update data table based on the selected suggestion
@callback(
    Output("data-explorer-dataview-id", "children"),
    Output("data-explorer-graph-id", "children"),
    Input("suggestions-autocomplete", "value")
)
def update_data(selected_suggestion):

    if not selected_suggestion:
        return [], []

    # Extract filters from the selected suggestion
    filters = {}
    
    # Store original and lowercase versions of Series Name
    lower_series_name = {name.lower(): name for name in data['Series Name'].unique()}
    match_series_name = process.extractOne(selected_suggestion.lower(), lower_series_name.keys(), score_cutoff=50)
    if match_series_name:
        best_match_lower, score = match_series_name
        filters["Series Name"] = lower_series_name[best_match_lower]
        print(">>>>> Series Name Result: ", filters["Series Name"], score)
        
    # Store original and lowercase versions of Indicator
    lower_indicator = {name.lower(): name for name in data['Indicator'].unique()}
    match_indicator = process.extractOne(selected_suggestion.lower(), lower_indicator.keys(), score_cutoff=50)
    if match_indicator:
        best_match_lower, score = match_indicator
        filters["Indicator"] = lower_indicator[best_match_lower]
        print(">>>>> Indicator Result: ", filters["Indicator"], score)
    
    # # Store original and lowercase versions of Markets
    # lower_markets = {name.lower(): name for name in data['Markets'].unique()}
    # match_markets = process.extractOne(selected_suggestion.lower(), lower_markets.keys(), score_cutoff=50)
    # if match_markets:
    #     best_match_lower, score = match_markets
    #     filters["Markets"] = lower_markets[best_match_lower]
    #     print(">>>>> Markets Result: ", filters["Markets"], score)
        
    # # Store original and lowercase versions of Province
    # lower_province = {name.lower(): name for name in data['Province'].unique()}
    # match_province = process.extractOne(selected_suggestion.lower(), lower_province.keys(), score_cutoff=50)
    # if match_province:
    #     best_match_lower, score = match_province
    #     filters["Province"] = lower_province[best_match_lower]
    #     print(">>>>> Province Result: ", filters["Province"], score)
    

    
    # Filter the dataset
    filtered_df = data
    for key, value in filters.items():
        filtered_df = filtered_df[filtered_df[key] == value]
    
    return create_dataview(filtered_df), create_graph(filtered_df)
