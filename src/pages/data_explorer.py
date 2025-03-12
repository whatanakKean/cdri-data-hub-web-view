
import json
import math
import sqlite3
import string
from dash import html, dcc, Input, Output, State, callback
import dash
import dash_mantine_components as dmc
import dash_ag_grid as dag
import pandas as pd
from dash_iconify import DashIconify
import plotly.graph_objects as go
from fuzzywuzzy import process
import dash_leaflet as dl
import dash_leaflet.express as dlx
from ..utils.utils import get_info, filter_data, style_handle


from src.utils.utils import get_info
# Sample dataset
conn = sqlite3.connect("./src/data/data.db")

# Query economic_data table
query1 = "SELECT * FROM education_data;"
df1 = pd.read_sql_query(query1, conn)
query2 = "SELECT * FROM agriculture_data;"
df2 = pd.read_sql_query(query2, conn)
data = pd.concat([df1, df2], ignore_index=True)


top_7 = ["Paddy Rice Price (Fragrant Rice)", "Paddy Rice Price (White Rice)", "Rice Production: Area Planted in Battambang", "Rice Export Value to Vietnam", "Occupations of School Dropouts in 2023", "Student Flow Rates: Dropout by Grade in Cambodia", "Successful Student in Cambodia"]
combined_options = [
    {"label": f"{row}", "value": f"{row}"} for row in top_7
] + [{"label": f"{row}", "value": f"{row}"} for row in data["Tag"].unique() if row not in top_7]

# About page with suggestions autocomplete
data_explorer_page = html.Main(
    [
        html.Div(
            style={
                "height": "300px",
                "backgroundImage": "url('./assets/data-explorer-background.jpg')",
                "backgroundSize": "cover",
                "backgroundPosition": "center",
                "display": "flex",
                "flexDirection": "column",
                "justifyContent": "center",
                "alignItems": "flex-start",
                "paddingLeft": "10px",
                "paddingRight": "10px"
            },
            children=[
                dmc.Stack(
                    p="lg",
                    children=[
                        dmc.Title('CDRI Data Hub Explorer', order=1, style={'color': 'white', 'fontSize': '2rem'}),
                        dmc.Text("Explore Data and Visualizations with Natural Language", size="xl", style={'color': 'white', 'fontSize': '1rem'}),
                        # Suggestions dropdown
                        dmc.Select(
                            label="Select Dataset", 
                            id="suggestions-autocomplete",
                            data=combined_options,
                            withScrollArea=False,
                            placeholder="Ask anything...",
                            styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                            checkIconPosition="right",
                            searchable=True,
                            clearable=True,
                            leftSectionPointerEvents="none",
                            leftSection=DashIconify(icon="mingcute:ai-fill"),
                            nothingFoundMessage="Nothing found...",
                            limit=25
                        ),
                        # dmc.Autocomplete(
                        #     id="suggestions-autocomplete",
                        #     placeholder="Ask anything...",
                        #     data=combined_options,
                        #     leftSection=DashIconify(icon="mingcute:ai-fill"),
                        #     style={"width": "100%", "marginBottom": "20px"},
                        #     limit=25
                        # ),
                        dmc.RadioGroup(
                                id="indicator-radio-group",
                                label="Select Variable:",
                                size="sm",
                                children=[],
                                mt=10,
                                mb=10,
                            ),
                    ],
                    className="animate__animated animate__fadeInUp animate__fast"
                )
            ],
        ),
        
        dmc.Container(children=[
            dmc.Paper([
                html.Div(id='data-explorer-map-id'),
                html.Div(id='data-explorer-graph-id'),
                html.Div(id='data-explorer-dataview-id', style={'marginTop': '20px'})
                ], shadow="xs", p="md", radius="md", withBorder=True),
        ], fluid=True),
        dcc.Store(id='data-explorer-filter-state'),
    ],
)

