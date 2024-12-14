import dash_bootstrap_components as dbc
from dash import html

natural_resource_and_environment = dbc.Container(
    [
        html.H1("natural_resource_and_environment", className="banner"),
        html.P(
            "The page you are looking for does not exist.",
            className="lead text-muted text-center",
        ),
    ],
    fluid=True,
    className="d-flex flex-column justify-content-center align-items-center bg-light pt-5",
)