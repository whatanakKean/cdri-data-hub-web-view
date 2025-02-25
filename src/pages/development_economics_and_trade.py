import json
import math
import sqlite3
import dash
from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
import dash_ag_grid as dag
import pandas as pd
from ..utils.utils import get_info, filter_data, style_handle
from dash_iconify import DashIconify
import plotly.graph_objects as go
import dash_leaflet as dl
import dash_leaflet.express as dlx

# Load data
conn = sqlite3.connect("./src/data/data.db")
data = pd.read_sql_query(f"SELECT * FROM economic_data;", conn)

# Sidebar components
def sidebar(data):
    return dmc.Stack([
        dmc.Paper([
            dmc.Select(
                label="Select Dataset", 
                id="series-name-dropdown-economic", 
                value='Export, by market', 
                data=[{'label': option, 'value': option} for option in data["Series Name"].dropna().str.strip().unique() if option],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                checkIconPosition="right",
                allowDeselect=False,
            ),
            dmc.Select(
                label="Select Product", 
                id="product-dropdown-economic", 
                value='Articles of apparel and clothing accessories, knitted or crocheted.', 
                data=[{'label': option, 'value': option} for option in sorted(data["Products"].dropna().str.strip().unique())],
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
                data=[{'label': option, 'value': option} for option in ['All'] + list(sorted(data["Markets"].dropna().str.strip().unique()))],
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
                data=[{'label': option, 'value': option} for option in list(sorted(data["Indicator"].dropna().str.strip().unique()))],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
            ),
            dmc.Select(
                label="Select Year", 
                id="year-dropdown-economic", 
                value=str(int(data["Year"].dropna().unique()[-1])),
        	    data=[{'label': str(int(option)), 'value': str(int(option))} for option in sorted(data["Year"].dropna().unique())],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
            )
        ], id="filter-economic", shadow="xs", p="md", radius="md", withBorder=True),
        
        dmc.Accordion(chevronPosition="right", variant="contained", radius="md", children=[
            dmc.AccordionItem(value="bender", children=[
                dmc.AccordionControl(dmc.Group([html.Div([dmc.Text("Metadata"), dmc.Text("Information about current data", size="sm", fw=400, c="dimmed")])]),),
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
                    # dmc.Autocomplete(
                    #     id="suggestions-autocomplete-economic",
                    #     placeholder="Ask anything...",
                    #     leftSection=DashIconify(icon="mingcute:ai-fill"),
                    #     style={"width": "100%", "marginBottom": "20px"},
                    # ),
                    dmc.Tabs(
                        children=[
                            dmc.TabsList(
                                [
                                    dmc.TabsTab("Map View", leftSection=DashIconify(icon="tabler:map"), value="map"),
                                    dmc.TabsTab("Visualization", leftSection=DashIconify(icon="tabler:chart-bar"), value="graph"),
                                    dmc.TabsTab("Data View", leftSection=DashIconify(icon="tabler:database"), value="dataview"),
                                ], 
                                grow="True",
                            ),
                            dmc.TabsPanel(
                                children=[
                                    html.Div(id='map-id-economic'),        
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
                        id="active-tab-economic", value="map", color="#336666"
                    ),
                ], shadow="xs", p="md", radius="md", withBorder=True),
            ], gap="xs"),
            
            dcc.Store(id="selected-point-data-economic"),
            dcc.Store(id="indicator-unit-economic"),
            dmc.Modal(
                id="info-modal-economic",
                children=[
                    dmc.Text(id="modal-body-economic"),
                ],
                fullScreen=True
            )
        ], span={"base": 12, "sm": 9}),
    ]),
], fluid=True, style={'paddingTop': '1rem'})

def create_dataview(dff): 
    pivoted_data = dff.pivot_table(
        index=[col for col in dff.columns if col not in ['Indicator', 'Indicator Value']],
        columns='Indicator',
        values='Indicator Value',
        aggfunc='first'
    ).reset_index()
    
    return html.Div([
        dag.AgGrid(id='ag-grid-economic', defaultColDef={"filter": True}, columnDefs=[{"headerName": col, "field": col} for col in pivoted_data.columns], rowData=pivoted_data.to_dict('records'), style={'height': '400px'}),
        dmc.Button("Download Data", id="download-button-economic", variant="outline", color="#336666", mt="md", style={'marginLeft': 'auto', 'display': 'flex', 'justifyContent': 'flex-end'}),
        dcc.Download(id="download-data-economic")
    ])
    
    
