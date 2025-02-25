
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
import random
# Sample dataset
conn = sqlite3.connect("./src/data/data.db")

# Query economic_data table
query1 = "SELECT * FROM education_data;"
df1 = pd.read_sql_query(query1, conn)
query2 = "SELECT * FROM agriculture_data;"
df2 = pd.read_sql_query(query2, conn)
data = pd.concat([df1, df2], ignore_index=True)

combined_options = [
    {"label": f"{item}", "value": f"{item}"}
    for item in random.sample(list(data["Tag"].unique()), len(data["Tag"].unique()))
]

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
                        dmc.Title('Data Hub Explorer', order=1, style={'color': 'white', 'fontSize': '2rem'}),
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
                    ],
                    className="animate__animated animate__fadeInUp animate__fast"
                )
            ],
        ),
        
        dmc.Container(children=[
            dmc.Paper([
                dmc.Tabs(
                    children=[
                        dmc.TabsList(
                            [
                                dmc.TabsTab("Visualization", leftSection=DashIconify(icon="tabler:chart-bar"), value="graph"),
                                dmc.TabsTab("Data View", leftSection=DashIconify(icon="tabler:database"), value="dataview"),
                            ], 
                            grow="True",
                        ),
                        dmc.TabsPanel(                               
                            children=[
                                html.Div(id='data-explorer-graph-id'),
                            ], 
                            value="graph"
                        ),
                        dmc.TabsPanel(html.Div(id='data-explorer-dataview-id'), value="dataview"),
                    ], 
                    value="graph", color="#336666"
                ),
                ], shadow="xs", p="md", radius="md", withBorder=True),
        ], fluid=True),
        dcc.Store(id='data-explorer-filter-state'),
    ],
)

def create_dataview(dff):
    dff = dff.dropna(axis=1, how='all')
    pivoted_data = dff.pivot_table(
        index=[col for col in dff.columns if col not in ['Indicator', 'Indicator Value']],
        columns='Indicator',
        values='Indicator Value',
        aggfunc='first'
    ).reset_index()
    
    return html.Div([
        dag.AgGrid(id='data-explorer-ag-grid', defaultColDef={"filter": True}, columnDefs=[{"headerName": col, "field": col} for col in pivoted_data.columns], rowData=pivoted_data.to_dict('records'), style={'height': '400px'}),
        dmc.Button("Download Data", id="data-explorer-download-button", variant="outline", color="#336666", mt="md", style={'marginLeft': 'auto', 'display': 'flex', 'justifyContent': 'flex-end'}),
        dcc.Download(id="data-explorer-download-data")
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
            y=-0.25,
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

    if 'rice price' in filters['Tag'].lower():
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
                gutter="xs",
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
            
        print(filters['Tag'])

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
                y=-0.25,
                xanchor="center",
                x=0.5,
                font=dict(
                    color='rgba(0, 0, 0, 0.6)'
                )
            ),
            annotations=[dict(
                x=0.5,  # Center horizontally (matches legend's x)
                y=-0.35,  # Slightly below the legend
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
                style={'minHeight': '450px'},
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
                y=-0.25,
                xanchor="center",
                x=0.5
            ),
            xaxis=dict(
                tickmode='auto',
                color='rgba(0, 0, 0, 0.6)',
                tickvals=dff['Year'].unique(),
            ),
            margin=dict(t=100, b=80, l=50, r=50, pad=10),
        )

        fig = go.Figure(layout=layout)
        for trace in traces:
            fig.add_trace(trace)
            
        if 'successful student' in filters['Tag'].lower():
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
                "The figure illustrates the student dropout rates from 2012 to 2023 across different grade levels: primary school, lower-secondary school, and upper-secondary school in Cambodia. It shows that the overall student dropout rates declined dramatically, a trend that can be attributed to the government’s efforts to improve the education system in Cambodia. Notably, during the 2019-2020 academic year, the overall dropout rate for upper-secondary school reached an unusually low level, primarily due to Grade 12 data. This was followed by a decline in class repetition compared to other years. In other words, most students that year were promoted to the next grade. This was primarily due to the COVID-19 pandemic, during which schools were closed, and the Ministry of Education, Youth, and Sport (MoEYS) announced the automatic promotion of all students. As a result, the dropout rate for that year was exceptionally low."
                if series_name == "Student Flow Rates" and indicator == "Dropout" 
                else "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                title="Description",
                color="green"
            )
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

    # Return graph components (unchanged)
    return html.Div([ 
        dcc.Graph(
            id="figure-linechart", 
            style={'minHeight': '450px'},
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


# Callback to update data table based on the selected suggestion
@callback(
    [Output("data-explorer-dataview-id", "children"),
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
        return default_message, default_message, {}

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
        return default_message, default_message, {}
    
    # return create_dataview(filtered_df), create_graph(filtered_df), filtered_df.to_dict('records')
    return create_dataview(filtered_df), create_graph(filtered_df, filters), filtered_df.to_dict('records')

@callback(Output("data-explorer-download-data", "data"), Input("data-explorer-download-button", "n_clicks"), State('data-explorer-filter-state', 'data'))
def download_data(n_clicks, filtered_df):
    if n_clicks is None: return dash.no_update
    filtered_df = pd.DataFrame(filtered_df)
    return dict(content=filtered_df.to_csv(index=False), filename="data.csv", type="application/csv")