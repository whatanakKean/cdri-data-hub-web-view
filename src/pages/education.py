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
data = pd.read_sql_query(f"SELECT * FROM education_data;", conn)

# Sidebar components
def sidebar(data):
    return dmc.Stack([
        dmc.Paper([
            dmc.Select(
                label="Select Dataset", 
                id="series-name-dropdown-education", 
                value='Student Flow Rates By Class Range', 
                data=[{'label': option, 'value': option} for option in data["Series Name"].dropna().str.strip().unique() if option],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                checkIconPosition="right",
                allowDeselect=False,
            ),
            dmc.Select(
                label="Select Indicator", 
                id="indicator-dropdown-education", 
                value='Dropout', 
                data=[{'label': option, 'value': option} for option in list(sorted(data["Indicator"].dropna().str.strip().unique()))],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
            ),
            dmc.Select(
                label="Select Grade", 
                id="grade-dropdown-education", 
                value="All",
        	    data=[{'label': str(option), 'value': str(option)} for option in ['All'] + list(sorted(data["Grade"].dropna().unique()))],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
            ),
            dmc.Select(
                label="Select Province", 
                id="province-dropdown-education", 
                value="Whole Kingdom",
        	    data=[{'label': str(option), 'value': str(option)} for option in sorted(data["Province"].dropna().unique())],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
            ),
            dmc.Select(
                label="Select Year", 
                id="year-dropdown-education", 
                value=str(data["Year"].dropna().unique()[-1]),
        	    data=[{'label': str(option), 'value': str(option)} for option in sorted(data["Year"].dropna().unique())],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
            )
        ], id="filter-education", shadow="xs", p="md", radius="md", withBorder=True),
        
        dmc.Accordion(chevronPosition="right", variant="contained", radius="md", children=[
            dmc.AccordionItem(value="bender", children=[
                dmc.AccordionControl(dmc.Group([html.Div([dmc.Text("Metadata"), dmc.Text("Information about current data", size="sm", fw=400, c="dimmed")])]),),
                dmc.AccordionPanel(
                    id="metadata-panel-education",
                    children=dmc.Text("Bender is a bending unit from the future...", size="sm")
                )
            ])
        ])
    ], gap="xs")

