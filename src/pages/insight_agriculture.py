import dash_mantine_components as dmc
from dash import html

insight_agriculture = dmc.Container(
    [
        html.H1("Hello", className="display-3 text-danger text-center"),
        html.P(
            "Insight Agriculture",
            className="lead text-muted text-center",
        ),
    ],
    fluid=True,
    className="d-flex flex-column justify-content-center align-items-center bg-light pt-5",
)