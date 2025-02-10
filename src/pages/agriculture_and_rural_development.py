import json
import math
import sqlite3
import dash
from dash import html, dcc, Input, Output, State, ctx, callback
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
data = pd.read_sql_query(f"SELECT * FROM agriculture_data;", conn)

# Sidebar components
def sidebar(data):
    return dmc.Stack([
        dmc.Paper([
            dmc.Select(
                label="Select Series Name", 
                id="series-name-dropdown", 
                value='Rice Production', 
                data=[{'label': option, 'value': option} for option in sorted(data["Series Name"].dropna().str.strip().unique()) if option],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                checkIconPosition="right",
                allowDeselect=False,
            ),
            dmc.Select(
                label="Select Sector", 
                id="sector-dropdown", 
                value='Agriculture', 
                data=[{'label': option, 'value': option} for option in sorted(data["Sector"].dropna().str.strip().unique()) if option],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
                style={'display': 'none'},
            ),
            dmc.Select(
                label="Select Sub-Sector (1)", 
                id="subsector-1-dropdown", 
                value='Production', 
                data=[{'label': option, 'value': option} for option in sorted(data["Sub-Sector (1)"].dropna().str.strip().unique())],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
                style={'display': 'none'},
            ),
            dmc.Select(
                label="Select Sub-Sector (2)", 
                id="subsector-2-dropdown", 
                value='Rice', 
                data=[{'label': option, 'value': option} for option in sorted(data["Sub-Sector (2)"].dropna().str.strip().unique())],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
                style={'display': 'none'},
            ),
            dmc.Select(
                label="Select Province", 
                id="province-dropdown", 
                value='All', 
                data=[{'label': option, 'value': option} for option in ['All'] + list(sorted(data["Province"].dropna().str.strip().unique()))],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
            ),
            dmc.Select(
                label="Select Indicator", 
                id="indicator-dropdown", 
                value='Area Planted', 
                data=[{'label': option, 'value': option} for option in list(sorted(data["Indicator"].dropna().str.strip().unique()))],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
            ),
            dmc.Select(
                label="Select Year", 
                id="year-dropdown", 
                value=str(data["Year"].unique()[-1]),
        	    data=[{'label': str(option), 'value': str(option)} for option in sorted(data["Year"].unique())],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
            )
        ], id="filter", shadow="xs", p="md", radius="md", withBorder=True),
        
        dmc.Accordion(chevronPosition="right", variant="contained", radius="md", children=[
            dmc.AccordionItem(value="bender", children=[
                dmc.AccordionControl(dmc.Group([html.Div([dmc.Text("Metadata"), dmc.Text("Information about current data", size="sm", fw=400, c="dimmed")])]),),
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
                                ], 
                                value="map"
                            ),
                            dmc.TabsPanel(                               
                                children=[
                                    html.Div(id='graph-id'),
                                ], 
                                value="graph"
                            ),
                            dmc.TabsPanel(html.Div(id='dataview-id'), value="dataview"),
                        ], 
                        id="active-tab", value="map",
                    ),
                
                ], shadow="xs", p="md", radius="md", withBorder=True),
            ], gap="xs"),
            
            dcc.Store(id="selected-point-data"),
            dcc.Store(id="indicator-unit"),
            dmc.Modal(
                id="info-modal",
                children=[
                    dmc.Text(id="modal-body"),
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
        dag.AgGrid(id='ag-grid', columnDefs=[{"headerName": col, "field": col} for col in pivoted_data.columns], rowData=pivoted_data.to_dict('records'), style={'height': '400px'}),
        dmc.Button("Download Data", id="download-button", variant="outline", color="#336666", mt="md", style={'marginLeft': 'auto', 'display': 'flex', 'justifyContent': 'flex-end'}),
        dcc.Download(id="download-data")
    ])
    
