import dash
from dash import html, dcc, Input, Output, State, callback, callback_context
import dash_mantine_components as dmc
import dash_ag_grid as dag
import plotly.express as px
from ..utils.load_data import load_data
from dash_iconify import DashIconify

# Load data
data = load_data(file_path="src/data/Datahub_Agri_Latest.xlsx", sheet_name="Database")

# Common dropdown generator
def create_dropdown(id, label, value, options):
    return dmc.Select(
        label=label, id=id, value=value, clearable=True, searchable=True,
        data=[{'label': option, 'value': option} for option in options],
        maxDropdownHeight=600, style={"marginBottom": "16px"}, checkIconPosition="right"
    )

# Sidebar components
def sidebar(data):
    return dmc.Stack([
        dmc.Paper([
            create_dropdown("sector-dropdown", "Select Sector", 'Agriculture', data["Sector"].dropna().unique()),
            create_dropdown("subsector-1-dropdown", "Select Sub-Sector (1)", 'Production', data["Sub-Sector (1)"].dropna().unique()),
            create_dropdown("subsector-2-dropdown", "Select Sub-Sector (2)", 'Rice', data["Sub-Sector (2)"].dropna().unique()),
            create_dropdown("indicator-dropdown", "Select Indicators", ["Area Planted"], data.columns.unique()),
            create_dropdown("province-dropdown", "Select Province", 'All', ['All'] + list(data["Province"].dropna().unique())),
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
    filtered_data = data[(data["Sector"] == sector) & (data["Sub-Sector (1)"] == subsector_1) & (data["Sub-Sector (2)"] == subsector_2)]
    if province != 'All': filtered_data = filtered_data[filtered_data["Province"] == province]
    filtered_data.to_csv("test.csv", index=False)
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
                    dmc.TabsPanel(html.Div(id='map-id'), value="map"),  # Changed to html.Div
                    dmc.TabsPanel(html.Div(id='graph-id'), value="graph"),  # Changed to html.Div
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

# Create map, graph, and table views
def create_map(dff):
    if 'Latitude' not in dff.columns or 'Longitude' not in dff.columns:
        return html.Div([dmc.Text("Error: Latitude and Longitude columns are missing.")])
    fig = px.scatter_mapbox(dff, lat='Latitude', lon='Longitude', hover_name='Province', color_continuous_scale=px.colors.cyclical.IceFire).update_layout(
        mapbox_style="open-street-map", mapbox=dict(zoom=6), margin=dict(l=0, r=0, t=0, b=0)
    )
    return html.Div([dcc.Graph(figure=fig)])

# Modify the create_graph function to return html.Div directly
def create_graph(dff):
    fig1 = px.histogram(dff, x='Province', y='Area Planted', color='Year', barmode='group', title="Title", height=400).update_layout(
        barmode='group', xaxis_title='Province', yaxis_title='Area Planted', hovermode="x unified", 
        title={'text': "Title<br><sub>Subtitle describing the data</sub>", 'x': 0.05, 'xanchor': 'left', 'y': 0.9})
    return html.Div([
        dcc.Graph(figure=fig1),
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
    dff = dff.rename(columns={'Latiude': 'Latitude'})  # Correct any typos if necessary
    # Returning html.Div with created map and graph
    return create_graph(dff), create_map(dff), create_dataview(dff)

@callback(Output("download-data", "data"), Input("download-button", "n_clicks"),
          State('sector-dropdown', 'value'), State('subsector-1-dropdown', 'value'), 
          State('subsector-2-dropdown', 'value'), State('province-dropdown', 'value'))
def download_data(n_clicks, sector, subsector_1, subsector_2, province):
    if n_clicks is None: return dash.no_update
    dff = filter_data(data, sector, subsector_1, subsector_2, province)
    return dict(content=dff.to_csv(index=False), filename="data.csv", type="application/csv")