import sqlite3
import dash_mantine_components as dmc
from dash import dcc, html, Input, Output, clientside_callback, ClientsideFunction
import pandas as pd
from src.data.testing_data import tradeData


# Sample dataset
conn = sqlite3.connect("./src/data/data.db")
query1 = """SELECT * FROM agriculture_data WHERE "Series Name" = 'Rice Production';"""
agriculture_data = pd.read_sql_query(query1, conn).to_dict(orient="records")


not_found_page = dmc.Container(
    [
        html.H1("Testing Visualization", className="display-3 text-danger text-center"),
        html.Div(
            children=[
                dcc.Store(id='ApexchartsSampleData', data=agriculture_data),
                dmc.Center(
                    dmc.Paper(
                        shadow="sm",
                        style={'height':'600px', 'width':'800px'},
                        children=[
                            html.Div(id='apexAreaChart')
                        ]
                    )
                )
            ]
        )
    ],
    fluid=True,
    className="d-flex flex-column justify-content-center align-items-center bg-light pt-5",
)

clientside_callback(
    ClientsideFunction(
        namespace='apexCharts',
        function_name='areaChart'
    ),
    Output("apexAreaChart", "children"),
    Input("ApexchartsSampleData", "data")
)