def create_metadata(dff):
    if 'Source' in dff and dff['Source'].dropna().any():
        return dmc.Text(
            f"Sources: {', '.join(dff['Source'].dropna().unique())}", size="sm"
        )
    return ""

def create_map(dff, year):
    # Filter data for the selected year
    dff = dff[dff["Year"] == int(year)]
    series_name = dff['Series Name'].unique()[0]
    indicator = dff['Indicator'].unique()[0]
    indicator_unit = dff['Indicator Unit'].unique()[0]
    
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

    if 'Province' in dff.columns:
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
                feature['properties']['Series Name'] = series_name
                feature['properties']['Indicator'] = indicator
                feature['properties']['Year'] = year
            else:
                # Assign None for missing data
                feature['properties'][indicator] = None
        
        # Create geojson.
        geojson = dl.GeoJSON(data=geojson_data,
                            style=style_handle,
                            zoomToBounds=True,
                            zoomToBoundsOnClick=True,
                            hoverStyle=dict(color='black'),
                            hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp=indicator),
                            id="geojson")

        # Return the map component along with the modal
        return html.Div(
            [
                dl.Map(
                    style={'width': '100%', 'height': '450px'},
                    center=[0, 0],
                    zoom=6,
                    children=[
                        dl.TileLayer(url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
                        geojson,
                        colorbar,
                        html.Div(children=get_info(series_name=series_name, indicator=indicator, indicator_unit=indicator_unit, year=year), id="info", className="info", style={"position": "absolute", "top": "20px", "right": "20px", "zIndex": "1000"}),
                    
                    ],
                    attributionControl=False,
                ),
            ],
            style={
                'position': 'relative',
                'zIndex': 0,
            }
        )
    
    elif 'Markets' in dff.columns:
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
                feature['properties']['Series Name'] = series_name
                feature['properties']['Indicator'] = indicator
                feature['properties']['Year'] = year
            else:
                # Assign None for missing data
                feature['properties'][indicator] = None
                
        # Create geojson.
        geojson = dl.GeoJSON(data=geojson_data,
                            style=style_handle,
                            zoomToBounds=True,
                            zoomToBoundsOnClick=True,
                            hoverStyle=dict(color='black'),
                            hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp=indicator),
                            id="geojson")
        
        return html.Div([
            dl.Map(
                    style={'width': '100%', 'height': '450px'},
                    center=[0, 0],
                    zoom=2,
                    children=[
                        dl.TileLayer(url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
                        geojson, 
                        colorbar,
                        html.Div(children=get_info(series_name=series_name, indicator=indicator, indicator_unit=indicator_unit, year=year), id="info", className="info", style={"position": "absolute", "top": "20px", "right": "20px", "zIndex": "1000"}),
                    ],
                    attributionControl=False,
            )],
            style={
                'position': 'relative',
                'zIndex': 0,
            }
        )
    else:
        with open('./assets/geoBoundaries-KHM-ADM0_simplified.json') as f:
            geojson_data = json.load(f)
            
        geojson_data['features'][0]['properties'][indicator] = dff['Indicator Value'].values[0]
        geojson_data['features'][0]['properties']['Series Name'] = series_name
        geojson_data['features'][0]['properties']['Indicator'] = indicator
        geojson_data['features'][0]['properties']['Year'] = year
        
        geojson = dl.GeoJSON(
            data=geojson_data,
            style=style_handle,
            zoomToBounds=True,
            zoomToBoundsOnClick=True,
            hoverStyle=dict(color='black'),
            hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp=indicator),
            id="geojson"
        )
        
        return html.Div([
            dl.Map(
                    style={'width': '100%', 'height': '450px'},
                    center=[0, 0],
                    zoom=6,
                    children=[
                        dl.TileLayer(url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
                        geojson,
                        html.Div(children=get_info(series_name=series_name, indicator=indicator, indicator_unit=indicator_unit, year=year), id="info", className="info", style={"position": "absolute", "top": "20px", "right": "20px", "zIndex": "1000"}),
                    ],
                    attributionControl=False,
            )],
            style={
                'position': 'relative',
                'zIndex': 0,
            }
        )
        
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
    fig1.update_layout(
        title=dict(
            text= f"{series_name}: {dff['Indicator'].unique()[0]}",
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
        dmc.Alert(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            title="Description",
            color="green"
        ),
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
            showgrid=True,
            gridwidth=0.5,
            griddash='dot',
            tickformat=',',
            rangemode='tozero',
            title=f"{indicator} ({dff_filtered['Indicator Unit'].unique()[0]})",
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
            text= f"{series_name}: {indicator} in {feature['shapeName']}",
        ),
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

# Callbacks
@callback([Output('graph-id', 'children'), Output('map-id', 'children'), Output('dataview-id', 'children'), Output('metadata-panel', 'children'), Output('indicator-unit', 'data')],
          [Input("series-name-dropdown", "value"), Input("subsector-1-dropdown", "value"), Input("subsector-2-dropdown", "value"),
           Input("province-dropdown", "value"), Input("indicator-dropdown", "value"), Input("year-dropdown", "value")])
def update_report(series_name, subsector_1, subsector_2, province, indicator, year):
    dff = filter_data(
        data=data,
        series_name=series_name,
        subsector_1=subsector_1 if subsector_1 else None,
        subsector_2=subsector_2 if subsector_2 else None,
        province=province if province else None,
        indicator=indicator
    )
    dff = dff.rename(columns={'Latiude': 'Latitude'})
    indicator_unit = dff['Indicator Unit'].unique()

    return create_graph(dff), create_map(dff, year), create_dataview(dff), create_metadata(dff), indicator_unit.tolist()


@callback(Output("download-data", "data"), Input("download-button", "n_clicks"),
          State('series-name-dropdown', 'value'), State('subsector-1-dropdown', 'value'),
          State('subsector-2-dropdown', 'value'), State('province-dropdown', 'value'), State('indicator-dropdown', 'value'))
def download_data(n_clicks, series_name, subsector_1, subsector_2, province, indicator):
    if n_clicks is None: return dash.no_update
    dff = filter_data(data=data, series_name=series_name, subsector_1=subsector_1, subsector_2=subsector_2, province=province, indicator=indicator)
    return dict(content=dff.to_csv(index=False), filename="data.csv", type="application/csv")


# Calllback for info on map
@callback(Output("info", "children"), Input('series-name-dropdown', 'value'), Input('year-dropdown', 'value'), Input('indicator-dropdown', 'value'), Input('indicator-unit', 'data'), Input("geojson", "hoverData"))
def info_hover(series_name, year, indicator, indicator_unit, feature):
    return get_info(series_name=series_name, indicator=indicator, feature=feature, indicator_unit=indicator_unit, year=year)


# Callbacks for dynamic dropdown updates
@callback(
    Output('subsector-1-dropdown', 'data'),
    Output('subsector-1-dropdown', 'value'),
    Input('series-name-dropdown', 'value')
)
def update_subsector_1(series_name):
    subsector_1_options = data[data["Series Name"] == series_name]["Sub-Sector (1)"].dropna().str.strip().unique()
    return [{'label': option, 'value': option} for option in sorted(subsector_1_options)], subsector_1_options[0] if subsector_1_options.size > 0 else None

@callback(
    Output('subsector-2-dropdown', 'data'),
    Output('subsector-2-dropdown', 'value'),
    Input('series-name-dropdown', 'value'),
    Input('subsector-1-dropdown', 'value')
)
def update_subsector_2(series_name, subsector_1):
    subsector_2_options = data[(data["Series Name"] == series_name) & (data["Sub-Sector (1)"] == subsector_1)]["Sub-Sector (2)"].dropna().str.strip().unique()
    return [{'label': option, 'value': option} for option in sorted(subsector_2_options)], subsector_2_options[0] if subsector_2_options.size > 0 else None

@callback(
    Output('province-dropdown', 'data'),
    Output('province-dropdown', 'value'),
    Output('province-dropdown', 'style'),
    Input('series-name-dropdown', 'value'),
    Input('subsector-1-dropdown', 'value'),
    Input('subsector-2-dropdown', 'value')
)
def update_province(series_name, subsector_1, subsector_2):
    if subsector_2:
        # Filter with subsector_2
        province_options = data[
            (data["Series Name"] == series_name) & 
            (data["Sub-Sector (1)"] == subsector_1) & 
            (data["Sub-Sector (2)"] == subsector_2)
        ]["Province"].dropna().str.strip().unique()
    else:
        # Filter without subsector_2
        province_options = data[
            (data["Series Name"] == series_name) & 
            (data["Sub-Sector (1)"] == subsector_1)
        ]["Province"].dropna().str.strip().unique()
        
    style = {'display': 'block'} if province_options.size > 0 else {'display': 'none'}
    return [{'label': option, 'value': option} for option in ['All'] + list(sorted(province_options))], 'All', style

@callback(
    Output('indicator-dropdown', 'data'),
    Output('indicator-dropdown', 'value'),
    Input('series-name-dropdown', 'value'),
    Input('subsector-1-dropdown', 'value'),
    Input('subsector-2-dropdown', 'value'),
    Input('province-dropdown', 'value'),
    prevent_initial_call=False
)
def update_indicators(series_name, subsector_1, subsector_2, province):
    dff = filter_data(data=data, series_name=series_name, subsector_1=subsector_1, subsector_2=subsector_2, province=province)
    
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
    Output('year-dropdown', 'data'),
    Output('year-dropdown', 'value'),
    Output('year-dropdown', 'style'),
    Input('series-name-dropdown', 'value'),
    Input('subsector-1-dropdown', 'value'),
    Input('subsector-2-dropdown', 'value'),
    Input('province-dropdown', 'value'),
    Input('indicator-dropdown', 'value'),
    Input('active-tab', 'value'),
)
def update_year_dropdown(series_name, subsector_1, subsector_2, province, indicator, active_tab):
    dff = filter_data(
        data=data,
        series_name=series_name,
        subsector_1=subsector_1,
        subsector_2=subsector_2,
        province=province,
        indicator=indicator
    )

    # Extract unique year values
    year_values = dff['Year'].dropna().unique().tolist()
    
    # If no year_values are available, return empty options and value
    if not year_values:
        return [], None, {'display': 'none' if active_tab != 'map' else 'block'}
    
    # Prepare dropdown options
    year_options = [{'label': str(year), 'value': str(year)} for year in sorted(year_values)]
    
    # Set default value to the latest year
    default_value = str(max(year_values))  # Convert to string to match dropdown data format
    
    # Conditionally set style based on active_tab
    dropdown_style = {'display': 'block'} if active_tab == 'map' else {'display': 'none'}
    
    return year_options, default_value, dropdown_style


# Callback to handle map clicks and display modal
@callback(
    Output("info-modal", "opened"),
    Output("modal-body", "children"),
    Output("geojson", "clickData"),  # Reset clickData
    Input("geojson", "clickData"),
    State("info-modal", "opened"),
    prevent_initial_call=True
)
def handle_map_click(click_data, is_modal_open):
    if click_data is None:
        return dash.no_update, dash.no_update, dash.no_update
    
    # Extract feature properties from the clicked data
    feature = click_data.get("properties", {})
    
    dff = filter_data(
        data=data,
        series_name=feature['Series Name'],
        province=feature['shapeName'],
    )
    
    # Prepare the content for the modal
    modal_content = [
        create_modal(dff, feature)
    ]
    
    # Open the modal, update its content, and reset clickData
    return not is_modal_open, modal_content, None