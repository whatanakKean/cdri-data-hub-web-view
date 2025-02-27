import json
import math
import sqlite3
import string
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
                value='Student Flow Rates', 
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
                label="Select Province", 
                id="province-dropdown-education", 
                value="Cambodia",
        	    data=[{'label': str(option), 'value': str(option)} for option in sorted(data["Province"].dropna().unique())],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
            ),
            dmc.SegmentedControl(
                id="segmented-grade-level",
                value="Level",
                data=[
                    {"value": "Level", "label": "Level"},
                    {"value": "Grade", "label": "Grade"},
                ],
                mt="md",
                fullWidth=True,
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
                label="Select Year", 
                id="year-dropdown-education", 
                value=str(data["Year"].dropna().unique()[-1]),
        	    data=[{'label': str(option), 'value': str(option)} for option in sorted(data["Year"].dropna().unique())],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
            ),
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
                                    dmc.TabsTab("Data View", leftSection=DashIconify(icon="tabler:database"), value="dataview"),
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
        # dcc.Download(id="download-data-education")
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
    
    if series_name == "Occupations of School Dropouts":
        return html.Div([
            # Blurred Map Container
            html.Div([
                dl.Map(
                    style={
                        'width': '100%',
                        'height': '450px',
                        'filter': 'blur(8px)'  # Apply blur effect to the map
                    },
                    center=[0, 0],
                    zoom=6,
                    children=[
                        dl.TileLayer(url="https://stamen-tiles.a.ssl.fastly.net/toner-lite/{z}/{x}/{y}.png"),
                        html.Div(children=get_info(is_gis=False), className="info", 
                                style={"position": "absolute", "top": "20px", "right": "20px", "zIndex": "1000"}),
                    ],
                    attributionControl=False,
                )
            ], style={
                "position": "relative",
                "overflow": "hidden"  # Prevents overflow from blur effect
            }),

            # Overlay Message
            html.Div(
                "GIS is not available for this dataset",
                style={
                    "position": "absolute",
                    "top": 0,
                    "left": 0,
                    "width": "100%",
                    "height": "100%",
                    "display": "flex",
                    "justify-content": "center",
                    "align-items": "center",
                    "font-size": "20px",
                    "font-weight": "bold",
                    "color": "#333",
                    "zIndex": 1000,
                    "background": "rgba(255, 255, 255, 0.3)"
                }
            )
        ], style={'position': 'relative', 'zIndex': 0})

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
    # ctg = [f"{int(classes[i])}+" for i in range(len(classes))]
    ctg = [f"" for i in range(len(classes))]
    colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale, width=30, height=300, position="bottomright")

    if 'Province' in dff.columns:
        if dff['Province'].unique() == 'Cambodia':
            dff = filter_data(data=data, series_name=dff['Series Name'].unique()[0], indicator=dff['Indicator'].unique()[0], grade=dff['Grade'].unique()[0], year=year)

        # ctg = [f"{int(classes[i])}+" for i in range(len(classes))]
        ctg = [f"" for i in range(len(classes))]
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
                    center=[12.5657, 104.9910],
                    zoom=7,
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
                    center=[12.5657, 104.9910],
                    zoom=7,
                    children=[
                        dl.TileLayer(url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
                        geojson,
                        colorbar,
                        html.Div(children=get_info(series_name=series_name, indicator=indicator, indicator_unit=indicator_unit, year=year), id="info-education", className="info", style={"position": "absolute", "top": "20px", "right": "20px", "zIndex": "1000"}),
                    ],
                    attributionControl=False,
            )],
            style={
                'position': 'relative',
                'zIndex': 0,
            }
        )


