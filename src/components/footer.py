from dash import dcc, html
import dash_mantine_components as dmc

def footer():
    return html.Div(
        style={
            "position": "relative",  # Set position to relative
            "bottom": "0",  # Pin the footer to the bottom of the page
            "width": "100%",  # Ensure the footer spans the full width of the page
            "backgroundColor": "#336666",
            "color": "white",
            "padding": "5px"
        },
        children=[
            dmc.Grid(
                align="center",
                justify="space-between",
                gutter="lg",
                children=[
                    dmc.GridCol(
                        dmc.Anchor(
                            href="/",
                            children=[
                                dmc.Image(
                                    src="https://cdri.org.kh/storage/images/CDRI%20Logo_1704186788.png",
                                    style={"width": "150px", "height": "auto"}
                                ),
                            ],
                        ),
                        span={"base": 12, "md": 4},
                    ),
                    dmc.GridCol(
                        dcc.Markdown(
                            """
                            **CDRI Data Hub** is a centralized repository for research-related data, offering reliable information across various sectors in Cambodia. It supports evidence-based decision-making by providing datasets, visualization tools, and resources tailored to researchers, policymakers, and practitioners.
                            """,
                            style={
                                "marginTop": "1rem",
                                "color": "white",  # Text color
                                "fontSize": "14px",  # Optional font size
                            },
                        ),
                        span={"base": 12, "md": 8},
                    ),
                ],
            ),
        ],
    )
