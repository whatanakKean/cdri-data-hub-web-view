import json
import dash
from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
import dash_ag_grid as dag
from ..utils.utils import load_data, get_info, filter_data, style_handle
from dash_iconify import DashIconify
import plotly.graph_objects as go
import dash_leaflet as dl
import dash_leaflet.express as dlx
import numpy as np

# Load data
data = load_data(file_path="src/data/Unpivoted_Datahub_Agri_Latest.xlsx", sheet_name="Sheet1")

# Sidebar components
def sidebar(data):
    return dmc.Stack([
        dmc.Paper([
            dmc.Select(
                label="Select Sector", 
                id="sector-dropdown", 
                value='Agriculture', 
                data=[{'label': option, 'value': option} for option in data["Sector"].dropna().str.strip().unique() if option],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                checkIconPosition="right"
            ),
            dmc.Select(
                label="Select Sub-Sector (1)", 
                id="subsector-1-dropdown", 
                value='Production', 
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
                data=[{'label': option, 'value': option} for option in list(data["Indicator"].dropna().str.strip().unique())],
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
                                        style={"paddingTop": "2px", "paddingBottom": "10px"},
                                        children=[
                                            dmc.Slider(
                                                id="year-slider",
                                                step=1
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
            dcc.Store(id="indicator-unit"),
            dmc.Modal(id="info-modal", title="Point Information", children=[
                dmc.Container(id="modal-content")
            ], fullScreen=True)
        ], span={"base": 12, "sm": 9}),
    ]),
], fluid=True, style={'paddingTop': '1rem'})

def create_dataview(dff): 
    return html.Div([
        dag.AgGrid(id='ag-grid', columnDefs=[{"headerName": col, "field": col} for col in dff.columns], rowData=dff.to_dict('records'), style={'height': '400px'}),
        dmc.Button("Download Data", id="download-button", variant="outline", color="#336666", mt="md", style={'marginLeft': 'auto', 'display': 'flex', 'justifyContent': 'flex-end'}),
        dcc.Download(id="download-data")
    ])
    
    
def create_metadata(dff):
    if 'Source' in dff and dff['Source'].dropna().any():  # Check if 'Source' exists and has non-NA values
        return dmc.Text(
            f"Sources: {', '.join(dff['Source'].dropna().unique())}", size="sm"
        )
    return ""


def create_map(dff, subsector_1, subsector_2, indicator, year, indicator_unit):
    # Filter data for the selected year
    dff = dff[dff["Year"] == int(year)]

    min_value, max_value = dff['Indicator Value'].min(), dff['Indicator Value'].max()
    num_classes = 5

    # Calculate the step size and dynamically create class intervals
    classes = np.linspace(min_value, max_value, num_classes)
    classes = np.round(classes, -4)

    # Create a dynamic color scale based on the classes
    colorscale = ['#a1d99b', '#31a354', '#2c8e34', '#196d30', '#155d2c', '#104d27']
    style = dict(weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7)
    ctg = ["{}+".format(int(cls)) for cls in classes[:-1]] + ["{}+".format(int(classes[-1]))]
    colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale, width=500, height=30, position="bottomleft")
    
    if subsector_1 == "Production":
        with open('./assets/geoBoundaries-KHM-ADM1_simplified.json') as f:
            geojson_data = json.load(f)
        
        # Map indicator values to geojson features
        for feature in geojson_data['features']:
            province_name = feature['properties']['shapeName']  # Ensure correct property for province name
            
            # Find matching row in the filtered data
            province_data = dff[dff['Province'] == province_name]
            
            if not province_data.empty:
                # Assign the indicator value
                feature['properties'][indicator] = province_data['Indicator Value'].values[0]
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
                        html.Div(children=get_info(subsector_1, subsector_2, indicator, indicator_unit), id="info", className="info", style={"position": "absolute", "top": "20px", "right": "20px", "zIndex": "1000"}),
                    
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
        with open('./assets/countries.json') as f:
            geojson_data = json.load(f)
                
        # Map indicator values to geojson features
        for feature in geojson_data['features']:
            province_name = feature['properties']['name']  # Ensure correct property for province name
            
            # Find matching row in the filtered data
            province_data = dff[dff['Markets'] == province_name]
            
            if not province_data.empty:
                # Assign the indicator value
                feature['properties'][indicator] = province_data['Indicator Value'].values[0]
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
                        html.Div(children=get_info(subsector_1, subsector_2, indicator, indicator_unit), id="info", className="info", style={"position": "absolute", "top": "20px", "right": "20px", "zIndex": "1000"}),
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
        