def create_graph(dff, year):
    series_name = dff['Series Name'].unique()[0]
    indicator = dff['Indicator'].unique()[0]
    
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
            color='rgba(0, 0, 0, 0.6)',
            showgrid=True,
            gridwidth=0.5,
            griddash='dot',
            tickformat=',',
            rangemode='tozero',
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
            y=-0.23,
            xanchor="center",
            x=0.5
        ),
        annotations=[dict(
            x=0.5,
            y=-0.30,
            xref="paper",
            yref="paper",
            text=f"Source: {dff['Source'].unique()[0]}",
            showarrow=False,
            font=dict(
                color='rgba(0, 0, 0, 0.6)',
                size=12
            )
        )],
        xaxis=dict(
            tickmode='auto',
            color='rgba(0, 0, 0, 0.6)',
            tickvals=dff['Year'].unique(),
        ),
        margin=dict(t=100, b=80, l=50, r=50, pad=10),
    )


    if series_name == 'Occupations of School Dropouts':
        custom_order = [
            "Elementary occupations",
            "plant and machine operators and assemblers",
            "Craft and related trades workers",
            "Skilled agricultural and fishery workers",
            "Service and shop and market sales workers",
            "Armed forces",
            "Clerks",
            "Technicians and associate professionals",
            "Professionals",
            "Legislations, senior officials and managers"
        ]
        
        # Filter the data for the latest year
        latest_data = dff[dff['Year'] == year]

        # Get unique sub-sectors
        sub_sectors = latest_data['Sub-Sector (1)'].unique()

        # Create a list to store traces for the grouped bar chart
        traces = []

        line_color = ["#A80000", "#156082", "#8EA4BC"]
        # Iterate over each sub-sector and createf a trace for it
        for idx, sub_sector in enumerate(sub_sectors):
            # Filter data for the current sub-sector
            sub_sector_data = latest_data[latest_data['Sub-Sector (1)'] == sub_sector]

            # Create a trace for this sub-sector, using its 'Occupation' and 'Indicator Value'
            traces.append(go.Bar(
                y=sub_sector_data['Occupation'],
                x=sub_sector_data['Indicator Value'],
                name=sub_sector,
                orientation='h',
                marker=dict(color=line_color[idx])
            ))

        # Create the layout for the grouped bar chart
        layout = go.Layout(
            images=[dict(
                source="./assets/CDRI Logo.png",
                xref="paper", yref="paper",
                x=1, y=1.1,
                sizex=0.2, sizey=0.2,
                xanchor="right", yanchor="bottom"
            )],
            title=dict(
                text=f"Occupations of School Dropouts ({year})"
                + f"<br><span style='display:block; margin-top:8px; font-size:70%; color:rgba(0, 0, 0, 0.6);'>{sub_sector_data['Indicator Unit'].unique()[0]}</span>"
            ),
            font=dict(
                family='BlinkMacSystemFont, -apple-system, sans-serif',
                color='rgb(24, 29, 31)'
            ),
            hovermode="y unified",
            barmode='group',  # Group the bars by sub-sector
            yaxis=dict(
                title="Occupation",
                color='rgba(0, 0, 0, 0.6)',
                categoryorder="array", categoryarray=custom_order
            ),
            xaxis=dict(
                gridcolor='rgba(169, 169, 169, 0.7)',
                color='rgba(0, 0, 0, 0.6)',
                gridwidth=0.5,
                griddash='dot',
                range = [0, 5000] if indicator == "Frequency" else [0, 40]
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.23,
                xanchor="center",
                x=0.5,
                font=dict(
                    color='rgba(0, 0, 0, 0.6)'
                )
            ),
            annotations=[dict(
                x=0.5,  # Center horizontally (matches legend's x)
                y=-0.30,
                xref="paper",
                yref="paper",text=f"Source: {dff['Source'].unique()[0]}",  # Customize this
                showarrow=False,
                font=dict(
                    color='rgba(0, 0, 0, 0.6)',
                    size=12
                )
            )],
            margin=dict(t=100, b=100, l=50, r=50),
            plot_bgcolor='white',
        )

        # Create the figure for the grouped bar chart
        fig = go.Figure(data=traces, layout=layout)

        # Create figure component (without alert)
        figure_component = html.Div([
            dcc.Graph(
                id="figure-barchart",
                figure=fig,
                style={'minHeight': '460px'},
                config={
                    'displaylogo': False,
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': f'cdri_datahub_viz_{year}',
                        'height': 500,
                        'width': 800,
                        'scale': 6
                    },
                },          
                responsive=True,
            ),
            dmc.Divider(size="sm"),
        ])

        return html.Div([
            html.Div([figure_component]),
            dmc.Alert(
                """Figures illustrate economic activities after dropping out of school using data from the Cambodia Socio-Economic Survey. Due to data availability, individuals aged 6–19 are assumed to be current students who have dropped out, while those aged 20–40 are considered students who dropped out earlier and have been out of school for a longer period.

    The figures show that after dropping out, current dropouts are primarily engaged in low-skilled jobs, such as elementary occupations. In contrast, when comparing current dropouts with older dropouts, it is evident that older dropouts are more involved in high-skilled jobs, such as clerks, professionals, technicians and associate professionals, legislators, senior officials, and managers. This is likely because older dropouts have been out of school for a longer period and may have developed skills through work experience and/or further education.

    However, it is important to note that we cannot guarantee that students aged 16–19 who are currently classified as dropouts did so recently; they may have dropped out earlier.""",
                title="Description",
                color="green"
            )
        ])
    
    else:
        if 'Grade' in dff.columns:
            traces = []
            for idx, grade in enumerate(dff['Grade'].unique()):
                grade_data = dff[dff['Grade'] == grade]
                line_color = ["#156082", "#A80000", "#8EA4BC", "#FF5733", "#F4A261", "#E9C46A", "#2A9D8F", "#E76F51", "#457B9D", "#D4A373", "#6A0572", "#264653"]
                sub_sector = dff["Sub-Sector (1)"].unique()[0]
                
                if sub_sector == "Level":
                    traces.append(go.Scatter(
                        x=grade_data['Year'],
                        y=grade_data['Indicator Value'],
                        mode='lines+markers' if len(grade_data) == 1 else 'lines',
                        name=f"{grade}",
                        line=dict(color=line_color[idx])
                    ))
                elif sub_sector == "Grade":
                    traces.append(go.Scatter(
                        x=grade_data['Year'],
                        y=grade_data['Indicator Value'],
                        mode='lines+markers' if len(grade_data) == 1 else 'lines',
                        name=f"{grade}",
                        line=dict(color=line_color[idx])
                    ))
                else:
                    traces.append(go.Scatter(
                        x=grade_data['Year'],
                        y=grade_data['Indicator Value'],
                        mode='lines+markers' if len(grade_data) == 1 else 'lines',
                        name=f"{grade}",
                        line=dict(color=line_color[idx])
                    ))
        else:
            traces = [go.Scatter(
                x=dff['Year'],
                y=dff['Indicator Value'],
                mode='lines+markers' if len(dff) == 1 else 'lines',
                name=indicator,
                line=dict(color="#156082")
            )]
            
        fig = go.Figure(layout=layout)
        for trace in traces:
            fig.add_trace(trace)
            
        if series_name == "Successful Student":
            fig.update_layout(
                title=dict(
                    text=f"{indicator} in {dff['Province'].unique()[0]}"
                        + f"<br><span style='display:block; margin-top:8px; font-size:70%; color:rgba(0, 0, 0, 0.6);'>{dff['Indicator Unit'].unique()[0]}</span>"
                )
            )
        else:
            fig.update_layout(
                title=dict(
                    text=f"{series_name}: {indicator} in {dff['Province'].unique()[0]}"
                        + f"<br><span style='display:block; margin-top:8px; font-size:70%; color:rgba(0, 0, 0, 0.6);'>{dff['Indicator Unit'].unique()[0]}</span>"
                )
            )
        
    return html.Div([
        dcc.Graph(
            id="figure-linechart",
            figure=fig,
            style={'minHeight': '460px'},
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
            "The figure illustrates the student dropout rates from 2012 to 2023 across different grade levels: primary school, lower-secondary school, and upper-secondary school in Cambodia. It shows that the overall student dropout rates declined dramatically, a trend that can be attributed to the government’s efforts to improve the education system in Cambodia. Notably, during the 2019-2020 academic year, the overall dropout rate for upper-secondary school reached an unusually low level, primarily due to Grade 12 data. This was followed by a decline in class repetition compared to other years. In other words, most students that year were promoted to the next grade. This was primarily due to the COVID-19 pandemic, during which schools were closed, and the Ministry of Education, Youth, and Sport (MoEYS) announced the automatic promotion of all students. As a result, the dropout rate for that year was exceptionally low."
            if series_name == "Student Flow Rates" and indicator == "Dropout" 
            else "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            title="Description",
            color="green"
        )
    ]) 

