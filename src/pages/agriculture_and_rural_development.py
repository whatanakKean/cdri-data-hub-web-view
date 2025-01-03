import json
import dash
from dash import html, dcc, Input, Output, State, callback, callback_context
import dash_mantine_components as dmc
import dash_ag_grid as dag
import plotly.express as px
from ..utils.utils import load_data, get_info, filter_data, style_handle
from dash_iconify import DashIconify
import plotly.graph_objects as go
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash.dependencies import ALL
from dash_extensions.javascript import arrow_function, assign

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
            dmc.Select(
                label="Select Indicator", 
                id="indicator-dropdown", 
                value='Area Planted', 
                searchable=True,
                data=[{'label': option, 'value': option} for option in ['All'] + list(data.columns.unique())],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right"
            ),
        ], shadow="xs", p="md", radius="md", withBorder=True),
        dmc.Accordion(chevronPosition="right", variant="contained", radius="md", children=[
            dmc.AccordionItem(value="bender", children=[
                dmc.AccordionControl(dmc.Group([html.Div([dmc.Text("Metadata"), dmc.Text("Additional information about the data", size="sm", fw=400, c="dimmed")])]),),
                dmc.AccordionPanel(
                    id="metadata-panel",
                    children=dmc.Text("Bender is a bending unit from the future...", size="sm")
                )
            ])
        ])
    ], gap="xs")