def create_dataview(dff, year):
    dff = dff[dff["Year"] == year]
    
    dff = dff[['Province', 'Indicator', 'Indicator Value']]
    pivoted_data = dff.pivot_table(
        index=[col for col in dff.columns if col not in ['Indicator', 'Indicator Value']],
        columns='Indicator',
        values='Indicator Value',
        aggfunc='first'
    ).reset_index()
    
    # Remove columns where all values are empty strings
    pivoted_data = pivoted_data.loc[:, ~(pivoted_data.apply(lambda col: col.eq("").all(), axis=0))]
    
    column_defs = [
        {"headerName": col, "field": col, "width": 100}
        for col in pivoted_data.columns if col != 'No. Farmers/province'
    ] + [{"headerName": "No. Farmers/province", "field": "No. Farmers/province", "width": 100}]
    
    return html.Div([
        dag.AgGrid(
            id='ag-grid',
            defaultColDef={
                "filter": True,
                "minWidth": 60,  # Smaller minimum width for compact columns
                "resizable": True,  # Allow resizing columns
                "cellStyle": {"fontSize": "10px"},  # Reduce font size for compactness
                "flex": 1,
                "cellDataType": False,
                "cellDataType": "text"
            },
            className="ag-theme-alpine compact",
            columnSize="autoSize",
            columnDefs=column_defs,
            rowData=pivoted_data.to_dict('records'),
            style={'width': '100%', 'fontSize': '10px'},  # Ensure the grid width is 100% of the container
            dashGridOptions={
                "domLayout": "autoHeight",  # Automatically adjust grid height
                "suppressHorizontalScroll": True,  # Disable horizontal scrolling
            }
        ),
    ])

        
