import dash_bootstrap_components as dbc
from dash import html, dcc


# Define the home page layout
home_page = dbc.Container(
    [
        html.H1("Home Page"),
        html.P("Welcome to the CDRI Data Hub Home Page!"),
    ],
    fluid=True,
    className="mt-4",
)