# Page Layout
agriculture_and_rural_development = dmc.Container([
    dmc.Grid([
        dmc.GridCol(sidebar(data), span={"base": 12, "sm": 3}),
        dmc.GridCol([
            dmc.Stack([
                dmc.Paper([
                    dmc.Tabs(
                        children=[
                            dmc.TabsList(
                                [
                                    dmc.TabsTab("Map View", leftSection=DashIconify(icon="tabler:map"), value="map"),
                                    dmc.TabsTab("Visualization", leftSection=DashIconify(icon="tabler:chart-bar"), value="graph"),
                                    dmc.TabsTab("Data Hub", leftSection=DashIconify(icon="tabler:database"), value="dataview"),
                                ], 
                                grow="True",
                            ),
                            dmc.TabsPanel(
                                children=[
                                    html.Div(id='map-id'),
                                    dmc.Box(
                                        style={"paddingTop": "10px", "paddingBottom": "10px"},
                                        children=[
                                            dmc.Slider(
                                                id="year-slider",
                                                step=1,
                                                mt="md"
                                            )
                                        ]
                                    )       
                                ], 
                                value="map"
                            ),
                            dmc.TabsPanel(                               
                                children=[
                                    html.Div(id='graph-id'),
                                ], 
                                value="graph"
                            ),
                            dmc.TabsPanel(html.Div(id='dataview-container'), value="dataview"),
                        ], 
                        value="map",
                    ),
                ], shadow="xs", p="md", radius="md", withBorder=True),
            ], gap="xs"),
            
            dcc.Store(id="selected-point-data"),
            dmc.Modal(id="info-modal", title="Point Information", children=[
                dmc.Container(id="modal-content")
            ], fullScreen=True)
        ], span={"base": 12, "sm": 9}),
    ]),
], fluid=True, style={'paddingTop': '1rem'})


    
def create_map(dff, subsector_1, subsector_2, indicator, year):
    

    classes = [0, 1000, 10000, 50000, 100000, 150000, 200000, 250000]
    colorscale = ['#e5f5e0', '#a1d99b', '#31a354', '#2c8e34', '#1f7032', '#196d30', '#155d2c', '#104d27']
    style = dict(weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7)
    ctg = ["{}+".format(cls, classes[i + 1]) for i, cls in enumerate(classes[:-1])] + ["{}+".format(classes[-1])]
    colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale, width=500, height=30, position="bottomleft")
    
    if subsector_1 == "Production":
        dff = dff[dff["Year"] == int(year)]
        with open('./assets/geoBoundaries-KHM-ADM1_simplified.json') as f:
            geojson_data = json.load(f)
        
        for feature in geojson_data['features']:
            country_name = feature['properties']['shapeName']  # Ensure your GeoJSON has the country names
            # Find matching row in the data
            country_data = dff[dff['Province'] == country_name]
            
            if not country_data.empty:
                feature['properties'][indicator] = country_data[indicator].values[0]
            else:
                # Assign None for missing data
                feature['properties'][indicator] = None
        
        # Create geojson.
        geojson = dl.GeoJSON(data=geojson_data,
                            style=style_handle,
                            zoomToBounds=True,
                            zoomToBoundsOnClick=True,
                            hoverStyle = dict(weight=5, color='#666', dashArray=''),
                            hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp=indicator),
                            id="geojson")

        # Return the map component along with the modal
        return html.Div(
            [
                dl.Map(
                    style={'width': '100%', 'height': '450px'},
                    center=[0, 0],
                    zoom=7,
                    children=[
                        dl.TileLayer(url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
                        geojson,
                        colorbar,
                        html.Div(children=get_info(subsector_1, subsector_2, indicator), id="info", className="info", style={"position": "absolute", "top": "20px", "right": "20px", "zIndex": "1000"}),
                    
                    ],
                    attributionControl=False,
                ),
            ],
            style={
                'position': 'relative',
                'zIndex': 0,
            }
        )
    
    elif subsector_1 == "Export":
        dff = dff[dff["Year"] == int(year)]
        with open('./assets/countries.json') as f:
            geojson_data = json.load(f)

        for feature in geojson_data['features']:
            country_name = feature['properties']['name']  # Ensure your GeoJSON has the country names
            # Find matching row in the data
            country_data = dff[dff['Markets'] == country_name]

            if not country_data.empty:
                # Assign data if available
                feature['properties'][indicator] = country_data[indicator].values[0]
            else:
                # Assign None for missing data
                feature['properties'][indicator] = None
        # Create geojson.
        geojson = dl.GeoJSON(data=geojson_data,
                            style=style_handle,
                            zoomToBounds=True,
                            zoomToBoundsOnClick=True,
                            hoverStyle = dict(weight=5, color='#666', dashArray=''),
                            hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp=indicator),
                            id="geojson")
        return html.Div([
            dl.Map(
                    style={'width': '100%', 'height': '450px'},
                    center=[20, 0],  # Centered on the equator, near the Prime Meridian
                    zoom=6,
                    children=[
                        dl.TileLayer(url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
                        geojson, 
                        colorbar,
                        html.Div(children=get_info(subsector_1, subsector_2, indicator), id="info", className="info", style={"position": "absolute", "top": "20px", "right": "20px", "zIndex": "1000"}),
                    ],
                    attributionControl=False,
            )],
            style={
                'position': 'relative',
                'zIndex': 0,
            }
        )
    else:
        return html.Div([
            dl.Map(
                    style={'width': '100%', 'height': '450px'},
                    center=[20, 0],  # Centered on the equator, near the Prime Meridian
                    zoom=6,
                    children=[
                        dl.TileLayer(url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
                    ],
                    attributionControl=False,
            )],
            style={
                'position': 'relative',
                'zIndex': 0,
            }
        )
        


def create_graph(dff,subsector_1, indicator):
    if subsector_1 == "Production":
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
                rangemode='tozero'
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
                text=indicator,
                subtitle=dict(
                    text=f"Description For {indicator}",
                    font=dict(color="gray", size=13),
                ),
            ),
            xaxis=dict(
                tickmode='array',
                tickvals=dff_agg['Year'].unique(),
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

        fig1.add_trace(go.Scatter(
                    x=dff_agg['Year'],
                    y=dff_agg[indicator],
                    mode='lines+markers',
                    name=indicator
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
            )
        ])
    elif subsector_1 == "Export":
        # Group by Year and calculate the sum for the relevant columns
        # dff_agg = dff
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
                rangemode='tozero'
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
                text=indicator,
                subtitle=dict(
                    text=f"Description For {indicator}",
                    font=dict(color="gray", size=13),
                ),
            ),
            xaxis=dict(
                tickmode='array',
                tickvals=dff_agg['Year'].unique(),
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

        # Iterate over each indicator and create a line plot for each country
        fig1.add_trace(go.Scatter(
            x=dff_agg['Year'],
            y=dff_agg[indicator],
            mode='lines+markers',
            name=indicator
        ))


        return html.Div([ 
            dcc.Graph(id="figure-linechart", figure=fig1, config={
                'displaylogo': False,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'custom_image',
                    'height': 500,
                    'width': 800,
                    'scale': 6
                }
            }),
            dmc.Divider(size="sm"),
        ])
    else:
        return html.Div([
            dmc.Text("Visualization is Under Construction", size="lg")
        ], style={'height': '400px', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})


