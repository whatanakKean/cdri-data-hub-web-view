import dash
from dash import html, dcc, Input, Output, State, callback, callback_context
import dash_mantine_components as dmc
import dash_ag_grid as dag
import plotly.express as px
from ..utils.load_data import load_data
from dash_iconify import DashIconify
import plotly.graph_objects as go

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
        ], shadow="xs", p="md", radius="md", withBorder=True, style={"marginBottom": "16px"}),
        dmc.Accordion(chevronPosition="right", variant="contained", radius="md", children=[
            dmc.AccordionItem(value="bender", children=[
                dmc.AccordionControl(dmc.Group([html.Div([dmc.Text("Metadata"), dmc.Text("Bender Bending Rodríguez", size="sm", fw=400, c="dimmed")])]),),
                dmc.AccordionPanel(dmc.Text("Bender is a bending unit from the future...", size="sm"))
            ])
        ])
    ])

# Data filter function
def filter_data(data, sector, subsector_1, subsector_2, province):
    filtered_data_test = data[(data["Sector"] == sector)]
    filtered_data_test = filtered_data_test[(filtered_data_test["Sub-Sector (1)"] == subsector_1)]

    filtered_data = data[(data["Sector"] == sector) & (data["Sub-Sector (1)"] == subsector_1) & (data["Sub-Sector (2)"] == subsector_2)]
    if province != 'All': filtered_data = filtered_data[filtered_data["Province"] == province]

    return filtered_data.dropna(axis=1, how='all')

# Layout components
agriculture_and_rural_development = dmc.Container([
    dmc.Grid([
        dmc.GridCol(sidebar(data), span={"base": 12, "sm": 3}),
        dmc.GridCol([
            dmc.Paper([
                dmc.Tabs([
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
                dmc.Text(id="modal-content"), dmc.Button("Close", id="close-modal", variant="outline", color="red", className="mt-3")
            ], size="lg")
        ], span={"base": 12, "sm": 9}),
    ]),
], fluid=True, style={'paddingTop': '1rem'})

def create_map(dff):
    # Check if Latitude and Longitude columns are present
    if 'Latitude' not in dff.columns or 'Longitude' not in dff.columns:
        # Create an empty map layout with no data points
        fig = px.scatter_mapbox(
            lat=[], lon=[],  # Empty data points
            mapbox_style="open-street-map"
        ).update_layout(
            mapbox=dict(zoom=6, center=dict(lat=12.5657, lon=104.9910)),
            margin=dict(l=0, r=0, t=0, b=0)
        )
    else:
        # Generate map with data points if Latitude and Longitude exist
        fig = px.scatter_mapbox(
            dff, lat='Latitude', lon='Longitude', hover_name='Province', 
            color_continuous_scale=px.colors.cyclical.IceFire
        ).update_layout(
            mapbox_style="open-street-map", mapbox=dict(zoom=6), 
            margin=dict(l=0, r=0, t=0, b=0)
        )

    # Return the map component
    return html.Div([
        dcc.Graph(
            id='map-graph',
            figure=fig,
            config={"displaylogo": False,}
        )
    ])

def create_graph(dff):
    # Check if the DataFrame is empty or if required columns are missing
    if dff.empty or not all(col in dff.columns for col in ['Year', 'Area Harvested', 'Quantity Harvested', 'Yield']):
        return html.Div([
            dmc.Text("No Visualization Available", size="lg")
        ], style={'height': '400px', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})
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
            text="Area Harvested, Quantity Hravested, Yield",
            subtitle=dict(
                text="Description For Area Harvested, Quantity Hravested, Yield",
                font=dict(color="gray", size=13),
            ),
        ),
        xaxis=dict(
            tickmode='array',
            tickvals=dff['Year'].unique()
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
        margin=dict(t=100, b=100, l=50, r=50),
    )
    fig2 = go.Figure(layout=layout)

    # Add line plot for 'Area Harvested'
    fig2.add_trace(go.Scatter(
        x=dff['Year'],
        y=dff['Area Harvested'],
        mode='lines+markers',
        name='Area Harvested',
        line=dict(color='blue')
    ))
    fig2.add_trace(go.Scatter(
        x=dff['Year'],
        y=dff['Quantity Harvested'],
        mode='lines+markers',
        name='Quantity Harvested',
        line=dict(color='red')
    ))
    fig2.add_trace(go.Scatter(
        x=dff['Year'],
        y=dff['Yield'],
        mode='lines+markers',
        name='Yield',
        line=dict(color='green')
    ))

    return html.Div([ 
        dcc.Graph(id="figure-linechart", figure=fig2, config={
            'displaylogo': False,
            'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'custom_image',
                    'height': 500,
                    'width': 800,
                    'scale':6
                }
            })
    ])

