import dash
from dash import html, dcc, Input, Output, State, callback, callback_context
import dash_mantine_components as dmc
import dash_ag_grid as dag
import plotly.express as px
from ..utils.load_data import load_data
from dash_iconify import DashIconify
import plotly.graph_objects as go
import dash_leaflet as dl
from dash.dependencies import ALL
import os 

# Load data
data = load_data(file_path="src/data/Datahub_Agri_Latest.xlsx", sheet_name="Database")

# Sidebar components
def sidebar(data):
    return dmc.Stack([
        dmc.Paper([
            dmc.Select(
                label="Select Sector", 
                id="sector-dropdown", 
                value='Agriculture', 
                searchable=True,
                data=[{'label': option, 'value': option} for option in data["Sector"].dropna().str.strip().unique()],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                checkIconPosition="right"
            ),
            dmc.Select(
                label="Select Sub-Sector (1)", 
                id="subsector-1-dropdown", 
                value='Production', 
                searchable=True,
                data=[{'label': option, 'value': option} for option in data["Sub-Sector (1)"].dropna().str.strip().unique()],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right"
            ),
            dmc.Select(
                label="Select Sub-Sector (2)", 
                id="subsector-2-dropdown", 
                value='Rice', 
                searchable=True,
                data=[{'label': option, 'value': option} for option in data["Sub-Sector (2)"].dropna().str.strip().unique()],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right"
            ),
            dmc.Select(
                label="Select Province", 
                id="province-dropdown", 
                value='All', 
                searchable=True,
                data=[{'label': option, 'value': option} for option in ['All'] + list(data["Province"].dropna().str.strip().unique())],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right"
            ),
            dmc.MultiSelect(
                label="Select Indicators", 
                id="indicator-dropdown", 
                value=["Area Planted"],
                data=[{'label': option, 'value': option} for option in list(data.columns.unique())],  # Populate options dynamically
                clearable=True,
                searchable=True,
                maxDropdownHeight=200,
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                placeholder="Select one or more indicators"
            )
        ], shadow="xs", p="md", radius="md", withBorder=True),
        dmc.Accordion(chevronPosition="right", variant="contained", radius="md", children=[
            dmc.AccordionItem(value="bender", children=[
                dmc.AccordionControl(dmc.Group([html.Div([dmc.Text("Metadata"), dmc.Text("Bender Bending Rodríguez", size="sm", fw=400, c="dimmed")])]),),
                dmc.AccordionPanel(dmc.Text("Bender is a bending unit from the future...", size="sm"))
            ])
        ])
    ])

# Data filter function
def filter_data(data, sector, subsector_1, subsector_2, province):
    filtered_data = data[(data["Sector"] == sector) & (data["Sub-Sector (1)"] == subsector_1) & (data["Sub-Sector (2)"] == subsector_2)]
    filtered_data = filtered_data.dropna(axis=1, how='all')
    
    # Filter Province
    if province != 'All':
        filtered_data = filtered_data[filtered_data["Province"] == province]

    return filtered_data

# Page Layout
agriculture_and_rural_development = dmc.Container([
    dmc.Grid([
        dmc.GridCol(sidebar(data), span={"base": 12, "sm": 3}),
        dmc.GridCol([
            dmc.Paper([
                dmc.Tabs(
                    children=[
                        dmc.TabsList([
                            dmc.TabsTab("Map View", leftSection=DashIconify(icon="tabler:map"), value="map"),
                            dmc.TabsTab("Visualization", leftSection=DashIconify(icon="tabler:chart-bar"), value="graph"),
                            dmc.TabsTab("Data Hub", leftSection=DashIconify(icon="tabler:database"), value="dataview"),
                        ], grow="True"),
                        dmc.TabsPanel(html.Div(id='map-id'), value="map"),
                        dmc.TabsPanel(html.Div(id='graph-id'), value="graph"),
                        dmc.TabsPanel(html.Div(id='dataview-container'), value="dataview"),
                ], value="map"),
            ], shadow="xs", p="md", radius="md", withBorder=True),
            dcc.Store(id="selected-point-data"),
            dmc.Modal(id="info-modal", title="Point Information", children=[
                dmc.Text(id="modal-content")
            ], size="lg")
        ], span={"base": 12, "sm": 9}),
    ]),
], fluid=True, style={'paddingTop': '1rem'})

