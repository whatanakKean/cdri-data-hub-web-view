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

# Common dropdown generator
def create_dropdown(id, label, value, options=[]):
    return dmc.Select(
        label=label, id=id, value=value, searchable=True,
        data=[{'label': option, 'value': option} for option in options],
        maxDropdownHeight=600, style={"marginBottom": "16px"}, checkIconPosition="right"
    )

# Sidebar components
def sidebar(data):
    return dmc.Stack([
        dmc.Paper([
            create_dropdown("sector-dropdown", "Select Sector", 'Agriculture', data["Sector"].dropna().str.strip().unique()),
            create_dropdown("subsector-1-dropdown", "Select Sub-Sector (1)", 'Production', data["Sub-Sector (1)"].dropna().str.strip().unique()),
            create_dropdown("subsector-2-dropdown", "Select Sub-Sector (2)", 'Rice', data["Sub-Sector (2)"].dropna().str.strip().unique()),
            create_dropdown("indicator-dropdown", "Select Indicators", "Area Planted", data.columns.unique()),
            create_dropdown("province-dropdown", "Select Province", 'All', ['All'] + list(data["Province"].dropna().str.strip().unique())),
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

    print(">> Sector: ",filtered_data_test["Sector"].dropna().str.strip().unique())
    print(">> Sub-Sector (1)", filtered_data_test["Sub-Sector (1)"].dropna().str.strip().unique())
    print(">> Sub-Sector (2)", filtered_data_test["Sub-Sector (2)"].dropna().str.strip().unique())
    print(">> Province", filtered_data_test["Province"].dropna().str.strip().unique())

    filtered_data = data[(data["Sector"] == sector) & (data["Sub-Sector (1)"] == subsector_1) & (data["Sub-Sector (2)"] == subsector_2)]
    if province != 'All': filtered_data = filtered_data[filtered_data["Province"] == province]

    return filtered_data.dropna(axis=1, how='all').fillna('')

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
    if 'Latitude' not in dff.columns or 'Longitude' not in dff.columns:
        return html.Div([dmc.Text("Error: Latitude and Longitude columns are missing.")])
    
    fig = px.scatter_mapbox(
        dff, lat='Latitude', lon='Longitude', hover_name='Province', 
        color_continuous_scale=px.colors.cyclical.IceFire
    ).update_layout(
        mapbox_style="open-street-map", mapbox=dict(zoom=6), 
        margin=dict(l=0, r=0, t=0, b=0)
    )

    # Add a Graph component to capture click events
    return html.Div([
        dcc.Graph(
            id='map-graph',
            figure=fig,
            config={"displaylogo": False}
        )
    ])

def create_graph(dff):
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
        dcc.Graph(id="figure-linechart", figure=fig2, config={'displaylogo': False})
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
           Input("province-dropdown", "value"), Input("indicator-dropdown", "value")])
def update_report(sector, subsector_1, subsector_2, province, indicators):
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