import json
import math
import sqlite3
import string
from dash import html, dcc, Input, Output, callback
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
                label="Select Dataset", 
                id="series-name-dropdown", 
                value='Rice Production', 
                data=[{'label': option, 'value': option} for option in ["Paddy Rice Price"] + [option for option in data["Series Name"].dropna().str.strip().unique() if option and option != "Paddy Rice Price"]],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                checkIconPosition="right",
                allowDeselect=False,
            ),
            dmc.Select(
                label="Select Type", 
                id="subsector-2-dropdown", 
                value='Fragrant Rice', 
                data=[{'label': option, 'value': option} for option in data["Sub-Sector (2)"].dropna().str.strip().unique() if option],
                withScrollArea=False,
                styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                mt="md",
                checkIconPosition="right",
                allowDeselect=False,
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
                label="Select Variable", 
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
        	    data=[{'label': str(option), 'value': str(option)} for option in sorted(data["Year"].dropna().unique())],
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
                                    dmc.TabsTab("Map View", leftSection=DashIconify(icon="tabler:map"), value="map", id="map-tab"),
                                    dmc.TabsTab("Visualization", leftSection=DashIconify(icon="tabler:chart-bar"), value="graph", id="graph-tab"),
                                    dmc.TabsTab("Data View", leftSection=DashIconify(icon="tabler:database"), value="dataview", id="dataview-tab"),
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
                        id="active-tab", value="map", color="#336666"
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
    
    # Remove columns where all values are empty strings
    pivoted_data = pivoted_data.loc[:, ~(pivoted_data.apply(lambda col: col.eq("").all(), axis=0))]
    
    return html.Div([
        dag.AgGrid(id='ag-grid', defaultColDef={"filter": True}, columnDefs=[{"headerName": col, "field": col} for col in pivoted_data.columns], rowData=pivoted_data.to_dict('records'), style={'height': '400px'}),
        dmc.Button("Download Data", id="download-button", variant="outline", color="#336666", mt="md", style={'marginLeft': 'auto', 'display': 'flex', 'justifyContent': 'flex-end'}),
        # dcc.Download(id="download-data")
    ])
    
def create_metadata(dff):
    if 'Source' in dff and dff['Source'].dropna().any():
        return dmc.Text(
            f"Sources: {', '.join(dff['Source'].dropna().unique())}", size="sm"
        )
    return ""

def create_map(dff, year):
    series_name = dff['Series Name'].unique()[0]
    indicator = dff['Indicator'].unique()[0]
    indicator_unit = dff['Indicator Unit'].unique()[0]
    
    if series_name == "Paddy Rice Price":
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
                        dl.TileLayer(url="http://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png"),
                        html.Div(children=get_info(is_gis=False), className="info", 
                                style={"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000"}),
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
    else:
        dff = dff[dff["Year"] == year]
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
        # ctg = [f"{int(classes[i])}+" for i in range(len(classes))]
        ctg = [f"" for i in range(len(classes))]
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
                        center=[12.5657, 104.9910],
                        zoom=7,
                        children=[
                            dl.TileLayer(url="http://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png"),
                            geojson,
                            colorbar,
                            html.Div(children=get_info(series_name=series_name, indicator=indicator, indicator_unit=indicator_unit, year=year), id="info", className="info", style={"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000"}),
                        
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
                        center=[20, 0],
                        zoom=6,
                        children=[
                            dl.TileLayer(url="http://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png"),
                            geojson, 
                            colorbar,
                            html.Div(children=get_info(series_name=series_name, indicator=indicator, indicator_unit=indicator_unit, year=year), id="info", className="info", style={"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000"}),
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
                        center=[12.5657, 104.9910],
                        zoom=7,
                        children=[
                            dl.TileLayer(url="http://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png"),
                            geojson,
                            html.Div(children=get_info(series_name=series_name, indicator=indicator, indicator_unit=indicator_unit, year=year), id="info", className="info", style={"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000"}),
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
            y=1,
            xanchor="right",    
            x=1
        ),
        xaxis=dict(
            showgrid=False,
            tickmode='auto',
            color='rgba(0, 0, 0, 0.6)',
            tickvals=dff_filtered['Year'].unique(),
            title=f"<span style='display:block; margin-top:8px; font-size:85%; color:rgba(0, 0, 0, 0.7);'>Source: {dff['Source'].unique()[0]}</span>",
        ),
        margin=dict(t=100, b=80, l=50, r=50, pad=10),
    )

    if series_name == "Paddy Rice Price":
        graphs = []  # Store multiple figures
        prefixes = [f"({letter})" for letter in string.ascii_lowercase]
        
        for idx, variety in enumerate(dff['Variety'].unique()):
            dff_variety = dff[dff['Variety'] == variety]
            dff_variety['Date'] = pd.to_datetime(dff_variety['Date'])
            dff_variety = dff_variety.sort_values(by='Date')
            
            # Create figure
            fig = go.Figure(layout=layout)
            fig.add_trace(go.Scatter(
                x=dff_variety['Date'],
                y=dff_variety['Indicator Value'],
                mode = 'lines+markers' if len(dff_variety.dropna()) == 1 else 'lines',
                name=variety,
                connectgaps=False,
                line=dict(color="#156082")
            ))  
            title_prefix = prefixes[idx] if idx < len(prefixes) else ""  

            fig.update_layout(
                title=dict(
                    text=f"{title_prefix} {dff_variety['Sub-Sector (1)'].unique()[0]} of {variety}<br><span style='display:block; margin-top:8px; font-size:70%; color:rgba(0, 0, 0, 0.6);'>{dff_variety['Indicator Unit'].unique()[0]}</span>"
                ),
                font=dict(size=10),
                images=[dict(
                    source="./assets/CDRI Logo.png",
                    xref="paper", yref="paper",
                    x=1, y=1.15,
                    sizex=0.2, sizey=0.2,
                    xanchor="right", yanchor="bottom"
                )],
                xaxis=dict(
                    tickmode='auto',
                    color='rgba(0, 0, 0, 0.6)',
                    tickvals=dff_filtered['Year'].unique(),
                    title=f"<span style='display:block; margin-top:8px; font-size:85%; color:rgba(0, 0, 0, 0.7);'>Source: {dff_variety['Source'].unique()[0]}</span>",
                ),
            )
            
            if dff_variety['Sub-Sector (1)'].unique()[0] == "FOB Price":
                fig.update_layout(
                    title=dict(
                        text=f"{title_prefix} {variety} Price at the Port <br><span style='display:block; margin-top:8px; font-size:70%; color:rgba(0, 0, 0, 0.6);'>{dff_variety['Indicator Unit'].unique()[0]}</span>"
                    )
                )
            
            # Add Annotation
            if dff_variety["Variety"].unique() in ["Sen Kra Ob 01", "Indica - Long B", "Indica (Average)"]:
                fig.update_layout(
                    shapes=[
                        dict(
                            type="rect",
                            xref="x", yref="paper",
                            x0=pd.to_datetime("2023-07-01"), x1=pd.to_datetime("2024-09-09"),
                            y0=0, y1=1,
                            fillcolor="#808080",
                            opacity=0.25,
                            layer="below",
                            line=dict(width=0)
                        )
                    ]
                )
            if dff_variety["Variety"].unique() in ["White Rice (Hard Texture)", "White Rice (Soft Texture)", "OM", "IR"]:
                fig.update_layout(
                    shapes=[
                        dict(
                            type="rect",
                            xref="x", yref="paper",
                            x0=pd.to_datetime("2024-12-01"), x1=pd.to_datetime("2025-02-01"),
                            y0=0, y1=1,
                            fillcolor="#808080",
                            opacity=0.25,
                            layer="below",
                            line=dict(width=0)
                        )
                    ]
                )

            # Create individual graph component
            graph_component = dcc.Graph(
                id=f"figure-linechart-{variety}", 
                figure=fig, 
                style={'height': '400px', 'width': '100%'},
                config={
                    'displaylogo': False,
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': f'cdri_datahub_viz_{variety}',
                        'height': 500,
                        'width': 800,
                        'scale': 6
                    },
                },
                responsive=True,
            )
            graphs.append(graph_component)

            grid = dmc.Grid(
                gutter="none",
                children=[
                    # Responsive columns: 6/12 (half width) on small screens and up
                    dmc.GridCol(
                        children=graphs[0] if len(graphs) > 0 else "",
                        span={"base": 12, "sm": 6}  # Full width on base, half on small screens+
                    ),
                    dmc.GridCol(
                        children=graphs[1] if len(graphs) > 1 else "",
                        span={"base": 12, "sm": 6}
                    ),
                    dmc.GridCol(
                        children=graphs[2] if len(graphs) > 2 else "",
                        span={"base": 12, "sm": 6}
                    ),
                    dmc.GridCol(
                        children=graphs[3] if len(graphs) > 3 else "",
                        span={"base": 12, "sm": 6}
                    ),
                ],
                style={"width": "100%"}
            )

        # Return the grid layout
        return html.Div([
            grid,
            # Uncomment if you want to keep the alert
            dmc.Alert(
                """Figures (a) and (b) illustrate the paddy prices of aromatic Pka Romdoul/Jasmine and Sen Kra Ob, respectively, while Figure (c) shows the European rice price for Indica – Long B, and Figure (d) displays the average European rice price for Indica.
                
                It is important to note that Cambodia produces two types of rice: aromatic/fragrant rice and white rice. Aromatic rice varieties, such as Pka Romdoul/Jasmine, are seasonal and harvested only between November and December each year, while another aromatic Sen Kra Ob can be grown year-round. Paddy prices in Cambodia are typically influenced by global markets, as these are premium rice products primarily exported to international markets, such as Europe.
                
                For example, when comparing Figure (b) with Figure (c), it is evident that the European rice price for Indica – Long B increased significantly from July 2023 onwards, followed by a rise in the price of Cambodia's aromatic paddy, Sen Kra Ob. This is due to India's rice export ban in July 2023, which disrupted global rice markets and benefitted Cambodia's rice exports, driving up prices.
                """
                if dff["Sub-Sector (2)"].unique() == "Fragrant Rice" 
                else """Figures (a) and (b) illustrate the paddy prices of white rice varieties OM and IR, respectively, while Figures (c) and (d) show the prices of white rice at the Sihanoukville port for both soft and hard textures, respectively.

                    It is important to note that, unlike most aromatic rice varieties such as Pka Romdoul and Jasmine, OM and IR are non-photoperiod-sensitive varieties. These varieties have higher yields and can be cultivated year-round. Additionally, they have wide markets in countries such as Vietnam and China, where they are consumed and used in processed foods. While their prices are influenced by global market trends, they are more significantly impacted by purchasing patterns in Vietnam.

                    For example, the paddy prices of OM and IR increased dramatically from July 2023 to the present. This rise can be attributed to India's rice export ban in July 2023, which disrupted global rice markets and benefited Cambodia's rice exports, driving up prices. However, their prices dipped slightly between the end of December and January, likely due to delayed purchases from Vietnam, coinciding with the Chinese and Vietnamese New Year celebrations. After the holiday period, prices returned to normal levels.
                    """,
                title="Description",
                color="green"
            )
        ])
    
    else:
        # Create figure
        fig1 = go.Figure(layout=layout)
        fig1.add_trace(go.Scatter(
            x=dff_filtered['Year'],
            y=dff_filtered['Indicator Value'],
            mode='lines+markers' if len(dff_filtered) == 1 else 'lines',
            name=indicator,
            line=dict(color="#156082")
        ))
        if series_name == "Rice Production":
            fig1.update_layout(
                title=dict(
                    text=f"{dff['Sub-Sector (2)'].unique()[0]} {dff['Indicator'].unique()[0]}"
                        + (f" in {dff['Province'].unique()[0]}" if 'Province' in dff.columns and dff['Province'].nunique() == 1 else "")
                        + (f" to {dff['Markets'].unique()[0]}" if 'Markets' in dff.columns and dff['Markets'].nunique() == 1 else "")
                        + f"<br><span style='display:block; margin-top:8px; font-size:70%; color:rgba(0, 0, 0, 0.6);'>{dff['Indicator Unit'].unique()[0]}</span>"
                )
            )
        else:  
            fig1.update_layout(
                title=dict(
                    text=f"{series_name} {dff['Indicator'].unique()[0]}"
                        + (f" in {dff['Province'].unique()[0]}" if 'Province' in dff.columns and dff['Province'].nunique() == 1 else "")
                        + (f" to {dff['Markets'].unique()[0]}" if 'Markets' in dff.columns and dff['Markets'].nunique() == 1 else "")
                        + f"<br><span style='display:block; margin-top:8px; font-size:70%; color:rgba(0, 0, 0, 0.6);'>{dff['Indicator Unit'].unique()[0]}</span>"
                )
            )

        # Return graph
        return html.Div([ 
            dcc.Graph(
                id="figure-linechart", 
                figure=fig1, 
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
            # dmc.Alert(
            #     "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            #     title="Description",
            #     color="green"
            # ),
        ])
        
# Callbacks
@callback([Output('graph-id', 'children'), Output('map-id', 'children'), Output('dataview-id', 'children'), Output('metadata-panel', 'children'), Output('indicator-unit', 'data')],
          [Input("series-name-dropdown", "value"), Input("subsector-2-dropdown", "value"), 
           Input("province-dropdown", "value"), Input("indicator-dropdown", "value"), Input("year-dropdown", "value")])
def update_report(series_name, subsector_2, province, indicator, year):
    dff = filter_data(
        data=data,
        series_name=series_name,
        subsector_2=subsector_2,
        province=province if province else None,
        indicator=indicator
    )
    dff = dff.rename(columns={'Latiude': 'Latitude'})
    indicator_unit = dff['Indicator Unit'].unique()

    return create_graph(dff), create_map(dff, year), create_dataview(dff), create_metadata(dff), indicator_unit.tolist()


# @callback(Output("download-data", "data"), Input("download-button", "n_clicks"),
#           State('series-name-dropdown', 'value'), State("series-name-dropdown", "value"), State('province-dropdown', 'value'), State('indicator-dropdown', 'value'))
# def download_data(n_clicks, series_name, subsector_2, province, indicator):
#     if n_clicks is None: return dash.no_update
#     dff = filter_data(data=data, series_name=series_name, subsector_2=subsector_2, province=province, indicator=indicator)
#     dff = dff.loc[:, ~(dff.apply(lambda col: col.eq("").all(), axis=0))]
#     return dict(content=dff.to_csv(index=False), filename="data.csv", type="application/csv")


# Calllback for info on map
@callback(Output("info", "children"), Input('series-name-dropdown', 'value'), Input('year-dropdown', 'value'), Input('indicator-dropdown', 'value'), Input('indicator-unit', 'data'), Input("geojson", "hoverData"))
def info_hover(series_name, year, indicator, indicator_unit, feature):
    return get_info(series_name=series_name, indicator=indicator, feature=feature, indicator_unit=indicator_unit, year=year)

@callback(
    Output('subsector-2-dropdown', 'data'),
    Output('subsector-2-dropdown', 'value'),
    Output('subsector-2-dropdown', 'style'),
    Input('series-name-dropdown', 'value')
)
def update_subsector_2(series_name):
    if series_name.lower() != "paddy rice price":
        return [], None, {'display': 'none'}
    
    province_options = data[(data["Series Name"] == series_name)]["Sub-Sector (2)"].dropna().str.strip().unique()

    style = {'display': 'block'} if province_options.size > 0 else {'display': 'none'}
    return [{'label': option, 'value': option} for option in list(sorted(province_options))], 'Fragrant Rice', style

@callback(
    Output('province-dropdown', 'data'),
    Output('province-dropdown', 'value'),
    Output('province-dropdown', 'style'),
    Input('series-name-dropdown', 'value')
)
def update_province(series_name):
    if series_name.lower() == "paddy rice price":
        return [], None, {'display': 'none'}
    
    province_options = data[(data["Series Name"] == series_name)]["Province"].dropna().str.strip().unique()

    style = {'display': 'block'} if province_options.size > 0 else {'display': 'none'}
    return [{'label': option, 'value': option} for option in ['All'] + list(sorted(province_options))], 'All', style

@callback(
    Output('indicator-dropdown', 'data'),
    Output('indicator-dropdown', 'value'),
    Input('series-name-dropdown', 'value'),
    Input('province-dropdown', 'value'),
    prevent_initial_call=False
)
def update_indicators(series_name, province):
    dff = filter_data(data=data, series_name=series_name, province=province)
    
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
    Input('province-dropdown', 'value'),
    Input('indicator-dropdown', 'value'),
    Input('active-tab', 'value'),
)
def update_year_dropdown(series_name, province, indicator, active_tab):
    if series_name.lower() == "paddy rice price":
        return [], None, {'display': 'none'}
    
    dff = filter_data(
        data=data,
        series_name=series_name,
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