def create_graph(dff, subsector_1, indicator):
    if subsector_1 not in ["Production", "Export"]:
        return html.Div([
            dmc.Text("Visualization is Under Construction", size="lg")
        ], style={'height': '400px', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})

    # Aggregate data
    dff_filtered = dff.groupby('Year')['Indicator Value'].sum().reset_index()


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
            tickvals=dff_filtered['Year'].unique(),
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

    # Create figure
    fig1 = go.Figure(layout=layout)
    fig1.add_trace(go.Scatter(
        x=dff_filtered['Year'],
        y=dff_filtered['Indicator Value'],
        mode='lines+markers',
        name=indicator
    ))

    # Return graph
    return html.Div([ 
        dcc.Graph(id="figure-linechart", figure=fig1, config={
            'displaylogo': False,
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'cdri_datahub_viz',
                'height': 500,
                'width': 800,
                'scale': 6
            }
        }),
        dmc.Divider(size="sm")
    ])



# Callbacks
@callback([Output('graph-id', 'children'), Output('map-id', 'children'), Output('dataview-container', 'children'), Output('metadata-panel', 'children'), Output('indicator-unit', 'data')],
          [Input("sector-dropdown", "value"), Input("subsector-1-dropdown", "value"), Input("subsector-2-dropdown", "value"),
           Input("province-dropdown", "value"), Input("indicator-dropdown", "value"), Input("year-slider", "value")])
def update_report(sector, subsector_1, subsector_2, province, indicator, year):
    dff = filter_data(data, sector, subsector_1, subsector_2, province, indicator)
    dff = dff.rename(columns={'Latiude': 'Latitude'})
    indicator_unit = dff['Indicator Unit'].unique()
    
    return create_graph(dff, subsector_1, indicator), create_map(dff, subsector_1, subsector_2, indicator, year, indicator_unit), create_dataview(dff), create_metadata(dff), indicator_unit.tolist()


@callback(Output("download-data", "data"), Input("download-button", "n_clicks"),
          State('sector-dropdown', 'value'), State('subsector-1-dropdown', 'value'), 
          State('subsector-2-dropdown', 'value'), State('province-dropdown', 'value'), State('indicator-dropdown', 'value'))
def download_data(n_clicks, sector, subsector_1, subsector_2, province, indicator):
    if n_clicks is None: return dash.no_update
    dff = filter_data(data, sector, subsector_1, subsector_2, province, indicator)
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
@callback(Output("info", "children"), Input('subsector-1-dropdown', 'value'), Input('subsector-2-dropdown', 'value'), Input('indicator-dropdown', 'value'), Input('indicator-unit', 'data'), Input("geojson", "hoverData"))
def info_hover(subsector_1, subsector_2, indicator, indicator_unit, feature):
    return get_info(subsector_1=subsector_1, subsector_2=subsector_2, indicator=indicator, feature=feature, indicator_unit=indicator_unit)


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
    Input('province-dropdown', 'value'),
    prevent_initial_call=False
)
def update_indicators(sector, subsector_1, subsector_2, province):
    # Filter data based on the selected filters
    dff = filter_data(data, sector, subsector_1, subsector_2, province)
    
    # Extract unique indicator values
    indicator_values = dff['Indicator'].unique().tolist()
    
    # If no indicators are available, return empty options and value
    if not indicator_values:
        return [], None
    
    # Prepare dropdown options
    indicator_options = [{'label': indicator, 'value': indicator} for indicator in indicator_values]
    
    # Set default value to the first indicator
    default_value = indicator_values[0] if indicator_values else None
    
    return indicator_options, default_value



@callback(
    Output('year-slider', 'min'),
    Output('year-slider', 'max'),
    Output('year-slider', 'value'),
    Output('year-slider', 'marks'),
    Input('sector-dropdown', 'value'),
    Input('subsector-1-dropdown', 'value'),
    Input('subsector-2-dropdown', 'value'),
    Input('province-dropdown', 'value'),
    Input('indicator-dropdown', 'value'),
)
def update_year_slider(sector, subsector_1, subsector_2, province, indicator):
    # Filter the data based on the selected filters
    dff = filter_data(data, sector, subsector_1, subsector_2, province, indicator)
    
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

