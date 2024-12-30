import dash_mantine_components as dmc
from dash import html, dcc


# Define the home page layout
home_page = dmc.Container(
    [
        html.H1("Home Page"),
        html.P("Welcome to the CDRI Data Hub Home Page!"),
    ],
    fluid=True,
    className="mt-4",
)