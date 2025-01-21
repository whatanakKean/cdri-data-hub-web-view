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
import plotly.express as px 

# Load data
data = load_data(file_path="src/data/Unpivoted_Datahub_Agri_Latest.xlsx", sheet_name="Sheet1")
data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Sidebar components
def sidebar(data):
    return dmc.Stack([
        dmc.Paper([
            dmc.Select(
                label="Select Series Name", 
                id="series-name-dropdown", 
                value='Rice Production', 
                data=[{'label': option, 'value': option} for option in data["Series Name"].dropna().str.strip().unique() if option],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                checkIconPosition="right",
                allowDeselect=False,
            ),
            dmc.Select(
                label="Select Sector", 
                id="sector-dropdown", 
                value='Agriculture', 
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
                id="subsector-1-dropdown", 
                value='Production', 
                data=[{'label': option, 'value': option} for option in data["Sub-Sector (1)"].dropna().str.strip().unique()],
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
                data=[{'label': option, 'value': option} for option in data["Sub-Sector (2)"].dropna().str.strip().unique()],
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
                data=[{'label': option, 'value': option} for option in ['All'] + list(data["Province"].dropna().str.strip().unique())],
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


def create_map(dff, series_name, indicator, year, indicator_unit):
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
        with open('./assets/geoBoundaries-KHM-ADM0_simplified.json') as f:  # Assuming this file has Cambodia as a single entity
            geojson_data = json.load(f)
            
        geojson_data['features'][0]['properties'][indicator] = dff['Indicator Value']
        
        geojson = dl.GeoJSON(
            data=geojson_data,
            style=style_handle,
            zoomToBounds=True,
            zoomToBoundsOnClick=True,
            hoverStyle=dict(weight=5, color='#666', dashArray=''),
            hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp=indicator),
            id="geojson"
        )
        
        return html.Div([
            dl.Map(
                    style={'width': '100%', 'height': '450px'},
                    center=[20, 0],  # Centered on the equator, near the Prime Meridian
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
        
def create_graph(dff, series_name, subsector_1, indicator, province):
    if subsector_1 not in ["Production", "Export", "Contract Farming", "Agricultural Cooperative"]:
        return html.Div([
            dmc.Text("Not Enough Data To Visualize", size="lg")
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
    
    if subsector_1 == "Production":
        dff = dff.sort_values(by='Indicator Value', ascending=False)
        fig2 = go.Figure(layout=layout)
        for year in dff['Year'].unique():
            year_data = dff[dff['Year'] == year]
            fig2.add_trace(go.Bar(
                x=year_data['Province'],
                y=year_data['Indicator Value'],
                name=str(year),
                marker=dict(color=px.colors.qualitative.Set1[list(dff['Year'].unique()).index(year)]),
                hoverinfo='x+y+name'
            ))
        # Set barmode to stack
        fig2.update_layout(
            barmode='stack',
            xaxis=dict(
                tickmode='array',  # Explicitly set ticks (labels)
                tickvals=list(dff['Province'].unique()),  # List of all unique provinces
                ticktext=list(dff['Province'].unique())  # Same as tickvals to display province names
            ),
            annotations=[ 
                dict(
                    x=0.5,
                    y=-0.3, 
                    xref="paper", yref="paper",
                    text="Produced By: CDRI Data Hub",
                    showarrow=False,
                    font=dict(size=12, color='rgba(0, 0, 0, 0.7)'),
                    align='center'
                ),
            ],
        )
        title_text = f"{dff['Sub-Sector (2)'].unique()[0]} {dff['Sub-Sector (1)'].unique()[0]}: {dff['Indicator'].unique()[0]} in {'Cambodia' if province == 'All' else province}"
        fig1.update_layout(
            title=dict(
                text=title_text,
            ),
        )
        fig2.update_layout(
            title=dict(
                text=title_text,
            ),
        )
    
    elif subsector_1 == "Export":
        fig2 = go.Figure(layout=layout)
        
        # Filter data for the latest year
        latest_year = dff['Year'].max()
        latest_data = dff[dff['Year'] == latest_year]
        
        # Add a Treemap trace for the latest year
        fig2.add_trace(go.Treemap(
            labels=latest_data['Markets'],
            parents=[""] * len(latest_data),
            values=latest_data['Indicator Value'],
            textinfo="label+value"
        ))

        # Create the year selector dropdown (without the "All Years" option)
        dropdown_buttons = []

        # Add a button for each year in the data
        for year in dff['Year'].unique():
            filtered_data = dff[dff['Year'] == year]
            dropdown_buttons.append({
                "label": f"{year}", "method": "update",
                "args": [{"labels": [filtered_data['Markets']], "values": [filtered_data['Indicator Value']]},
                        ]
            })
        
        # Find the index of the latest year to make it the default selection
        default_year_index = list(dff['Year'].unique()).index(latest_year)

        # Add dropdown menu
        fig2.update_layout(
            updatemenus=[{
                "buttons": dropdown_buttons,
                "direction": "down",
                "x": 1,
                "xanchor": "right",
                "y": 1.1, "yanchor": "top",
                "active": default_year_index
            }],
            annotations=[{
                "x": 0.5, "y": -0.3, "xref": "paper", "yref": "paper",
                "text": "Produced By: CDRI Data Hub",
                "showarrow": False, "font": {"size": 12, "color": 'rgba(0, 0, 0, 0.7)'},
                "align": "center"
            }]
        )
        title_text = f"{dff['Sub-Sector (2)'].unique()[0]} {dff['Sub-Sector (1)'].unique()[0]} {dff['Indicator'].unique()[0]}"
        fig1.update_layout(
            title=dict(
                text=title_text,
            ),
        )
        fig2.update_layout(
            title=dict(
                text=f"{title_text} By Countries ({latest_year})",
            ),
        )
    elif subsector_1 == "Contract Farming":
        title_text = f"{dff['Sub-Sector (2)'].unique()[0]} {dff['Sub-Sector (1)'].unique()[0]} {dff['Indicator'].unique()[0]}"
        fig1.update_layout(
            title=dict(
                text=title_text,
            ),
        )
    elif subsector_1 == "Agricultural Cooperative":
        title_text = f"{dff['Sub-Sector (1)'].unique()[0]} {dff['Indicator'].unique()[0]}"
        fig1.update_layout(
            title=dict(
                text=title_text,
            ),
        )

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
            dmc.Divider(size="sm"),
            # dcc.Graph(id="figure-linechart", figure=fig2, config={
            #     'displaylogo': False,
            #     'toImageButtonOptions': {
            #         'format': 'png',
            #         'filename': 'cdri_datahub_viz',
            #         'height': 500,
            #         'width': 800,
            #         'scale': 6
            #     }
            # }),
        ])





# Callbacks
@callback([Output('graph-id', 'children'), Output('map-id', 'children'), Output('dataview-container', 'children'), Output('metadata-panel', 'children'), Output('indicator-unit', 'data')],
          [Input("series-name-dropdown", "value"), Input("subsector-1-dropdown", "value"), Input("subsector-2-dropdown", "value"),
           Input("province-dropdown", "value"), Input("indicator-dropdown", "value"), Input("year-slider", "value")])
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

    return create_graph(dff, series_name, subsector_1, indicator, province), create_map(dff, series_name, indicator, year, indicator_unit), create_dataview(dff), create_metadata(dff), indicator_unit.tolist()


@callback(Output("download-data", "data"), Input("download-button", "n_clicks"),
          State('series-name-dropdown', 'value'), State('subsector-1-dropdown', 'value'),
          State('subsector-2-dropdown', 'value'), State('province-dropdown', 'value'), State('indicator-dropdown', 'value'))
def download_data(n_clicks, series_name, subsector_1, subsector_2, province, indicator):
    if n_clicks is None: return dash.no_update
    dff = filter_data(data=data, series_name=series_name, subsector_1=subsector_1, subsector_2=subsector_2, province=province, indicator=indicator)
    return dict(content=dff.to_csv(index=False), filename="data.csv", type="application/csv")


# Calllback for info on map
@callback(Output("info", "children"), Input('series-name-dropdown', 'value'), Input('year-slider', 'value'), Input('indicator-dropdown', 'value'), Input('indicator-unit', 'data'), Input("geojson", "hoverData"))
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
    return [{'label': option, 'value': option} for option in subsector_1_options], subsector_1_options[0] if subsector_1_options.size > 0 else None

@callback(
    Output('subsector-2-dropdown', 'data'),
    Output('subsector-2-dropdown', 'value'),
    Input('series-name-dropdown', 'value'),
    Input('subsector-1-dropdown', 'value')
)
def update_subsector_2(series_name, subsector_1):
    subsector_2_options = data[(data["Series Name"] == series_name) & (data["Sub-Sector (1)"] == subsector_1)]["Sub-Sector (2)"].dropna().str.strip().unique()
    return [{'label': option, 'value': option} for option in subsector_2_options], subsector_2_options[0] if subsector_2_options.size > 0 else None

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
    return [{'label': option, 'value': option} for option in ['All'] + list(province_options)], 'All', style

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
    indicator_options = [{'label': indicator, 'value': indicator} for indicator in indicator_values]
    
    # Set default value to the first indicator
    default_value = indicator_values[0] if indicator_values else None
    
    return indicator_options, default_value



@callback(
    Output('year-slider', 'min'),
    Output('year-slider', 'max'),
    Output('year-slider', 'value'),
    Output('year-slider', 'marks'),
    Input('series-name-dropdown', 'value'),
    Input('subsector-1-dropdown', 'value'),
    Input('subsector-2-dropdown', 'value'),
    Input('province-dropdown', 'value'),
    Input('indicator-dropdown', 'value'),
)
def update_year_slider(series_name, subsector_1, subsector_2, province, indicator):
    # Filter the data based on the selected filters
    dff = filter_data(data=data, series_name=series_name, subsector_1=subsector_1, subsector_2=subsector_2, province=province, indicator=indicator)
    
    # Get the unique years available after filtering
    year_options = dff["Year"].dropna().unique()
    
    # If no years are available, return default values
    if not year_options.size:
        return 0, 0, 0, []
    
    # Get the minimum and maximum years
    min_year = int(year_options.min())
    max_year = int(year_options.max())
    
    # Prepare the marks for the slider based on the available years
    marks = [{'value': year, 'label': str(year)} for year in year_options]
    
    # Default value for the `year-slider` (min value)
    year_slider_value = max_year
    
    # Return the updated properties for the year-slider
    return min_year, max_year, year_slider_value, marks

