import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback


def banner():
    """Build the banner at the top of the page with sector buttons inside."""
    return html.Div(
        id="banner",
        style={
            "padding": "0.5rem",
            "background-color": "#336666",
            "color": "white",
            "z-index": 1,
        },
        children=[
            dbc.Navbar(
                children=[
                    # Logo Section
                    dbc.Row(
                        align="center",
                        children=[
                            dbc.Col(
                                html.A(
                                    href="/",
                                    children=html.Img(
                                        src="https://cdri.org.kh/storage/images/CDRI%20Logo_1704186788.png",
                                        style={"width": "150px", "height": "auto"},
                                    ),
                                ),
                                width="auto",
                            ),
                        ],
                        className="g-0",
                    ),

                    # Responsive Toggle Menu
                    dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),

                    dbc.Collapse(
                        id="navbar-collapse",
                        is_open=False,
                        navbar=True,
                        children=dbc.Nav(
                            className="ms-auto",
                            navbar=True,
                            children=[
                                dbc.NavItem(dbc.NavLink("Home", href="/")),
                                dbc.DropdownMenu(
                                    children=[
                                        dbc.DropdownMenuItem("Sector", header=True),
                                        dbc.DropdownMenuItem("Agriculture and Rural Development", href="/agriculture-and-rural-development"),
                                        dbc.DropdownMenuItem("Development Economics and Trade", href="/development-economics-and-trade"),
                                        dbc.DropdownMenuItem("Educational Research and Innovation", href="/educational-research-and-innovation"),
                                        dbc.DropdownMenuItem("Natural Resource and Environment", href="/natural-resource-and-environment"),
                                        dbc.DropdownMenuItem("Governance and Inclusive Society", href="/governance-and-inclusive-society"),
                                    ],
                                    nav=True,
                                    in_navbar=True,
                                    label="Sector",
                                ),
                                dbc.NavItem(dbc.NavLink("About", href="/about")),
                            ],
                        ),
                    ),
                ],
                color="#336666",
                dark=True,
                sticky="top",
            ),
        ],
    )

# Callback to handle toggle button functionality
@callback(
    Output("navbar-collapse", "is_open"),
    Input("navbar-toggler", "n_clicks"),
    [Input("navbar-collapse", "is_open")],
)
def toggle_navbar(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open