# Calllback for info on map
@callback(Output("info-education", "children"), Input('series-name-dropdown-education', 'value'), Input('year-dropdown-education', 'value'), Input('indicator-dropdown-education', 'value'),  Input('indicator-unit-education', 'data'), Input("geojson-education", "hoverData"))
def info_hover(series_name, year, indicator, indicator_unit, feature):
    return get_info(series_name=series_name, indicator=indicator, feature=feature, indicator_unit=indicator_unit, year=year)


# Callbacks
@callback([Output('graph-id-education', 'children'), Output('map-id-education', 'children'), Output('dataview-container-education', 'children'), Output('metadata-panel-education', 'children'), Output('indicator-unit-education', 'data')],
          [Input('series-name-dropdown-education', 'value'), Input('segmented-grade-level', 'value'),
           Input("indicator-dropdown-education", "value"), Input("year-dropdown-education", "value"), Input('grade-dropdown-education', 'value'), Input('province-dropdown-education', 'value'),])
def update_report(series_name, grade_or_level, indicator, year, grade, province):
    dff = filter_data(data=data, series_name=series_name, subsector_1=grade_or_level, indicator=indicator, grade=grade, province=province)

    indicator_unit = dff['Indicator Unit'].unique()
    return create_graph(dff, year), create_map(dff, year), create_dataview(dff), create_metadata(dff), indicator_unit.tolist()