def create_metadata(dff):
    if 'Source' in dff and dff['Source'].dropna().any():  # Check if 'Source' exists and has non-NA values
        return dmc.Text(
            f"Sources: {', '.join(dff['Source'].dropna().unique())}", size="sm"
        )
    return ""


def create_map(dff, year):
    dff = dff[dff["Year"] == int(year)]
    series_name = dff['Series Name'].unique()[0]
    indicator = dff['Indicator'].unique()[0]
    indicator_unit = dff['Indicator Unit'].unique()[0]
    
    if 'Markets' in dff.columns:
        # Calculate Choropleth Gradient Scale Range
        num_classes = 5
        min_value = dff['Indicator Value'].min()
        max_value = dff['Indicator Value'].max()
        range_value = max_value - min_value

        # Handle the case where range_value is 0
        if range_value == 0:
            classes = [0] * (num_classes + 1)
        else:
            magnitude = 10 ** int(math.log10(range_value))
            if range_value / magnitude < 3:
                rounding_base = magnitude // 2
            else:
                rounding_base = magnitude
            width = math.ceil(range_value / num_classes / rounding_base) * rounding_base
            
            # Start the classes list from 0 and calculate subsequent classes
            classes = [0] + [i * width for i in range(1, num_classes)] + [max_value]
            
            # Round classes to nearest rounding base and remove duplicates
            classes = [math.ceil(cls / rounding_base) * rounding_base for cls in classes]
            classes = sorted(set(classes))

        # Create a dynamic color scale based on the classes
        colorscale = ['#a1d99b', '#31a354', '#2c8e34', '#196d30', '#134e20', '#0d3b17']
        style = dict(weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7)
        ctg = [f"{int(classes[i])}+" for i in range(len(classes))]
        colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale, width=30, height=300, position="bottomright")
    
        with open('./assets/countries.json') as f:
            geojson_data = json.load(f)
                
        # Map indicator values to geojson features
        for feature in geojson_data['features']:
            market_name = feature['properties']['name']  # Ensure correct property for market name
            feature['properties']['Series Name'] = series_name
            feature['properties']['Indicator'] = indicator
            feature['properties']['Year'] = year
            
            # Find matching row in the filtered data
            market_data = dff[dff['Markets'] == market_name]
            
            if not market_data.empty:
                # Assign the indicator value
                feature['properties'][indicator] = market_data['Indicator Value'].values[0]
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
                            id="geojson-economic")
        
        return html.Div([
            dl.Map(
                    style={'width': '100%', 'height': '450px'},
                    center=[20, 0],  # Centered on the equator, near the Prime Meridian
                    zoom=6,
                    children=[
                        dl.TileLayer(url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
                        geojson, 
                        colorbar,
                        html.Div(children=get_info(indicator=indicator, indicator_unit=indicator_unit, year=year), id="info-economic", className="info", style={"position": "absolute", "top": "20px", "right": "20px", "zIndex": "1000"}),
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
        
def create_graph(dff):
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
            color='rgba(0, 0, 0, 0.6)',
            showgrid=True,
            gridwidth=0.5,
            griddash='dot',
            tickformat=',',
            rangemode='tozero',
            title=f"{indicator} ({dff['Indicator Unit'].unique()[0]})",
        ),
        font=dict(
            family='BlinkMacSystemFont, -apple-system, sans-serif',
            color='rgb(24, 29, 31)'
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
            showgrid=False,
            tickmode='auto',
            color='rgba(0, 0, 0, 0.6)',
            tickvals=dff_filtered['Year'].unique(),
            title="<span style='display:block; margin-top:8px; font-size:70%; color:rgba(0, 0, 0, 0.7);'>Produced By: CDRI Data Hub</span>",
        ),
        margin=dict(t=100, b=80, l=50, r=50, pad=10),
    )

    # Create figure
    fig1 = go.Figure(layout=layout)
    fig1.add_trace(go.Scatter(
        x=dff_filtered['Year'],
        y=dff_filtered['Indicator Value'],
        mode='lines+markers' if len(dff_filtered) == 1 else 'lines',
        name=indicator
    ))
    
    fig1.update_layout(
        title=dict(
            text=f"{series_name}: {dff['Indicator'].unique()[0]}",
        ),
    )

    # Return graph
    return html.Div([ 
        dcc.Graph(
            id="figure-linechart", 
            figure=fig1, 
            style={'minHeight': '450px'},
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
        # dmc.Alert(
        #     "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
        #     title="Description",
        #     color="green"
        # ),
    ])


def create_modal(dff, feature):
    indicator = feature['Indicator']
    dff_filtered = dff[dff['Indicator'] == indicator]
    series_name = dff_filtered['Series Name'].unique()[0]

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
            color='rgba(0, 0, 0, 0.6)',
            showgrid=True,
            gridwidth=0.5,
            griddash='dot',
            tickformat=',',
            rangemode='tozero',
            title=f"{indicator} ({dff_filtered['Indicator Unit'].unique()[0]})",
        ),
        font=dict(
            family='BlinkMacSystemFont, -apple-system, sans-serif',
            color='rgb(24, 29, 31)'
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
            tickmode='auto',
            color='rgba(0, 0, 0, 0.6)',
            tickvals=dff_filtered['Year'].unique(),
            title="<span style='display:block; margin-top:8px; font-size:70%; color:rgba(0, 0, 0, 0.7);'>Produced By: CDRI Data Hub</span>",
        ),
        margin=dict(t=100, b=80, l=50, r=50, pad=10),
    )

    # Create figure
    fig1 = go.Figure(layout=layout)
    fig1.add_trace(go.Scatter(
        x=dff_filtered['Year'],
        y=dff_filtered['Indicator Value'],
        mode='lines+markers' if len(dff_filtered) == 1 else 'lines',
        name=indicator
    ))  
    fig1.update_layout(
        title=dict(
            text = f"{series_name}: {dff['Indicator'].unique()[0]}" + (f" in {dff['Province'].unique()[0]}" if 'Province' in dff.columns and dff['Province'].nunique() == 1 else "") + (f" to {dff['Markets'].unique()[0]}" if 'Markets' in dff.columns and dff['Markets'].nunique() == 1 else "")
        )
    )

    # Return graph with the Pie chart selector and line chart
    return html.Div([
        dmc.Divider(size="sm"),
        dcc.Graph(
            id="figure-linechart", 
            figure=fig1, 
            style={'minHeight': '450px'},
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
    ])
    

# Calllback for info on map
@callback(Output("info-economic", "children"), Input('series-name-dropdown-economic', 'value'), Input('year-dropdown-economic', 'value'), Input('indicator-dropdown-economic', 'value'),  Input('indicator-unit-economic', 'data'), Input("geojson-economic", "hoverData"))
def info_hover(series_name, year, indicator, indicator_unit, feature):
    return get_info(series_name=series_name, indicator=indicator, feature=feature, indicator_unit=indicator_unit, year=year)


# Callbacks
@callback([Output('graph-id-economic', 'children'), Output('map-id-economic', 'children'), Output('dataview-container-economic', 'children'), Output('metadata-panel-economic', 'children'), Output('indicator-unit-economic', 'data')],
          [Input('series-name-dropdown-economic', 'value'), Input("product-dropdown-economic", "value"),
           Input("indicator-dropdown-economic", "value"), Input("market-dropdown-economic", "value"), Input("year-dropdown-economic", "value")])
def update_report(series_name, product, indicator, market, year):
    dff = filter_data(data=data, series_name=series_name, indicator=indicator, product=product, market=market)
    indicator_unit = dff['Indicator Unit'].unique()
    return create_graph(dff), create_map(dff, year), create_dataview(dff), create_metadata(dff), indicator_unit.tolist()


@callback(Output("download-data-economic", "data"), Input("download-button-economic", "n_clicks"),
          State('series-name-dropdown-economic', 'value'), State('indicator-dropdown-economic', 'value'), State("market-dropdown-economic", "value"))
def download_data(n_clicks, series_name, indicator, market):
    if n_clicks is None: return dash.no_update
    dff = filter_data(data=data, series_name=series_name, indicator=indicator, market=market)
    return dict(content=dff.to_csv(index=False), filename="data.csv", type="application/csv")

@callback(
    Output('product-dropdown-economic', 'data'),
    Output('product-dropdown-economic', 'value'),
    Output('product-dropdown-economic', 'style'),
    Input('series-name-dropdown-economic', 'value'),
)
def update_products(series_name):
    products_options = data[(data["Series Name"] == series_name)]["Products"].dropna().str.strip().unique()
    # Control visibility based on available options
    style = {'display': 'block'} if products_options.size > 0 else {'display': 'none'}
    return [{'label': option, 'value': option} for option in sorted(products_options)], products_options[0] if products_options.size > 0 else None, style

@callback(
    Output('market-dropdown-economic', 'data'),
    Output('market-dropdown-economic', 'value'),
    Output('market-dropdown-economic', 'style'),
    Input('series-name-dropdown-economic', 'value'),
)
def update_markets(series_name):
    market_options = data[(data["Series Name"] == series_name)]["Markets"].dropna().str.strip().unique()
    # Control visibility based on available options
    style = {'display': 'block'} if market_options.size > 0 else {'display': 'none'}
    return [{'label': option, 'value': option} for option in ['All'] + list(sorted(market_options))], 'All', style


@callback(
    Output('indicator-dropdown-economic', 'data'),
    Output('indicator-dropdown-economic', 'value'),
    Input('series-name-dropdown-economic', 'value'),
    Input('market-dropdown-economic', 'value'),
    prevent_initial_call=False
)
def update_indicators(series_name, market):
    # Filter data based on the selected filters
    dff = filter_data(data=data, series_name=series_name, market=market)
    
    # Extract unique indicator values
    indicator_values = dff['Indicator'].unique().tolist()
    
    # If no indicators are available, return empty options and value
    if not indicator_values:
        return [], None
    
    # Prepare dropdown options
    indicator_options = [{'label': indicator, 'value': indicator} for indicator in sorted(indicator_values)]
    
    # Set default value to the first indicator
    default_value = indicator_values[0] if indicator_values else None
    
    return indicator_options, default_value



@callback(
    Output('year-dropdown-economic', 'data'),
    Output('year-dropdown-economic', 'value'),
    Output('year-dropdown-economic', 'style'),
    Input('series-name-dropdown-economic', 'value'),
    Input('indicator-dropdown-economic', 'value'),
    Input('market-dropdown-economic', 'value'),
    Input('product-dropdown-economic', 'value'),
    Input('active-tab-economic', 'value'),
)
def update_year_dropdown(series_name, indicator, market, product, active_tab):
    # Filter the data based on the selected filters
    dff = filter_data(data=data, series_name=series_name, indicator=indicator, market=market, product=product)
    
    # Extract unique year values
    year_values = dff['Year'].dropna().unique().tolist()
    
    # If no year_values are available, return empty options and value
    if not year_values:
        return [], None, {'display': 'none' if active_tab != 'map' else 'block'}
    
    # Prepare dropdown options
    year_options = [{'label': str(int(year)), 'value': str(int(year))} for year in sorted(year_values)]
    
    # Set default value to the latest year
    default_value = str(max(year_values))  # Convert to string to match dropdown data format
    
    # Conditionally set style based on active_tab
    dropdown_style = {'display': 'block'} if active_tab == 'map' else {'display': 'none'}
    
    return year_options, default_value, dropdown_style


# # Callback to handle map clicks and display modal
# @callback(
#     Output("info-modal-economic", "opened"),
#     Output("modal-body-economic", "children"),
#     Output("geojson-economic", "clickData"),  # Reset clickData
#     Input("geojson-economic", "clickData"),
#     State("info-modal-economic", "opened"),
#     prevent_initial_call=True
# )
# def handle_map_click(click_data, is_modal_open):
#     if click_data is None:
#         return dash.no_update, dash.no_update, dash.no_update
    
#     # Extract feature properties from the clicked data
#     feature = click_data.get("properties", {})
    
#     dff = filter_data(
#         data=data,
#         series_name=feature['Series Name'],
#         market=feature['name'],
#     )
    
#     # Prepare the content for the modal
#     modal_content = [
#         create_modal(dff, feature)
#     ]
    
#     # Open the modal, update its content, and reset clickData
#     return not is_modal_open, modal_content, None