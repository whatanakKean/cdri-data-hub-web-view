import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
from ..components.sidebar import sidebar
from ..utils.load_data import load_data
import pandas as pd
import dash_ag_grid as dag
import plotly.graph_objects as go
import plotly.express as px

# Import your data
data = load_data(file_path="src/data/Datahub_Agri_Latest.xlsx", sheet_name="Database")

# Page layout
agriculture_and_rural_development = dbc.Container(
    [
        dbc.Row([ 
            sidebar(data), 
            dbc.Col(
                [
                    # Visualization Tab
                    dcc.Tabs(
                        [
                            dcc.Tab(dcc.Graph(id='graph-id'), label="Visualization"),
                            dcc.Tab(dcc.Graph(id='map-id'), label="Map View"),
                            dcc.Tab(id='dataview-id', label="Data Hub", children=html.Div(id='dataview-container')),
                        ]
                    ),
                ], md=9
            ),
        ]),
    ],
    fluid=True,
)

def create_map(dff):
    fig = px.scatter_map(dff, lat='Latitude', lon='Longitude', hover_name='Province',
                         color_continuous_scale=px.colors.cyclical.IceFire)
    
    # Remove map padding by setting margins to 0
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    
    return fig

def create_graph(dff):
    return go.Figure(data=[go.Line(x=dff['Year'], y=dff['Area Planted'])])

# Create Dataview table
def create_dataview(dff):
    column_defs = [{"headerName": col, "field": col} for col in dff.columns]
    
    table = dag.AgGrid(
        id='ag-grid',
        columnDefs=column_defs,
        rowData=dff.to_dict('records'),
        style={'height': '400px', 'width': '100%'}
    )
    return table

# Callback to update graph, map, and dataview
@callback(
    [Output('graph-id', 'figure'),
     Output('map-id', 'figure'),
     Output('dataview-id', 'children')],
    Input("sector-dropdown", "value"),
    Input("subsector-1-dropdown", "value"),
    Input("subsector-2-dropdown", "value"),
    Input("province-dropdown", "value"),
)
def pin_selected_report(sector, subsector_1, subsector_2, province):
    # Filter the data based on selected inputs
    dff = data[
        (data["Sector"] == sector) & 
        (data["Sub-Sector (1)"] == subsector_1) & 
        (data["Sub-Sector (2)"] == subsector_2)
    ]

    # If province is selected (not 'All'), filter by province too
    if province != 'All':
        dff = dff[dff["Province"] == province]

    dff = dff.fillna('')

    # Rename 'Latiude' to 'Latitude' if necessary
    dff = dff.rename(columns={'Latiude': 'Latitude'}) 

    # Create the table for Dataview
    fig_dataview = create_dataview(dff)
    fig_graph = create_graph(dff)
    fig_map = create_map(dff)

    return fig_graph, fig_map, fig_dataview