def create_dataview(dff): 
    return html.Div([
        dag.AgGrid(id='ag-grid', columnDefs=[{"headerName": col, "field": col} for col in dff.columns], rowData=dff.to_dict('records'), style={'height': '400px', 'width': '100%'}),
        dmc.Button("Download Data", id="download-button", variant="outline", color="green", className="mt-3"),
        dcc.Download(id="download-data")
    ])

# Callbacks
@callback([Output('graph-id', 'children'), Output('map-id', 'children'), Output('dataview-container', 'children')],
          [Input("sector-dropdown", "value"), Input("subsector-1-dropdown", "value"), Input("subsector-2-dropdown", "value"),
           Input("province-dropdown", "value")])
def update_report(sector, subsector_1, subsector_2, province):
    dff = filter_data(data, sector, subsector_1, subsector_2, province)
    dff = dff.rename(columns={'Latiude': 'Latitude'})
    return create_graph(dff), create_map(dff), create_dataview(dff)

@callback(Output("download-data", "data"), Input("download-button", "n_clicks"),
          State('sector-dropdown', 'value'), State('subsector-1-dropdown', 'value'), 
          State('subsector-2-dropdown', 'value'), State('province-dropdown', 'value'))
def download_data(n_clicks, sector, subsector_1, subsector_2, province):
    if n_clicks is None: return dash.no_update
    dff = filter_data(data, sector, subsector_1, subsector_2, province)
    return dict(content=dff.to_csv(index=False), filename="data.csv", type="application/csv")


@callback(
    [Output("info-modal", "opened"), Output("modal-content", "children")],
    [Input("map-graph", "clickData"), Input("close-modal", "n_clicks")],
    prevent_initial_call=True
)
def manage_modal(clickData, close_click):
    # Identify which input triggered the callback
    ctx = callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Handle modal close
    if trigger_id == "close-modal":
        return False, ""

    # Handle modal open and populate content
    elif trigger_id == "map-graph":
        if clickData:
            lat = clickData['points'][0]['lat']
            lon = clickData['points'][0]['lon']
            return True, f"Latitude: {lat}, Longitude: {lon}"

    # Default return (shouldn't reach here)
    return False, ""



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
    filtered_data = filter_data(data, sector, subsector_1, subsector_2, province)
    
    # Extract the available indicators based on the columns in the filtered data
    # We'll exclude 'Sector', 'Sub-Sector (1)', 'Sub-Sector (2)', and 'Province' from the columns
    indicator_columns = [col for col in filtered_data.columns if col not in ['Sector', 'Sub-Sector (1)', 'Sub-Sector (2)', 'Province', 'Series Name', 'Area planted unit', 'Area Harvested Unit', 'Year','Yield Unit', 'Quantity Harvested Unit', 'Latiude', 'Longitude', 'Source', 'Quantity Unit', 'Value Unit', 'Pro code']]
    
    # If no indicators are available, return an empty list
    if not indicator_columns:
        return [], []
    
    # Prepare the options for the multi-select dropdown
    indicator_options = [{'label': col, 'value': col} for col in indicator_columns]
    
    # Default value is the first indicator (if available)
    default_value = indicator_columns[0] if indicator_columns else []
    
    return indicator_options, [default_value]