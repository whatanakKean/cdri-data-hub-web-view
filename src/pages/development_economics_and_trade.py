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
data = load_data(file_path="src/data/Unpivoted_Datahub_Economic.xlsx", sheet_name="Sheet1")
data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Sidebar components
def sidebar(data):
    return dmc.Stack([
        dmc.Paper([
            dmc.Select(
                label="Select Series Name", 
                id="series-name-dropdown-economic", 
                value='Export, by market', 
                data=[{'label': option, 'value': option} for option in data["Series Name"].dropna().str.strip().unique() if option],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                checkIconPosition="right",
                allowDeselect=False,
            ),
            dmc.Select(
                label="Select Sector", 
                id="sector-dropdown-economic", 
                value='Economic', 
                data=[{'label': option, 'value': option} for option in data["Sector"].dropna().str.strip().unique() if option],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
                style={'display': 'none'},
            ),
            dmc.Select(
                label="Select Sub-Sector (1)", 
                id="subsector-1-dropdown-economic", 
                value='Trade', 
                data=[{'label': option, 'value': option} for option in data["Sub-Sector (1)"].dropna().str.strip().unique()],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
                style={'display': 'none'},
            ),
            dmc.Select(
                label="Select Product", 
                id="product-dropdown-economic", 
                value='Articles of apparel and clothing accessories, knitted or crocheted.', 
                data=[{'label': option, 'value': option} for option in data["Products"].dropna().str.strip().unique()],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
            ),
            dmc.Select(
                label="Select Market", 
                id="market-dropdown-economic", 
                value='All', 
                data=[{'label': option, 'value': option} for option in ['All'] + list(data["Markets"].dropna().str.strip().unique())],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
            ),
            dmc.Select(
                label="Select Indicator", 
                id="indicator-dropdown-economic", 
                value='Value', 
                data=[{'label': option, 'value': option} for option in list(data["Indicator"].dropna().str.strip().unique())],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
            ),
        ], shadow="xs", p="md", radius="md", withBorder=True),
        dmc.Accordion(chevronPosition="right", variant="contained", radius="md", children=[
            dmc.AccordionItem(value="bender", children=[
                dmc.AccordionControl(dmc.Group([html.Div([dmc.Text("Metadata"), dmc.Text("Additional information about the data", size="sm", fw=400, c="dimmed")])]),),
                dmc.AccordionPanel(
                    id="metadata-panel-economic",
                    children=dmc.Text("Bender is a bending unit from the future...", size="sm")
                )
            ])
        ])
    ], gap="xs")

# Page Layout
development_economics_and_trade = dmc.Container([
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
                                    html.Div(id='map-id-economic'),
                                    dmc.Box(
                                        style={"paddingTop": "2px", "paddingBottom": "10px"},
                                        children=[
                                            dmc.Slider(
                                                id="year-slider-economic",
                                                step=1
                                            )
                                        ]
                                    )        
                                ], 
                                value="map"
                            ),
                            dmc.TabsPanel(                               
                                children=[
                                    html.Div(id='graph-id-economic'),
                                ], 
                                value="graph"
                            ),
                            dmc.TabsPanel(html.Div(id='dataview-container-economic'), value="dataview"),
                        ], 
                        value="map",
                    ),
                ], shadow="xs", p="md", radius="md", withBorder=True),
            ], gap="xs"),
            
            dcc.Store(id="selected-point-data-economic"),
            dcc.Store(id="indicator-unit-economic"),
            dmc.Modal(id="info-modal-economic", title="Point Information", children=[
                dmc.Container(id="modal-content-economic")
            ], fullScreen=True)
        ], span={"base": 12, "sm": 9}),
    ]),
], fluid=True, style={'paddingTop': '1rem'})

def create_dataview(dff): 
    return html.Div([
        dag.AgGrid(id='ag-grid-economic', columnDefs=[{"headerName": col, "field": col} for col in dff.columns], rowData=dff.to_dict('records'), style={'height': '400px'}),
        dmc.Button("Download Data", id="download-button-economic", variant="outline", color="#336666", mt="md", style={'marginLeft': 'auto', 'display': 'flex', 'justifyContent': 'flex-end'}),
        dcc.Download(id="download-data-economic")
    ])
    
    