# @callback(Output("download-data-education", "data"), Input("download-button-education", "n_clicks"),
#           State('series-name-dropdown-education', 'value'), State('segmented-grade-level', 'value'), State('indicator-dropdown-education', 'value'), Input('grade-dropdown-education', 'value'), Input('province-dropdown-education', 'value'),)
# def download_data(n_clicks, series_name, grade_or_level, indicator, grade, province):
#     if n_clicks is None: return dash.no_update
#     dff = filter_data(data=data, series_name=series_name, subsector_1=grade_or_level,indicator=indicator, grade=grade, province=province)
#     dff = dff.loc[:, ~(dff.apply(lambda col: col.eq("").all(), axis=0))]
#     return dict(content=dff.to_csv(index=False), filename="data.csv", type="application/csv")


@callback(
    [Output('segmented-grade-level', 'style'),
     Output('segmented-grade-level', 'value')],
    Input('series-name-dropdown-education', 'value')
)
def update_segmented_control_visibility(series_name):
    # If the series name is "Student Flow Rates", show the segmented control
    if series_name == "Student Flow Rates":
        return {'visibility': 'visible', 'position': 'relative'}, "Level"  # Keep value None when visible
    else:
        return {'visibility': 'hidden', 'position': 'absolute'}, None  # Clear value when hidden
    
@callback(
    Output('grade-dropdown-education', 'data'),
    Output('grade-dropdown-education', 'value'),
    Output('grade-dropdown-education', 'style'),
    Output('grade-dropdown-education', 'label'),
    Input('series-name-dropdown-education', 'value'),
    Input('segmented-grade-level', 'value')
)
def update_grade(series_name, grade_or_level):
    # Filtering data based on Series Name
    if series_name == "Student Flow Rates":
        # Filter based on the 'Sub-Sector (1)' column using grade_or_level
        grade_options = data[(data["Series Name"] == series_name) & 
                              (data["Sub-Sector (1)"] == grade_or_level)]["Grade"].dropna().str.strip().unique()
    else:
        # Default behavior (filtering just by Series Name)
        grade_options = data[(data["Series Name"] == series_name)]["Grade"].dropna().str.strip().unique()

    # Control visibility based on available options
    style = {'display': 'block'} if grade_options.size > 0 else {'display': 'none'}

    # Update the label based on the segmented control value
    label = "Select Level" if grade_or_level == "Level" else "Select Grade"

    return [{'label': option, 'value': option} for option in ['All'] + list(grade_options)], 'All' if grade_options.size > 0 else None, style, label


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
    return [{'label': option, 'value': option} for option in sorted(province_options)], "Cambodia" if province_options.size > 0 else None, style

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
    dropdown_style = {'display': 'block'} if (active_tab == 'map' or (active_tab == 'graph' and series_name == 'Occupations of School Dropouts')) else {'display': 'none'}


    return year_options, default_value, dropdown_style