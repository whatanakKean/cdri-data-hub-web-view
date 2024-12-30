import dash_mantine_components as dmc
from dash import html

not_found_page = dmc.Container(
    [
        html.H1("404: Page Not Found", className="display-3 text-danger text-center"),
        html.P(
            "The page you are looking for does not exist.",
            className="lead text-muted text-center",
        ),
    ],
    fluid=True,
    className="d-flex flex-column justify-content-center align-items-center bg-light pt-5",
)