def create_metadata(dff):
    if 'Source' in dff and dff['Source'].dropna().any():  # Check if 'Source' exists and has non-NA values
        return dmc.Text(
            f"Sources: {', '.join(dff['Source'].dropna().unique())}", size="sm"
        )
    return ""


def create_map(dff, series_name, indicator, year, indicator_unit):
    dff = dff[dff["Year"] == int(year)]
    
    if 'Markets' in dff.columns:
        min_value, max_value = dff['Indicator Value'].min(), dff['Indicator Value'].max()
        num_classes = 5

        # Calculate the step size and dynamically create class intervals
        classes = np.linspace(min_value, max_value, num_classes)
        classes = np.round(classes, -4)

        # Create a dynamic color scale based on the classes
        colorscale = ['#a1d99b', '#31a354', '#2c8e34', '#196d30', '#155d2c', '#104d27']
        style = dict(weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7)
        ctg = ["{}+".format(int(cls)) for cls in classes[:-1]] + ["{}+".format(int(classes[-1]))]
        colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale, width=30, height=300, position="bottomright")
    
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
                        html.Div(children=get_info(indicator=indicator, indicator_unit=indicator_unit), id="info-economic", className="info", style={"position": "absolute", "top": "20px", "right": "20px", "zIndex": "1000"}),
                    ],
                    attributionControl=False,
            )],
            style={
                'position': 'relative',
                'zIndex': 0,
            }
        )

    return html.Div([
        dl.Map(
                style={'width': '100%', 'height': '450px'},
                center=[20, 0],
                zoom=6,
                children=[
                    dl.TileLayer(url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
                    html.Div(children=get_info(is_gis=False), className="info", style={"position": "absolute", "top": "20px", "right": "20px", "zIndex": "1000"}),
                ],
                attributionControl=False,
        )],
        style={
            'position': 'relative',
            'zIndex': 0,
        }
    )
        
def create_graph(dff, subsector_1, products, indicator):
    if subsector_1 not in ["Trade"]:
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
            # subtitle=dict(
            #     text=f"Description For {indicator}",
            #     font=dict(color="gray", size=13),
            # ),
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
                text="Produced By: CDRI Data Hub",
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

# Calllback for info on map
@callback(Output("info-economic", "children"), Input('series-name-dropdown-economic', 'value'), Input('indicator-dropdown-economic', 'value'), Input('indicator-unit-economic', 'data'), Input("geojson", "hoverData"))
def info_hover(series_name, indicator, indicator_unit, feature):
    return get_info(series_name=series_name, indicator=indicator, feature=feature, indicator_unit=indicator_unit)


# Callbacks
@callback([Output('graph-id-economic', 'children'), Output('map-id-economic', 'children'), Output('dataview-container-economic', 'children'), Output('metadata-panel-economic', 'children'), Output('indicator-unit-economic', 'data')],
          [Input("sector-dropdown-economic", "value"), Input('series-name-dropdown-economic', 'value'), Input("subsector-1-dropdown-economic", "value"), Input("product-dropdown-economic", "value"),
           Input("indicator-dropdown-economic", "value"), Input("market-dropdown-economic", "value"), Input("year-slider-economic", "value")])
def update_report(sector, series_name, subsector_1, product, indicator, market, year):
    dff = filter_data(data=data, sector=sector, series_name=series_name, subsector_1=subsector_1, indicator=indicator, product=product, market=market)
    indicator_unit = dff['Indicator Unit'].unique()
    return create_graph(dff, subsector_1, product, indicator), create_map(dff, series_name, indicator, year, indicator_unit), create_dataview(dff), create_metadata(dff), indicator_unit.tolist()


@callback(Output("download-data-economic", "data"), Input("download-button-economic", "n_clicks"),
          State('series-name-dropdown-economic', 'value'), State('sector-dropdown-economic', 'value'), State('subsector-1-dropdown-economic', 'value'), 
          State('indicator-dropdown-economic', 'value'), State("market-dropdown-economic", "value"))
def download_data(n_clicks, series_name, sector, subsector_1, indicator, market):
    if n_clicks is None: return dash.no_update
    dff = filter_data(data=data, series_name=series_name, sector=sector, subsector_1=subsector_1, indicator=indicator, market=market)
    return dict(content=dff.to_csv(index=False), filename="data.csv", type="application/csv")

# Callbacks for dynamic dropdown updates
@callback(
    Output('subsector-1-dropdown-economic', 'data'),
    Output('subsector-1-dropdown-economic', 'value'),
    Input('series-name-dropdown-economic', 'value'),
    Input('sector-dropdown-economic', 'value')
)
def update_subsector_1(series_name, sector):
    # Filter data by Sector and Series Name
    filtered_data = data[(data["Sector"] == sector) & (data["Series Name"] == series_name)]

    # Extract unique Sub-Sector (1) values
    subsector_1_options = filtered_data["Sub-Sector (1)"].dropna().str.strip().unique()

    # Prepare dropdown options
    dropdown_options = [{'label': option, 'value': option} for option in subsector_1_options]

    # Set default value if options exist, otherwise None
    default_value = subsector_1_options[0] if subsector_1_options.size > 0 else None
    
    return dropdown_options, default_value

@callback(
    Output('product-dropdown-economic', 'data'),
    Output('product-dropdown-economic', 'value'),
    Output('product-dropdown-economic', 'style'),
    Input('series-name-dropdown-economic', 'value'),
    Input('sector-dropdown-economic', 'value'),
    Input('subsector-1-dropdown-economic', 'value')
)
def update_products(series_name, sector, subsector_1):
    # Get the subsector-2 options based on the sector and subsector-1
    products_options = data[(data["Series Name"] == series_name) & (data["Sector"] == sector) & (data["Sub-Sector (1)"] == subsector_1)]["Products"].dropna().str.strip().unique()
    # Control visibility based on available options
    style = {'display': 'block'} if products_options.size > 0 else {'display': 'none'}
    return [{'label': option, 'value': option} for option in products_options], products_options[0] if products_options.size > 0 else None, style

@callback(
    Output('market-dropdown-economic', 'data'),
    Output('market-dropdown-economic', 'value'),
    Output('market-dropdown-economic', 'style'),
    Input('series-name-dropdown-economic', 'value'),
    Input('sector-dropdown-economic', 'value'),
    Input('subsector-1-dropdown-economic', 'value')
)
def update_markets(series_name, sector, subsector_1):
    # Get the subsector-2 options based on the sector and subsector-1
    market_options = data[(data["Series Name"] == series_name) & (data["Sector"] == sector) & (data["Sub-Sector (1)"] == subsector_1)]["Markets"].dropna().str.strip().unique()
    # Control visibility based on available options
    style = {'display': 'block'} if market_options.size > 0 else {'display': 'none'}
    return [{'label': option, 'value': option} for option in ['All'] + list(market_options)], 'All', style


@callback(
    Output('indicator-dropdown-economic', 'data'),
    Output('indicator-dropdown-economic', 'value'),
    Input('series-name-dropdown-economic', 'value'),
    Input('sector-dropdown-economic', 'value'),
    Input('subsector-1-dropdown-economic', 'value'),
    Input('market-dropdown-economic', 'value'),
    prevent_initial_call=False
)
def update_indicators(series_name, sector, subsector_1, market):
    # Filter data based on the selected filters
    dff = filter_data(data=data, series_name=series_name, sector=sector, subsector_1=subsector_1, market=market)
    
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
    Output('year-slider-economic', 'min'),
    Output('year-slider-economic', 'max'),
    Output('year-slider-economic', 'value'),
    Output('year-slider-economic', 'marks'),
    Input('series-name-dropdown-economic', 'value'),
    Input('sector-dropdown-economic', 'value'),
    Input('subsector-1-dropdown-economic', 'value'),
    Input('indicator-dropdown-economic', 'value'),
    Input('market-dropdown-economic', 'value'),
)
def update_year_slider(series_name, sector, subsector_1, indicator, market):
    # Filter the data based on the selected filters
    dff = filter_data(data=data, series_name=series_name, sector=sector, subsector_1=subsector_1, indicator=indicator, market=market)
    
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

