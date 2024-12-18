from dash import dcc, html

def banner():
    """Build the banner at the top of the page using HTML components."""
    return html.Div(
        id="banner",
        style={
            "display": "flex",
            "justify-content": "space-between",
            "align-items": "center",
            "padding": "0.5rem 1rem",
            "background-color": "#336666",
            "color": "white",
            "z-index": 1,
        },
        children=[
            # Logo Section
            html.A(
                href="/",
                children=html.Img(
                    src="https://cdri.org.kh/storage/images/CDRI%20Logo_1704186788.png",
                    style={"width": "150px", "height": "auto"},
                ),
            ),

            # Navigation Links
            html.Div(
                style={"display": "flex", "gap": "1rem"},
                children=[
                    html.A("Home", href="/", style={"color": "white", "text-decoration": "none"}),
                    html.Div(
                        children=[
                            html.A("Sector", href="#", style={"color": "white", "text-decoration": "none"}),
                            html.Div(
                                style={
                                    "position": "absolute",
                                    "background-color": "white",
                                    "color": "black",
                                    "box-shadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",
                                    "padding": "0.5rem",
                                    "border-radius": "4px",
                                    "display": "none",
                                },
                                children=[
                                    html.A("Agriculture and Rural Development", href="/agriculture-and-rural-development", style={"display": "block", "margin": "0.5rem 0"}),
                                    html.A("Development Economics and Trade", href="/development-economics-and-trade", style={"display": "block", "margin": "0.5rem 0"}),
                                    html.A("Educational Research and Innovation", href="/educational-research-and-innovation", style={"display": "block", "margin": "0.5rem 0"}),
                                    html.A("Natural Resource and Environment", href="/natural-resource-and-environment", style={"display": "block", "margin": "0.5rem 0"}),
                                    html.A("Governance and Inclusive Society", href="/governance-and-inclusive-society", style={"display": "block", "margin": "0.5rem 0"}),
                                ],
                            ),
                        ],
                    ),
                    html.A("About", href="/about", style={"color": "white", "text-decoration": "none"}),
                ],
            ),
        ],
    )
