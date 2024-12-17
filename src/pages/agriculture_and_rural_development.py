import dash_bootstrap_components as dbc
import dash
from dash import html, dcc, Input, Output, State, callback, ctx
from ..components.sidebar import sidebar
from ..utils.load_data import load_data
import pandas as pd
import dash_ag_grid as dag
import plotly.graph_objects as go
import plotly.express as px
import io

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
                            dcc.Tab(dcc.Graph(id='map-id', config= {'displaylogo': False}), label="Map View"),
                            dcc.Tab(dcc.Graph(id='graph-id', config= {'displaylogo': False}), label="Visualization"),
                            dcc.Tab(id='dataview-id', label="Data Hub", children=html.Div(id='dataview-container')),
                        ]
                    ),
                    dcc.Store(id="selected-point-data"),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("Detail Insight")),
                            dbc.ModalBody(id="modal-body"),
                            dbc.ModalFooter(
                                dbc.Button("Close", id="close-modal", className="ms-auto", n_clicks=0)
                            ),
                        ],
                        id="info-modal",
                        is_open=False,
                        centered=True,
                    ),
                ], md=9
            ),
        ], className="mb-4 mt-2"),
    ],
    fluid=True,
)

def create_map(dff):
    fig = px.scatter_mapbox(dff, lat='Latitude', lon='Longitude', hover_name='Province',
                            color_continuous_scale=px.colors.cyclical.IceFire)
    
    # Enable clicking on points
    fig.update_traces(marker=dict(size=10), mode='markers', selector=dict(type='scattermapbox'))
    
    # Set map style and margins
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(
            zoom=6
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    return fig

def create_graph(dff):
    # Ensure the correct bar mode and grouping
    fig = px.histogram(dff, 
                 x='Province', 
                 y='Area Planted', 
                 color='Year', 
                 barmode='group', 
                 height=400)
    # Adjust layout to further ensure grouping behavior
    fig.update_layout(barmode='group', xaxis_title='Province', yaxis_title='Area Planted')
    return fig
    
def create_dataview(dff):
    # Define the table's column definitions
    column_defs = [{"headerName": col, "field": col} for col in dff.columns]
    
    # Create the ag-Grid table
    table = dag.AgGrid(
        id='ag-grid',
        columnDefs=column_defs,
        rowData=dff.to_dict('records'),
        style={'height': '400px', 'width': '100%'}
    )

    # Create the download button
    download_button = dbc.Button("Download Data", id="download-button", outline=True, color="success", className="mt-3")
    
    # Return the table and button in a layout
    return html.Div([
        table,
        download_button,
        dcc.Download(id="download-data")  # Ensure you have the download component here
    ])

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

# Callback to handle map point click and show modal
@callback(
    [Output("selected-point-data", "data"),
     Output("info-modal", "is_open"),
     Output("modal-body", "children")],
    [Input("map-id", "clickData"),
     Input("close-modal", "n_clicks")],
    [State("info-modal", "is_open")],
)
def show_modal_on_click(click_data, n_close, is_open):
    triggered = ctx.triggered_id
    if triggered == "map-id" and click_data:
        # Extract point information
        point_data = click_data["points"][0]
        hover_text = point_data.get("hovertext", "No details available")
        lat = point_data.get("lat", "N/A")
        lon = point_data.get("lon", "N/A")
        content = f"""
        Hover Text: {hover_text}
        Latitude: {lat}
        Longitude: {lon}
        """
        return point_data, True, content
    
    if triggered == "close-modal":
        return None, False, None
    
    return None, is_open, None

# Callback to handle data download
@callback(
    Output("download-data", "data"),
    Input("download-button", "n_clicks"),
    State('sector-dropdown', 'value'),
    State('subsector-1-dropdown', 'value'),
    State('subsector-2-dropdown', 'value'),
    State('province-dropdown', 'value')
)
def download_data(n_clicks, sector, subsector_1, subsector_2, province):
    if n_clicks is None:
        return dash.no_update

    # Filter the data based on selected inputs
    dff = data[
        (data["Sector"] == sector) & 
        (data["Sub-Sector (1)"] == subsector_1) & 
        (data["Sub-Sector (2)"] == subsector_2)
    ]

    if province != 'All':
        dff = dff[dff["Province"] == province]

    dff = dff.fillna('')

    # Create CSV string for download (no base64 encoding)
    csv_string = dff.to_csv(index=False)

    # Return the content as plain CSV string
    return dict(content=csv_string, filename="data.csv", type="application/csv")