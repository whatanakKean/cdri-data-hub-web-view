import dash_bootstrap_components as dbc
from dash import dcc, html

def footer():
    return dbc.Row(
        align="center",
        justify="between",
        id="footer-container",
        children=[
            dbc.Col(
                children=[
                    dbc.Col(
                        html.A(
                            href="/",
                            children=[
                                html.Img(
                                    src="https://cdri.org.kh/storage/images/CDRI%20Logo_1704186788.png",
                                    style={"width": "150px", "height": "auto"}  # Adjust the width as needed
                                ),
                            ],
                        ),
                        width="auto",
                    ),
                ],
                width=12,
                md=4,
                style={"padding": "15px"},
            ),
            dbc.Col(
                children=[
                    dbc.Row(
                        [
                            dcc.Markdown(
                                """
                                **CDRI Data Hub** is a centralized repository for research-related data, offering reliable information across various sectors in Cambodia. It supports evidence-based decision-making by providing datasets, visualization tools, and resources tailored to researchers, policymakers, and practitioners.
                                """
                            ),
                        ],
                        style={"marginTop": "1rem"},
                    ),
                ],
                width=12,
                md=8,
            ),
        ],
        style={"margin": "0", "background-color": "#336666", "color": "white", "position": "relative"},
    )