def create_map(dff):
    sub_sector_2_to_image = {
        "Rice": "noto--sheaf-of-rice.png",
        "Corn": "emojione--ear-of-corn.png",
        "Cassava": "casava.png",
        "Vegetable": "vegetable.png",
        "Caffee": "openmoji--roasted-coffee-bean.png",
        "Rubber": "rubber.png",
        "Pepper": "chilli.png",
        "Tea": "green-tea.png",
        "Sugarcane": "sugar-cane.png",
        "Longan": "longan.png",
        "Lychee": "lychee.png",
        "Banana": "bananas.png",
        "Dragon Fruit": "dragon-fruit.png",
        "Cashew Nut": "peanut.png",
        "Chillies": "chilli.png",
        "Mango": "mango.png",
        "African Oil Palm": "palm-oil.png",
        "Sweet Potato": "sweet-potato.png",
        "Peanut": "peanut.png",
        "Vigna Radiata": "peas.png",
        "Buffalo": "fluent-emoji--water-buffalo.png",
        "Cattle": "fluent-emoji-flat--cow.png",
        "Pig": "fxemoji--pigside.png",
        "Poultry": "chicken.png"
    }
    
    # Check if Latitude and Longitude columns are present
    if 'Latitude' not in dff.columns or 'Longitude' not in dff.columns:
        markers = []  # No markers if coordinates are missing
    else:
        # Create markers for each data point
        markers = [
            dl.Marker(
                id={"type": "marker", "index": index},
                position=[row['Latitude'], row['Longitude']],
                children=dl.Tooltip(f"{row['Province']}"),
                icon=dict(
                    iconUrl=f"./assets/agricuture_icons/{sub_sector_2_to_image[row['Sub-Sector (2)']]}",  # URL of your custom icon
                    iconSize=[30, 30],  # Icon size (width, height)
                    iconAnchor=[15, 30],  # The anchor point of the icon (relative to iconSize)
                    popupAnchor=[0, -30]  # Position of the popup relative to the icon
                )
            ) for index, row in dff.iterrows()
        ]

    # Return the map component along with the modal
    return html.Div(
        [
            dl.Map(
                style={'width': '100%', 'height': '450px'},
                center=[12.5657, 104.9910],
                zoom=7,
                children=[
                    dl.TileLayer(url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"),
                    dl.LayerGroup(markers)
                ],
                attributionControl=False,
            ),
        ],
        style={
            'position': 'relative',
            'zIndex': 0,
        }
    )

def create_graph(dff, indicator):
    # Check if the DataFrame is empty or if required columns are missing
    if dff.empty or not all(col in dff.columns for col in ['Year', 'Area Harvested', 'Quantity Harvested', 'Yield']):
        return html.Div([
            dmc.Text("Visualization is Under Construction", size="lg")
        ], style={'height': '400px', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})
    
    # Group by Year and calculate the sum for the relevant columns
    dff_agg = dff.groupby('Year')[indicator].sum().reset_index()

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
        title=dict(
            text=", ".join(indicator),
            subtitle=dict(
                text=f"Description For {', '.join(indicator)}",
                font=dict(color="gray", size=13),
            ),
        ),
        xaxis=dict(
            tickmode='array',
            tickvals=dff_agg['Year'].unique()
        ),
        annotations=[ 
            dict(
                x=0.5,
                y=-0.15, 
                xref="paper", yref="paper",
                text="Source: CDRI Data Hub",
                showarrow=False,
                font=dict(size=12, color='rgba(0, 0, 0, 0.7)'),
                align='center'
            ),
        ],
        margin=dict(t=100, b=80, l=50, r=50),
    )
    fig1 = go.Figure(layout=layout)

    # Add line plot for 'Area Harvested'
    for idx, item in enumerate(indicator):
        if item in dff_agg.columns:
            fig1.add_trace(go.Scatter(
                x=dff_agg['Year'],
                y=dff_agg[item],
                mode='lines+markers',
                name=item
            ))

    return html.Div([ 
        dcc.Graph(id="figure-linechart", figure=fig1, config={
            'displaylogo': False,
            'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'custom_image',
                    'height': 500,
                    'width': 800,
                    'scale':6
                }
            }
        ),
        dmc.Divider(size="sm"),
    ])

def create_dataview(dff): 
    return html.Div([
        dag.AgGrid(id='ag-grid', columnDefs=[{"headerName": col, "field": col} for col in dff.columns], rowData=dff.to_dict('records'), style={'height': '400px'}),
        dmc.Button("Download Data", id="download-button", variant="outline", color="green", className="mt-3"),
        dcc.Download(id="download-data")
    ])

# Callbacks
@callback([Output('graph-id', 'children'), Output('map-id', 'children'), Output('dataview-container', 'children')],
          [Input("sector-dropdown", "value"), Input("subsector-1-dropdown", "value"), Input("subsector-2-dropdown", "value"),
           Input("province-dropdown", "value"), Input("indicator-dropdown", "value")])