def create_graph(dff, filters):
    dff_filtered = dff[dff['Indicator'] == dff['Indicator'].unique()[0]]
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
            y=-0.23,
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

    if 'paddy rice price' in filters['Tag'].lower():
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
            dmc.Title(
                dff["Tag"].unique()[0],
                order=3,
                style={
                    "fontWeight": 600,
                    "textAlign": "center",
                    "marginBottom": "20px",
                    "textTransform": "uppercase",
                    # "letterSpacing": "1px",
                    "background": "linear-gradient(90deg, #ECF0F1, #FFFFFF)",
                    "padding": "10px",
                    "borderRadius": "8px",
                    "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
                }
            ),
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
    
    if 'occupations of school dropouts' in filters['Tag'].lower():
        dff = dff[dff['Indicator'] == 'Percent']
        series_name = dff['Series Name'].unique()[0]
        indicator = dff['Indicator'].unique()[0]
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
        year = dff['Year'].unique()[0]
        
        # Filter the data for the latest year
        
        latest_data = dff
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
                # title="Occupation",
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
                y=-0.30,  # Slightly below the legend
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
            dmc.Title(
                f"Occupations of School Dropouts",
                order=3,
                style={
                    "fontWeight": 600,
                    "textAlign": "center",
                    "marginBottom": "20px",
                    "textTransform": "uppercase",
                    # "letterSpacing": "1px",
                    "background": "linear-gradient(90deg, #ECF0F1, #FFFFFF)",
                    "padding": "10px",
                    "borderRadius": "8px",
                    "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
                }
            ),
                
            # dmc.Select(
            #     label="Select Year:", 
            #     withAsterisk=True,
            #     id="year-dropdown-data-explorer", 
            #     value="2023",
            #     data=[{'label': str(option), 'value': str(option)} for option in ["2023", "2022", "2021"]],
            #     withScrollArea=False,
            #     styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},   
            #     checkIconPosition="right",
            #     allowDeselect=False,
            #     w=200,
            # ),
            html.Div([figure_component]),
            dmc.Alert(
                """The figures illustrate economic activities after dropping out of school, based on data from the Cambodia Socio-Economic Survey. Due to data limitations, individuals aged 6–19 are assumed to be recent dropouts, while those aged 20–40 are considered to have dropped out earlier and been out of school for a longer period.

The figures show that recent dropouts are primarily engaged in low-skilled jobs, such as elementary occupations, with higher-ranking jobs accounting for less than 5%. Similarly, when comparing recent dropouts with older dropouts, it is evident that older dropouts also remain in low-skilled jobs. However, there is a slight increase in employment in higher-ranking positions—such as clerks, professionals, technicians and associate professionals, legislators, senior officials, and managers—though this remains below 10%.

In other words, despite having worked for up to 20 years, older dropouts are still predominantly in low-skilled jobs, underscoring the crucial role of education in improving employment opportunities. Further, it is important to note that we cannot guarantee that students aged 16–19 who are currently classified as dropouts did so recently; they may have dropped out earlier.""",
                title="Description",
                color="green"
            )
        ])
    
    if any(word in filters['Tag'].lower() for word in ['student flow rates', 'successful student']):
        if any(word in filters['Tag'].lower() for word in ['grade', 'level', 'successful student']):
            traces = []
            for idx, grade in enumerate(dff['Grade'].unique()):
                grade_data = dff[dff['Grade'] == grade]
                line_color = ["#156082", "#A80000", "#8EA4BC", "#FF5733", "#F4A261", "#E9C46A", "#2A9D8F", "#E76F51", "#457B9D", "#D4A373", "#6A0572", "#264653"]
                
                if 'level' in filters['Tag'].lower():
                    traces.append(go.Scatter(
                        x=grade_data['Year'],
                        y=grade_data['Indicator Value'],
                        mode='lines+markers' if len(grade_data) == 1 else 'lines',
                        name=f"{grade}",
                        line=dict(color=line_color[idx])
                    ))
                elif 'grade' in filters['Tag'].lower():
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
            xaxis=dict(
                tickmode='auto',
                color='rgba(0, 0, 0, 0.6)',
                tickvals=dff['Year'].unique(),
            ),
            margin=dict(t=100, b=80, l=50, r=50, pad=10),
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
        )

        fig = go.Figure(layout=layout)
        for trace in traces:
            fig.add_trace(trace)
            
        if 'successful student' in filters['Tag'].lower():
            fig.update_layout(
                title=dict(
                    text=f"{indicator} in {dff['Province'].unique()[0]}"
                        + f"<br><span style='display:block; margin-top:8px; font-size:70%; color:rgba(0, 0, 0, 0.6);'>{dff['Indicator Unit'].unique()[0]}</span>"
                ),
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
            # dmc.Alert(
            #     "The figure illustrates the student dropout rates from 2012 to 2023 across different grade levels: primary school, lower-secondary school, and upper-secondary school in Cambodia. It shows that the overall student dropout rates declined dramatically, a trend that can be attributed to the government’s efforts to improve the education system in Cambodia. Notably, during the 2019-2020 academic year, the overall dropout rate for upper-secondary school reached an unusually low level, primarily due to Grade 12 data. This was followed by a decline in class repetition compared to other years. In other words, most students that year were promoted to the next grade. This was primarily due to the COVID-19 pandemic, during which schools were closed, and the Ministry of Education, Youth, and Sport (MoEYS) announced the automatic promotion of all students. As a result, the dropout rate for that year was exceptionally low."
            #     if series_name == "Student Flow Rates" and indicator == "Dropout" 
            #     else "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            #     title="Description",
            #     color="green"
            # )
        ]) 
    
    # Create traces (unchanged)
    traces = []
    if dff['Grade'].notna().all():
        for grade in dff['Grade'].unique():
            grade_data = dff[dff['Series Name'] == grade]
            traces.append(go.Scatter(
                x=grade_data['Year'],
                y=grade_data['Indicator Value'],
                mode='lines+markers' if len(grade_data) == 1 else 'lines',
                name=f"{grade}",
                line=dict(color="#156082")
            ))
    else:
        trace = go.Scatter(
            x=dff_filtered['Year'],
            y=dff_filtered['Indicator Value'],
            mode='lines+markers' if len(dff_filtered) == 1 else 'lines',
            name=f"{indicator} (Line)",
            line=dict(color="#156082")
        )
        traces.append(trace)

    # Create frames for animation (unchanged)
    frames = []
    years = sorted(dff_filtered['Year'].unique())
    for i in range(len(years)):
        frame_data = []
        for trace in traces:
            frame_trace = go.Scatter(
                x=trace.x[:i+1],
                y=trace.y[:i+1],
                mode=trace.mode,
                name=trace.name,
                line=dict(color="#156082")
            )
            frame_data.append(frame_trace)
        frames.append(go.Frame(data=frame_data, name=str(years[i])))

    # Create figure with animation settings
    fig_line = go.Figure(
        data=traces,
        layout=layout,
        frames=frames
    )

    # Add play/pause buttons and slider with synchronized movement
    fig_line.update_layout(
        title=dict(
            text=f"{series_name} {dff['Indicator'].unique()[0]}"
                + (f" in {dff['Province'].unique()[0]}" if 'Province' in dff.columns and dff['Province'].nunique() == 1 else "")
                + (f" to {dff['Markets'].unique()[0]}" if 'Markets' in dff.columns and dff['Markets'].nunique() == 1 else "")
                + f"<br><span style='display:block; margin-top:8px; font-size:70%; color:rgba(0, 0, 0, 0.6);'>{dff['Indicator Unit'].unique()[0]}</span>"
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(
                        args=[None, {
                            "frame": {"duration": 500, "redraw": True},
                            "fromcurrent": True,
                            "transition": {"duration": 200, "easing": "linear"}
                        }],
                        label="Play",
                        method="animate"
                    ),
                    dict(
                        args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}],
                        label="Pause",
                        method="animate"
                    )
                ],
                pad={"r": 10, "t": 65},
                showactive=True,
                x=0.0,
                xanchor="left",
                y=0,
                yanchor="top"
            ),
        ],
        sliders=[{
            "active": 0,
            "yanchor": "top",
            "xanchor": "left",
            "transition": {"duration": 300, "easing": "cubic-in-out"},
            "pad": {"b": 10, "t": 50},
            "len": 0.8,
            "x": 0.15,
            "y": 0,
            "steps": [{
                "args": [[str(year)], {
                    "frame": {"duration": 300, "redraw": True},
                    "mode": "immediate",
                    "transition": {"duration": 300}
                }],
                "label": "",
                "method": "animate"
            } for year in years],
            # Add these to synchronize slider with animation
            "activebgcolor": "#ADD8E6",
            "tickcolor": "gray",
            "minorticklen": 6
        }]
    )
    
    if series_name == "Rice Production":
        fig_line.update_layout(
            title=dict(
                text=f"{dff['Sub-Sector (2)'].unique()[0]} {dff['Indicator'].unique()[0]}"
                    + (f" in {dff['Province'].unique()[0]}" if 'Province' in dff.columns and dff['Province'].nunique() == 1 else "")
                    + (f" to {dff['Markets'].unique()[0]}" if 'Markets' in dff.columns and dff['Markets'].nunique() == 1 else "")
                    + f"<br><span style='display:block; margin-top:8px; font-size:70%; color:rgba(0, 0, 0, 0.6);'>{dff['Indicator Unit'].unique()[0]}</span>"
            )
        )

    # Return graph components (unchanged)
    return html.Div([ 
        dcc.Graph(
            id="figure-linechart", 
            style={'minHeight': '460px'},
            figure=fig_line, 
            config={
                'displaylogo': False,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'cdri_datahub_linechart',
                    'height': 500,
                    'width': 800,
                    'scale': 6
                },
            },
            responsive=True
        ),
        dmc.Divider(size="sm"),
    ])


