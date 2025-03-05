import dash_mantine_components as dmc
from dash import dcc, html, Input, Output, clientside_callback, ClientsideFunction
from src.pages.data import tradeData


not_found_page = dmc.Container(
    [
        html.H1("404: Page Not Found", className="display-3 text-danger text-center"),
        html.P(
            "The page you are looking for does not exist.",
            className="lead text-muted text-center",
        ),
        html.Div(
            children=[
                dcc.Store(id='ApexchartsSampleData', data=tradeData),
                html.H1("Javascript Charts inside a Dash App"),
                dmc.Center(
                    dmc.Paper(
                        shadow="sm",
                        style={'height':'600px', 'width':'800px', 'marginTop':'100px'},
                        children=[
                            html.Div(id='apexAreaChart'),
                            dmc.Center(
                                children=[
                                    dmc.SegmentedControl(
                                        id="selectCountryChip",
                                        value="Canada",
                                        data=['Canada', 'USA', 'Australia'],
                                    )
                                ]
                            )
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
    Input("ApexchartsSampleData", "data"),
    Input("selectCountryChip", "value"),
)