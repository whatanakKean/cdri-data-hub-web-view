import dash_bootstrap_components as dbc
from dash import html

governance_and_inclusive_society = dbc.Container(
    [
        html.H1("Governance", className="display-3 text-danger text-center"),
        html.P(
            "The page you are looking for does not exist.",
            className="lead text-muted text-center",
        ),
    ],
    fluid=True,
    className="d-flex flex-column justify-content-center align-items-center bg-light pt-5",
)