def create_map(dff, year, indicator=None):
    series_name = dff['Series Name'].unique()[0]
    if indicator is None:
        indicator = sorted(dff['Indicator'].unique())[0]
    
    # Filter data by both year and indicator
    if indicator is not None:
        dff = dff[(dff["Year"] == year) & (dff["Indicator"] == indicator)]
    else:
        dff = dff[dff["Year"] == year]
        
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
                            id="geojson-data-explorer")
        
        # print(data[data["Indicator"] == "No. Farmers/province"]["Indicator Value"])

        return html.Div(
            [
                dmc.Title(
                    "Cashew Nut Crop Profile",
                    order=3,
                    style={
                        "fontWeight": 600,
                        "textAlign": "center",
                        "marginBottom": "20px",
                        "textTransform": "uppercase",
                        # "letterSpacing": "1px",
                        "background": "linear-gradient(90deg, #ECF0F1, #FFFFFF)",
                        "padding": "10px",
                        "borderRadius": "8px",
                        "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
                    }
                ),
                
                dl.Map(
                    style={'width': '100%', 'height': '450px', 'zIndex': 0},
                    center=[12.5657, 104.9910],
                    zoom=7,
                    children=[
                        dl.TileLayer(url="http://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png"),
                        geojson,
                        colorbar,
                        html.Div(children=get_info(series_name=series_name, indicator=indicator, indicator_unit=indicator_unit, year=year), id="info-data-explorer", className="info", style={"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000"}),
                    ],
                    attributionControl=False,
                ),  
                dmc.Stack(
                    children= [
                        dmc.Select(
                            label="Select Year:", 
                            withAsterisk=True,
                            id="year-dropdown", 
                            value="2023",
                            data=[{'label': str(option), 'value': str(option)} for option in ["2023", "2022", "2021"]],
                            withScrollArea=False,
                            styles={"marginBottom": "16px", "dropdown": {"maxHeight": 200, "overflowY": "auto"}},   
                            checkIconPosition="right",
                            allowDeselect=False,
                        ),
                        dmc.RadioGroup(
                            id="indicator-radio-group",
                            withAsterisk=True,
                            value=indicator,
                            label="Select Variable:",
                            size="sm",
                            children=[
                                dmc.Radio(label=option, value=option) 
                                for option in sorted(
                                    data[data["Tag"] == "Cashew Nut Crop Profile"]["Indicator"].dropna().str.strip().unique(),
                                )
                            ],
                            # mt=10,
                            mb=10,
                        ),
                    ],
                    className="info",
                    style={
                        "position": "absolute",  # Position it absolutely within the map container
                        "bottom": "10px",
                        "left": "10px",  # Adjust the position as needed
                        "zIndex": 1000,
                        "display": "flex",
                        "flex-wrap": "wrap",
                        "gap": "10px"
                    }
                )
                
                
            ],
            style={
                'position': 'relative',
                'zIndex': 0,
            }
        )
   
        
