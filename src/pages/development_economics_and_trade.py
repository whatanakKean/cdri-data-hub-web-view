import dash_bootstrap_components as dbc
from dash import html

development_economics_and_trade = dbc.Container(
    [
        html.H1("development_economics_and_trade", className="display-3 text-danger text-center"),
        html.P(
            "The page you are looking for does not exist.",
            className="lead text-muted text-center",
        ),
    ],
    fluid=True,
    className="d-flex flex-column justify-content-center align-items-center bg-light pt-5",
)