def update_report(sector, subsector_1, subsector_2, province, indicator):
    dff = filter_data(data, sector, subsector_1, subsector_2, province)
    dff = dff.rename(columns={'Latiude': 'Latitude'})
    return create_graph(dff, indicator), create_map(dff), create_dataview(dff)

@callback(Output("download-data", "data"), Input("download-button", "n_clicks"),
          State('sector-dropdown', 'value'), State('subsector-1-dropdown', 'value'), 
          State('subsector-2-dropdown', 'value'), State('province-dropdown', 'value'))
def download_data(n_clicks, sector, subsector_1, subsector_2, province):
    if n_clicks is None: return dash.no_update
    dff = filter_data(data, sector, subsector_1, subsector_2, province)
    return dict(content=dff.to_csv(index=False), filename="data.csv", type="application/csv")


@callback(
    [Output("info-modal", "opened"), Output("modal-content", "children")],
    Input({"type": "marker", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def manage_modal(n_clicks):
    ctx = callback_context

    # Get the clicked marker ID and ensure it's valid
    if not ctx.triggered_id or 'index' not in ctx.triggered_id:
        return False, ""

    # Check for clicks on markers
    clicked_index = ctx.triggered_id['index']
    if not any(n_clicks):
        return False, ""

    return True, f"Marker {clicked_index} was clicked!"



# Callbacks for dynamic dropdown updates
@callback(
    Output('subsector-1-dropdown', 'data'),
    Output('subsector-1-dropdown', 'value'),
    Input('sector-dropdown', 'value')
)
def update_subsector_1(sector):
    subsector_1_options = data[data["Sector"] == sector]["Sub-Sector (1)"].dropna().str.strip().unique()
    return [{'label': option, 'value': option} for option in subsector_1_options], subsector_1_options[0] if subsector_1_options.size > 0 else None

@callback(
    Output('subsector-2-dropdown', 'data'),
    Output('subsector-2-dropdown', 'value'),
    Input('sector-dropdown', 'value'),
    Input('subsector-1-dropdown', 'value')
)
def update_subsector_2(sector, subsector_1):
    # Get the subsector-2 options based on the sector and subsector-1
    subsector_2_options = data[(data["Sector"] == sector) & (data["Sub-Sector (1)"] == subsector_1)]["Sub-Sector (2)"].dropna().str.strip().unique()
    return [{'label': option, 'value': option} for option in subsector_2_options], subsector_2_options[0] if subsector_2_options.size > 0 else None

@callback(
    Output('province-dropdown', 'data'),
    Output('province-dropdown', 'value'),
    Input('sector-dropdown', 'value'),
    Input('subsector-1-dropdown', 'value'),
    Input('subsector-2-dropdown', 'value')
)
def update_province(sector, subsector_1, subsector_2):
    # Get the province options based on the sector, subsector-1, and subsector-2
    province_options = data[(data["Sector"] == sector) & 
                             (data["Sub-Sector (1)"] == subsector_1) & 
                             (data["Sub-Sector (2)"] == subsector_2)]["Province"].dropna().str.strip().unique()
    return [{'label': option, 'value': option} for option in ['All'] + list(province_options)], 'All'

@callback(
    Output('indicator-dropdown', 'data'),
    Output('indicator-dropdown', 'value'),
    Input('sector-dropdown', 'value'),
    Input('subsector-1-dropdown', 'value'),
    Input('subsector-2-dropdown', 'value'),
    Input('province-dropdown', 'value')
)
def update_indicators(sector, subsector_1, subsector_2, province):
    # Filter data based on the selected filters
    dff = filter_data(data, sector, subsector_1, subsector_2, province)
    
    indicator_columns = [col for col in dff.columns if col not in ['Sector', 'Sub-Sector (1)', 'Sub-Sector (2)', 'Province', 'Series Code','Series Name', 'Area planted unit', 'Area Harvested Unit', 'Year','Yield Unit', 'Quantity Harvested Unit', 'Latiude', 'Longitude', 'Source', 'Quantity Unit', 'Value Unit', 'Pro code']]
    
    # If no indicators are available, return an empty list
    if not indicator_columns:
        return [], []
    
    # Prepare the options for the multi-select dropdown
    indicator_options = [{'label': col, 'value': col} for col in indicator_columns]
    
    # Default value is the first indicator (if available)
    default_value = indicator_columns[0] if indicator_columns else []
    
    return indicator_options, [default_value]