# Callback to update data table based on the selected suggestion
@callback(
    [Output("data-explorer-map-id", "children"),
    Output("data-explorer-dataview-id", "children"),
    Output("data-explorer-graph-id", "children"),
    Output("data-explorer-filter-state", "data")],
    Input("suggestions-autocomplete", "value")
)
def update_data(selected_suggestion):
    if not selected_suggestion:
        # Default content when no question is entered
        default_message = dmc.Alert(
            "Please enter a question in the search bar above to explore data visualizations and tables.",
            title="Welcome to the CDRI Data Hub Explorer!",
            color="blue",
            variant="light",
            style={'margin': '20px'}
        )
        return default_message, None, None, {}

    # Extract filters from the selected suggestion
    filters = {}
    for col in ["Tag"]:
        lower_mapping = {str(name).lower(): name for name in data[col].unique() if pd.notna(name)}
        match = process.extractOne(selected_suggestion.lower(), lower_mapping.keys(), score_cutoff=50)
        if match:
            best_match_lower, score = match
            filters[col] = lower_mapping[best_match_lower]
        
    # Filter the dataset
    filtered_df = data
    for key, value in filters.items():
        if key in filtered_df.columns:
            # Apply the filter temporarily
            temp_df = filtered_df[filtered_df[key] == value]
            
            if not temp_df.empty:
                # If the filtered data is not empty, apply the filter
                filtered_df = temp_df
    
    
    if not filters or 'Tag' not in filters:
        # Default content when no question is entered
        default_message = dmc.Alert(
            "Please enter a question in the search bar above to explore data visualizations and tables.",
            title="Dataset Not Found!",
            color="blue",
            variant="light",
            style={'margin': '20px'}
        )
        return default_message, None, None, {}

    if selected_suggestion == "Cashew Nut Crop Profile":
        return create_map(filtered_df, "2023", None), create_dataview(filtered_df, "2023"), None, filtered_df.to_dict('records')

    return None, None, create_graph(filtered_df, filters), filtered_df.to_dict('records')

@callback(
    Output("data-explorer-map-id", "children", allow_duplicate=True),
    Input("indicator-radio-group", "value"),
    Input("data-explorer-filter-state", "data"),
    prevent_initial_call=True
)
def update_map(indicator, filtered_df):
    if indicator is None:
        return dash.no_update
    
    # Convert stored data to DataFrame and filter by selected indicator
    filtered_df = pd.DataFrame(filtered_df)
    
    # Generate the map with the filtered data
    return create_map(filtered_df, "2023", indicator)

# Calllback for info on map
@callback(Output("info-data-explorer", "children"), Input("data-explorer-filter-state", "data"), Input("indicator-radio-group", "value"), Input("geojson-data-explorer", "hoverData"))
def info_hover(filtered_df, indicator, feature):
    filtered_df = pd.DataFrame(filtered_df)
    series_name = filtered_df["Series Name"].unique()[0]
    indicator_unit = filtered_df[filtered_df["Indicator"] == indicator]["Indicator Unit"].unique()[0]
    year = filtered_df["Year"].unique()[0]

    return get_info(series_name=series_name, indicator=indicator, feature=feature, indicator_unit=[indicator_unit], year=year)