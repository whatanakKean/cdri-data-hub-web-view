import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback


def banner():
    """Build the banner at the top of the page with sector buttons inside."""
    return html.Div(
        id="banner",
        style={
            "padding": "1rem",
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
                                dbc.NavItem(dbc.NavLink("About", href="/about")),
                                dbc.NavItem(dbc.NavLink("Contact", href="/contact")),
                                dbc.DropdownMenu(
                                    children=[
                                        dbc.DropdownMenuItem("More", header=True),
                                        dbc.DropdownMenuItem("Documentation", href="/documentation"),
                                        dbc.DropdownMenuItem("FAQ", href="/faq"),
                                    ],
                                    nav=True,
                                    in_navbar=True,
                                    label="More",
                                ),
                            ],
                        ),
                    ),
                ],
                color="#336666",
                dark=True,
                sticky="top",
            ),

            # Sector Buttons Section Inside the Banner
            html.Div(
                id="tabs-container",
                children=[
                    dcc.Tabs(
                        id="tabs",
                        parent_className="custom-tabs",
                        value="agriculture-and-rural-development",  # Initial tab value
                        children=[
                            dcc.Tab(
                                label="Agriculture and Rural Development",
                                value="agriculture-and-rural-development",
                                className="custom-tab",
                                selected_className="custom-tab--selected",
                                style={
                                    'color': '#586069',
                                    'borderColor': 'lightgrey',
                                    'borderTopLeftRadius': '3px',
                                    'borderTopRightRadius': '3px',
                                    'borderTop': '3px solid transparent',
                                    'borderLeft': '1px solid lightgrey',
                                    'borderRight': '1px solid lightgrey',
                                    'backgroundColor': '#fafbfc',
                                    'padding': '12px',
                                    'fontFamily': '"system-ui"',
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'justifyContent': 'center'
                                },
                                selected_style={
                                    'color': 'black',
                                    'boxShadow': '1px 1px 0 white',
                                    'borderLeft': '1px solid lightgrey',
                                    'borderRight': '1px solid lightgrey',
                                    'borderTop': '6px solid #abd2ff'
                                }
                            ),
                            dcc.Tab(
                                label="Development Economics and Trade",
                                value="development-economics-and-trade",
                                className="custom-tab",
                                selected_className="custom-tab--selected",
                                style={
                                    'color': '#586069',
                                    'borderColor': 'lightgrey',
                                    'borderTopLeftRadius': '3px',
                                    'borderTopRightRadius': '3px',
                                    'borderTop': '3px solid transparent',
                                    'borderLeft': '1px solid lightgrey',
                                    'borderRight': '1px solid lightgrey',
                                    'backgroundColor': '#fafbfc',
                                    'padding': '12px',
                                    'fontFamily': '"system-ui"',
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'justifyContent': 'center'
                                },
                                selected_style={
                                    'color': 'black',
                                    'boxShadow': '1px 1px 0 white',
                                    'borderLeft': '1px solid lightgrey',
                                    'borderRight': '1px solid lightgrey',
                                    'borderTop': '6px solid #abd2ff'
                                }
                            ),
                            dcc.Tab(
                                label="Educational Research and Innovation",
                                value="educational-research-and-innovation",
                                className="custom-tab",
                                selected_className="custom-tab--selected",
                                style={
                                    'color': '#586069',
                                    'borderColor': 'lightgrey',
                                    'borderTopLeftRadius': '3px',
                                    'borderTopRightRadius': '3px',
                                    'borderTop': '3px solid transparent',
                                    'borderLeft': '1px solid lightgrey',
                                    'borderRight': '1px solid lightgrey',
                                    'backgroundColor': '#fafbfc',
                                    'padding': '12px',
                                    'fontFamily': '"system-ui"',
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'justifyContent': 'center'
                                },
                                selected_style={
                                    'color': 'black',
                                    'boxShadow': '1px 1px 0 white',
                                    'borderLeft': '1px solid lightgrey',
                                    'borderRight': '1px solid lightgrey',
                                    'borderTop': '6px solid #abd2ff'
                                }
                            ),
                            dcc.Tab(
                                label="Natural Resource and Environment",
                                value="natural-resource-and-environment",
                                className="custom-tab",
                                selected_className="custom-tab--selected",
                                style={
                                    'color': '#586069',
                                    'borderColor': 'lightgrey',
                                    'borderTopLeftRadius': '3px',
                                    'borderTopRightRadius': '3px',
                                    'borderTop': '3px solid transparent',
                                    'borderLeft': '1px solid lightgrey',
                                    'borderRight': '1px solid lightgrey',
                                    'backgroundColor': '#fafbfc',
                                    'padding': '12px',
                                    'fontFamily': '"system-ui"',
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'justifyContent': 'center'
                                },
                                selected_style={
                                    'color': 'black',
                                    'boxShadow': '1px 1px 0 white',
                                    'borderLeft': '1px solid lightgrey',
                                    'borderRight': '1px solid lightgrey',
                                    'borderTop': '6px solid #abd2ff'
                                }
                            ),
                            dcc.Tab(
                                label="Governance and Inclusive Society",
                                value="governance-and-inclusive-society",
                                className="custom-tab",
                                selected_className="custom-tab--selected",
                                style={
                                    'color': '#586069',
                                    'borderColor': 'lightgrey',
                                    'borderTopLeftRadius': '3px',
                                    'borderTopRightRadius': '3px',
                                    'borderTop': '3px solid transparent',
                                    'borderLeft': '1px solid lightgrey',
                                    'borderRight': '1px solid lightgrey',
                                    'backgroundColor': '#fafbfc',
                                    'padding': '12px',
                                    'fontFamily': '"system-ui"',
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'justifyContent': 'center'
                                },
                                selected_style={
                                    'color': 'black',
                                    'boxShadow': '1px 1px 0 white',
                                    'borderLeft': '1px solid lightgrey',
                                    'borderRight': '1px solid lightgrey',
                                    'borderTop': '6px solid #abd2ff'
                                }
                            ),
                        ],
                    ),
                ],
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

# # Callback to render content for the selected tab
# @callback(
#     Output("tab-content", "children"),
#     Input("tabs", "value"),
# )
# def render_content(selected_tab):
#     if selected_tab == "agriculture-and-rural-development":
#         return html.Div("Content for Agriculture and Rural Development")
#     elif selected_tab == "development-economics-and-trade":
#         return html.Div("Content for Development Economics and Trade")
#     elif selected_tab == "educational-research-and-innovation":
#         return html.Div("Content for Educational Research and Innovation")
#     elif selected_tab == "natural-resource-and-environment":
#         return html.Div("Content for Natural Resource and Environment")
#     elif selected_tab == "governance-and-inclusive-society":
#         return html.Div("Content for Governance and Inclusive Society")
#     return html.Div("Select a tab to see the content")