# Page Layout
education = dmc.Container([
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
                                    html.Div(id='map-id-education'),        
                                ], 
                                value="map"
                            ),
                            dmc.TabsPanel(                               
                                children=[
                                    html.Div(id='graph-id-education'),
                                ], 
                                value="graph"
                            ),
                            dmc.TabsPanel(html.Div(id='dataview-container-education'), value="dataview"),
                        ], 
                        id="active-tab-education", value="map", color="#336666"
                    ),
                ], shadow="xs", p="md", radius="md", withBorder=True),
            ], gap="xs"),
            
            dcc.Store(id="selected-point-data-education"),
            dcc.Store(id="indicator-unit-education"),
            dmc.Modal(
                id="info-modal-education",
                children=[
                    dmc.Text(id="modal-body-education"),
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
    
    # Remove columns where all values are empty strings
    pivoted_data = pivoted_data.loc[:, ~(pivoted_data.apply(lambda col: col.eq("").all(), axis=0))]
    
    return html.Div([
        dag.AgGrid(id='ag-grid-education', defaultColDef={"filter": True}, columnDefs=[{"headerName": col, "field": col} for col in pivoted_data.columns], rowData=pivoted_data.to_dict('records'), style={'height': '400px'}),
        dmc.Button("Download Data", id="download-button-education", variant="outline", color="#336666", mt="md", style={'marginLeft': 'auto', 'display': 'flex', 'justifyContent': 'flex-end'}),
        dcc.Download(id="download-data-education")
    ])
    
    
def create_metadata(dff):
    if 'Source' in dff and dff['Source'].dropna().any():  # Check if 'Source' exists and has non-NA values
        return dmc.Text(
            f"Sources: {', '.join(dff['Source'].dropna().unique())}", size="sm"
        )
    return ""


def create_map(dff, year):
    # Filter data for the selected year
    dff = dff[dff["Year"] == year]
    
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

    if 'Province' in dff.columns and dff['Province'].unique() != 'Whole Kingdom':
        ctg = [f"{int(classes[i])}+" for i in range(len(classes))]
        colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale, width=30, height=300, position="bottomright")
    
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
                            id="geojson-education")

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
                        html.Div(children=get_info(series_name=series_name, indicator=indicator, indicator_unit=indicator_unit, year=year), id="info-education", className="info", style={"position": "absolute", "top": "20px", "right": "20px", "zIndex": "1000"}),
                    
                    ],
                    attributionControl=False,
                ),
            ],
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
            id="geojson-education"
        )
        
        return html.Div([
            dl.Map(
                    style={'width': '100%', 'height': '450px'},
                    center=[0, 0],
                    zoom=6,
                    children=[
                        dl.TileLayer(url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
                        geojson,
                        html.Div(children=get_info(series_name=series_name, indicator=indicator, indicator_unit=indicator_unit, year=year), id="info-education", className="info", style={"position": "absolute", "top": "20px", "right": "20px", "zIndex": "1000"}),
                    ],
                    attributionControl=False,
            )],
            style={
                'position': 'relative',
                'zIndex': 0,
            }
        )
   
def create_graph(dff):
    series_name = dff['Series Name'].unique()[0]
    indicator = dff['Indicator'].unique()[0]

    if series_name == 'Dropout Rate By Occupation':
        # Create a multi-bar chart with Y-axis as Occupation
        traces = []
        for year in dff['Year'].unique():
            year_data = dff[dff['Year'] == year]
            traces.append(go.Bar(
                y=year_data['Occupation'],
                x=year_data['Indicator Value'],
                name=str(year),
                orientation='h'
            ))

        # Create layout for bar chart
        layout = go.Layout(
            images=[dict(
                source="./assets/CDRI Logo.png",
                xref="paper", yref="paper",
                x=1, y=1.1,
                sizex=0.2, sizey=0.2,
                xanchor="right", yanchor="bottom"
            )],
            title=dict(text=f"{series_name}: {indicator}"),
            font=dict(
                family='BlinkMacSystemFont, -apple-system, sans-serif',
                color='rgb(24, 29, 31)'
            ),
            barmode='group',  # Group bars for different years
            yaxis=dict(
                title="Occupation",
                categoryorder='total ascending'
            ),
            xaxis=dict(
                title=f"{indicator} ({dff['Indicator Unit'].unique()[0]})",
                gridcolor='rgba(169, 169, 169, 0.7)',
                showgrid=True,
                gridwidth=0.5,
                griddash='dot'
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.4,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=100, b=100, l=50, r=50),
            plot_bgcolor='white',
        )

        fig = go.Figure(data=traces, layout=layout)
    else:
        # # Original line chart implementation
        # min_value = dff['Indicator Value'].min()
        # max_value = dff['Indicator Value'].max()
        # yaxis_range = [0, 100] if 0 <= min_value and max_value <= 100 else None

        if 'Grade' in dff.columns:
            traces = []
            for grade in dff['Grade'].unique():
                grade_data = dff[dff['Grade'] == grade]
                traces.append(go.Scatter(
                    x=grade_data['Year'],
                    y=grade_data['Indicator Value'],
                    mode='lines+markers',
                    name=f"{grade}",
                ))
        else:
            traces = [go.Scatter(
                x=dff['Year'],
                y=dff['Indicator Value'],
                mode='lines+markers',
                name=indicator
            )]

        # Create line chart layout
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
                family='BlinkMacSystemFont, -apple-system, sans-serif',
                color='rgb(24, 29, 31)'
            ),
            hovermode="x unified",
            plot_bgcolor='white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.4,
                xanchor="center",
                x=0.5
            ),
            xaxis=dict(
                tickmode='array',
                tickvals=dff['Year'].unique(),
            ),
            margin=dict(t=100, b=100, l=50, r=50),
        )

        fig = go.Figure(layout=layout)
        for trace in traces:
            fig.add_trace(trace)
        fig.update_layout(title=dict(text=f"{series_name}: {indicator}"))

    return html.Div([
        dcc.Graph(
            id="figure-linechart",
            figure=fig,
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
    
    # # Determine y-axis range if values fall between 0-100
    # min_value = dff_filtered['Indicator Value'].min()
    # max_value = dff_filtered['Indicator Value'].max()
    # yaxis_range = [0, 100] if 0 <= min_value and max_value <= 100 else None

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
            family='BlinkMacSystemFont, -apple-system, sans-serif',
            color='rgb(24, 29, 31)'
        ),
        hovermode="x unified",
        plot_bgcolor='white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=5,
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
            text = f"{series_name}: {dff['Indicator'].unique()[0]}" + (f" in {dff['Province'].unique()[0]}" if 'Province' in dff.columns and dff['Province'].nunique() == 1 else "")
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
@callback(Output("info-education", "children"), Input('series-name-dropdown-education', 'value'), Input('year-dropdown-education', 'value'), Input('indicator-dropdown-education', 'value'),  Input('indicator-unit-education', 'data'), Input("geojson-education", "hoverData"))
def info_hover(series_name, year, indicator, indicator_unit, feature):
    return get_info(series_name=series_name, indicator=indicator, feature=feature, indicator_unit=indicator_unit, year=year)


# Callbacks
@callback([Output('graph-id-education', 'children'), Output('map-id-education', 'children'), Output('dataview-container-education', 'children'), Output('metadata-panel-education', 'children'), Output('indicator-unit-education', 'data')],
          [Input('series-name-dropdown-education', 'value'), 
           Input("indicator-dropdown-education", "value"), Input("year-dropdown-education", "value"), Input('grade-dropdown-education', 'value'), Input('province-dropdown-education', 'value'),])
def update_report(series_name, indicator, year, grade, province):
    dff = filter_data(data=data, series_name=series_name, indicator=indicator, grade=grade, province=province)

    indicator_unit = dff['Indicator Unit'].unique()
    return create_graph(dff), create_map(dff, year), create_dataview(dff), create_metadata(dff), indicator_unit.tolist()


@callback(Output("download-data-education", "data"), Input("download-button-education", "n_clicks"),
          State('series-name-dropdown-education', 'value'), State('indicator-dropdown-education', 'value'), Input('grade-dropdown-education', 'value'), Input('province-dropdown-education', 'value'),)
def download_data(n_clicks, series_name, indicator, grade, province):
    if n_clicks is None: return dash.no_update
    dff = filter_data(data=data, series_name=series_name, indicator=indicator, grade=grade, province=province)
    dff = dff.loc[:, ~(dff.apply(lambda col: col.eq("").all(), axis=0))]
    return dict(content=dff.to_csv(index=False), filename="data.csv", type="application/csv")

@callback(
    Output('grade-dropdown-education', 'data'),
    Output('grade-dropdown-education', 'value'),
    Output('grade-dropdown-education', 'style'),
    Input('series-name-dropdown-education', 'value'),
)
def update_grade(series_name):
    grade_options = data[(data["Series Name"] == series_name)]["Grade"].dropna().str.strip().unique()
    # Control visibility based on available options
    style = {'display': 'block'} if grade_options.size > 0 else {'display': 'none'}
    return [{'label': option, 'value': option} for option in ['All'] + sorted(grade_options)], 'All' if grade_options.size > 0 else None, style

@callback(
    Output('province-dropdown-education', 'data'),
    Output('province-dropdown-education', 'value'),
    Output('province-dropdown-education', 'style'),
    Input('series-name-dropdown-education', 'value'),
)
def update_province(series_name):
    province_options = data[(data["Series Name"] == series_name)]["Province"].dropna().str.strip().unique()
    # Control visibility based on available options
    style = {'display': 'block'} if province_options.size > 0 else {'display': 'none'}
    return [{'label': option, 'value': option} for option in sorted(province_options)], "Whole Kingdom" if province_options.size > 0 else None, style

@callback(
    Output('indicator-dropdown-education', 'data'),
    Output('indicator-dropdown-education', 'value'),
    Input('series-name-dropdown-education', 'value'),
    Input('grade-dropdown-education', 'value'),
    Input('province-dropdown-education', 'value'),
    prevent_initial_call=False
)
def update_indicators(series_name, grade, province):
    # Filter data based on the selected filters
    dff = filter_data(data=data, series_name=series_name, grade=grade, province=province)
    
    # Extract unique indicator values
    indicator_values = dff['Indicator'].unique().tolist()
    
    # If no indicators are available, return empty options and value
    if not indicator_values:
        return [], None
    
    # Prepare dropdown options
    indicator_options = [{'label': indicator, 'value': indicator} for indicator in sorted(indicator_values)]
    
    # Set default value to the first indicator
    default_value = sorted(indicator_values)[0] if indicator_values else None
    
    return indicator_options, default_value

@callback(
    Output('year-dropdown-education', 'data'),
    Output('year-dropdown-education', 'value'),
    Output('year-dropdown-education', 'style'),
    Input('series-name-dropdown-education', 'value'),
    Input('indicator-dropdown-education', 'value'),
    Input('grade-dropdown-education', 'value'),
    Input('province-dropdown-education', 'value'),
    Input('active-tab-education', 'value'),
)
def update_year_dropdown(series_name, indicator, grade, province, active_tab):
    # Filter the data based on the selected filters
    dff = filter_data(data=data, series_name=series_name, indicator=indicator, province=province, grade=grade)
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


# # Callback to handle map clicks and display modal
# @callback(
#     Output("info-modal-education", "opened"),
#     Output("modal-body-education", "children"),
#     Output("geojson-education", "clickData"),  # Reset clickData
#     Input("geojson-education", "clickData"),
#     State("info-modal-education", "opened"),
#     prevent_initial_call=True
# )
# def handle_map_click(click_data, is_modal_open):
#     if click_data is None:
#         return dash.no_update, dash.no_update, dash.no_update
    
#     # Extract feature properties from the clicked data
#     feature = click_data.get("properties", {})
    
#     dff = filter_data(
#         data=data,
#         series_name=feature['Series Name']
#     )
    
#     # Prepare the content for the modal
#     modal_content = [
#         create_modal(dff, feature)
#     ]
    
#     # Open the modal, update its content, and reset clickData
#     return not is_modal_open, modal_content, None