import dash_mantine_components as dmc
import dash
from dash import html, dcc, Input, Output, State, callback, ctx, callback_context
from ..utils.load_data import load_data
import pandas as pd
import dash_ag_grid as dag
import plotly.graph_objects as go
import plotly.express as px
import io
from dash_iconify import DashIconify

# Import your data
data = load_data(file_path="src/data/Datahub_Agri_Latest.xlsx", sheet_name="Database")

# Sidebar components
def sidebar(data):
    indicator_dropdown = dmc.Select(
        label="Select Indicator",
        id="indicator-dropdown",
        data=[{'label': indicator, 'value': indicator} for indicator in data.columns.unique()],
        value='Area Planted',
        clearable=False,
        searchable=True,
        maxDropdownHeight=600,
        style={"marginBottom": "16px"}
    )
    sector_dropdown = dmc.Select(
        label="Select Sector",
        id="sector-dropdown",
        data=[{'label': sector, 'value': sector} for sector in data["Sector"].dropna().unique()],
        value='Agriculture',
        clearable=False,
        searchable=True,
        maxDropdownHeight=600,
        style={"marginBottom": "16px"}
    )

    subsector_1_dropdown = dmc.Select(
        label="Select Sub-Sector (1)",
        id="subsector-1-dropdown",
        data=[{'label': subsector_1, 'value': subsector_1} for subsector_1 in data["Sub-Sector (1)"].dropna().unique()],
        value='Production',
        clearable=False,
        searchable=True,
        maxDropdownHeight=600,
        style={"marginBottom": "16px"}
    )

    subsector_2_dropdown = dmc.Select(
        label="Select Sub-Sector (2)",
        id="subsector-2-dropdown",
        data=[{'label': subsector_2, 'value': subsector_2} for subsector_2 in data["Sub-Sector (2)"].dropna().unique()],
        value='Rice',
        clearable=False,
        searchable=True,
        maxDropdownHeight=600,
        style={"marginBottom": "16px"}
    )

    province_dropdown = dmc.Select(
        label="Select Province",
        id="province-dropdown",
        data=[
            {'label': 'All Provinces', 'value': 'All'},
            *[{'label': province, 'value': province} for province in data["Province"].dropna().unique()]
        ],
        value='All',  # Default value to "All Provinces"
        clearable=False,
        searchable=True,
        maxDropdownHeight=600,
        style={"marginBottom": "16px"}
    )

    control_panel = dmc.Paper(
        [
            sector_dropdown,
            subsector_1_dropdown,
            subsector_2_dropdown,
            indicator_dropdown,
            province_dropdown
        ],
        shadow="xs",
        p="md",
        radius="md",
        withBorder=True,
        style={"marginBottom": "16px"}
    )

    info = dmc.Accordion(
        chevronPosition="right",
        variant="contained",
        radius="md",
        children=[
            dmc.AccordionItem(
                value="bender",
                children=[
                    dmc.AccordionControl(
                        dmc.Group(
                            [
                                html.Div(
                                    [
                                        dmc.Text("Metadata"),
                                        dmc.Text("Fascinated with cooking, though has no sense of taste", size="sm", fw=400, c="dimmed"),
                                    ]
                                ),
                            ]
                        )
                    ),
                    dmc.AccordionPanel(dmc.Text("Bender Bending Rodríguez, (born September 4, 2996), designated Bending Unit 22, and commonly "
                                            "known as Bender, is a bending unit created by a division of MomCorp in Tijuana, Mexico, "
                                            "and his serial number is 2716057. His mugshot id number is 01473. He is Fry's best friend.", size="sm")),
                ]
            )
        ]
    )

    return dmc.Stack([control_panel, info])



agriculture_and_rural_development = dmc.Container(
    [
        dmc.Grid(children=[
            dmc.GridCol(sidebar(data), span={"base": 12, "sm": 3}),
            dmc.GridCol(
                [
                    dmc.Paper(
                        [
                            dmc.Tabs(
                            [
                                dmc.TabsList(
                                    grow=True,
                                    children=[
                                        dmc.TabsTab(
                                            "Map View",
                                            leftSection=DashIconify(icon="tabler:map"),
                                            value="map",
                                        ),
                                        dmc.TabsTab(
                                            "Visalualization",
                                            leftSection=DashIconify(icon="tabler:chart-bar"),
                                            value="graph",
                                        ),
                                        dmc.TabsTab(
                                            "Data Hub",
                                            leftSection=DashIconify(icon="tabler:database"),
                                            value="dataview",
                                        ),
                                        
                                    ]
                                ),
                                dmc.TabsPanel(
                                    dcc.Graph(id='map-id', config={'displaylogo': False}),
                                    value="map",
                                ),
                                dmc.TabsPanel(
                                    dcc.Graph(id='graph-id', config={'displaylogo': False}),
                                    value="graph",
                                ),
                                dmc.TabsPanel(
                                    html.Div(id='dataview-container'),
                                    value="dataview",
                                ),
                            ],
                            value="map",
                            ),
                        ],
                        shadow="xs",
                        p="md",
                        radius="md",
                        withBorder=True,
                        style={"marginBottom": "16px"}
                    ),
                    dcc.Store(id="selected-point-data"),
                    dmc.Modal(
                        id="info-modal",
                        title="Point Information",
                        children=[
                            dmc.Text(id="modal-content"),
                            dmc.Button("Close", id="close-modal", variant="outline", color="red", className="mt-3")
                        ],
                        size="lg",
                    )
                ],
                span={"base": 12, "sm": 9},
            ),
        ]),
    ],
    fluid=True,
    style={'paddingTop': '1rem'}
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
        margin=dict(l=0, r=0, t=0, b=0),
        clickmode="event+select"
    )
    
    return fig

def create_graph(dff):
    # Ensure the correct bar mode and grouping
    fig = px.histogram(
        dff,
        x='Province',
        y='Area Planted',
        color='Year',
        barmode='group',
        title='Title',
        height=400
    )
    
    # Adjust layout to further ensure grouping behavior
    fig.update_layout(
        barmode='group',
        xaxis_title='Province',
        yaxis_title='Area Planted',
        hovermode="x unified",
        title={
            'text': "Title<br><sub>Subtitle describing the data or context</sub>",
            'x': 0.05,
            'xanchor': 'left',
            'y': 0.9
        }
    )
    
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
    download_button = dmc.Button("Download Data", id="download-button", variant="outline", color="green", className="mt-3")
    
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
     Output('dataview-container', 'children')],
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


# Callback to handle the map click and show modal with point data
@callback(
    Output('info-modal', 'opened'),
    Output('modal-content', 'children'),
    Input('map-id', 'clickData'),
    Input('close-modal', 'n_clicks'),
    prevent_initial_call=True
)
def manage_modal(click_data, n_clicks):
    # Get the trigger that called the callback
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    
    # If the trigger is the map click
    if triggered_id == 'map-id' and click_data:
        point_data = click_data['points'][0]
        province = point_data['hovertext']
        latitude = point_data['lat']
        longitude = point_data['lon']
        
        modal_content = f"Province: {province}\nLatitude: {latitude}\nLongitude: {longitude}"
        return True, modal_content  # Open the modal with the data

    # If the trigger is the close button click
    elif triggered_id == 'close-modal' and n_clicks:
        return False, ""  # Close the modal
    
    # Default case if no trigger is pressed
    return False, ""