def create_dataview(dff): 
    return html.Div([
        dag.AgGrid(id='ag-grid', columnDefs=[{"headerName": col, "field": col} for col in dff.columns], rowData=dff.to_dict('records'), style={'height': '400px'}),
        dmc.Button("Download Data", id="download-button", variant="outline", color="#336666", mt="md", style={'marginLeft': 'auto', 'display': 'flex', 'justifyContent': 'flex-end'}),
        dcc.Download(id="download-data")
    ])


def create_metadata(dff):
    return dmc.Text(
        f"Sources: {', '.join(dff['Source'].dropna().unique())}", size="sm"
    )


# Callbacks
@callback([Output('graph-id', 'children'), Output('map-id', 'children'), Output('dataview-container', 'children'), Output('metadata-panel', 'children')],
          [Input("sector-dropdown", "value"), Input("subsector-1-dropdown", "value"), Input("subsector-2-dropdown", "value"),
           Input("province-dropdown", "value"), Input("indicator-dropdown", "value"), Input("year-slider", "value")])
def update_report(sector, subsector_1, subsector_2, province, indicator, year):
    dff = filter_data(data, sector, subsector_1, subsector_2, province)
    dff = dff.rename(columns={'Latiude': 'Latitude'})
    
    return create_graph(dff, subsector_1, indicator), create_map(dff, subsector_1, subsector_2, indicator, year), create_dataview(dff), create_metadata(dff)


@callback(Output("download-data", "data"), Input("download-button", "n_clicks"),
          State('sector-dropdown', 'value'), State('subsector-1-dropdown', 'value'), 
          State('subsector-2-dropdown', 'value'), State('province-dropdown', 'value'))
def download_data(n_clicks, sector, subsector_1, subsector_2, province):
    if n_clicks is None: return dash.no_update
    dff = filter_data(data, sector, subsector_1, subsector_2, province)
    return dict(content=dff.to_csv(index=False), filename="data.csv", type="application/csv")

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

# Calllback for info on map
@callback(Output("info", "children"), Input('subsector-1-dropdown', 'value'), Input('subsector-2-dropdown', 'value'), Input('indicator-dropdown', 'value'), Input("geojson", "hoverData"))
def info_hover(subsector_1, subsector_2, indicator, feature):
    return get_info(subsector_1=subsector_1, subsector_2=subsector_2, indicator=indicator, feature=feature)


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
    
    # Extract valid indicator columns
    indicator_columns = [col for col in dff.columns if col not in [
        'Sector', 'Sub-Sector (1)', 'Sub-Sector (2)', 'Province', 'Series Code', 
        'Series Name', 'Area planted unit', 'Area Harvested Unit', 'Year',
        'Yield Unit', 'Quantity Harvested Unit', 'Latiude', 'Longitude', 
        'Source', 'Quantity Unit', 'Value Unit', 'Pro code', 'Markets'
    ]]
    
    # If no indicators are available, return empty data and value
    if not indicator_columns:
        return [], None
    
    # Prepare options for dropdown
    indicator_options = [{'label': col, 'value': col} for col in indicator_columns]
    
    # Default value as first indicator
    default_value = indicator_columns[0] if indicator_columns else None
    
    return indicator_options, default_value

@callback(
    Output('year-slider', 'min'),
    Output('year-slider', 'max'),
    Output('year-slider', 'value'),
    Output('year-slider', 'marks'),
    Input('sector-dropdown', 'value'),
    Input('subsector-1-dropdown', 'value'),
    Input('subsector-2-dropdown', 'value'),
    Input('province-dropdown', 'value')
)
def update_year_slider(sector, subsector_1, subsector_2, province):
    # Filter the data based on the selected filters
    dff = filter_data(data, sector, subsector_1, subsector_2, province)
    
    # Get the unique years available after filtering
    year_options = dff["Year"].dropna().unique()
    
    # If no years are available, return default values
    if not year_options.size:
        return 0, 0, 0, []
    
    # Get the minimum and maximum years
    min_year = int(year_options.min())
    max_year = int(year_options.max())
    
    # Prepare the marks for the slider based on the available years
    marks = [{'value': year, 'label': str(year)} for year in range(min_year, max_year + 1)]
    
    # Default value for the `year-slider` (min value)
    year_slider_value = max_year
    
    # Return the updated properties for the year-slider
    return min_year, max_year, year_slider_value, marks

