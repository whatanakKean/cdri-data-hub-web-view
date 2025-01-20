from dash import dcc, html
import dash_mantine_components as dmc

def footer():
    return html.Div(
        style={
            "position": "relative",
            "bottom": "0",
            "width": "100%",
            "backgroundColor": "#336666",
            "color": "white",
            "padding": "20px"
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
                        children=[
                            dmc.Title("Phone:", order=4, td="underline"),
                            dmc.Text("+855 23 881701"),
                            dmc.Text("+855 23 881916"),
                            dmc.Text("+855 23 883603"),
                            dmc.Space(h=10),
                            
                            dmc.Title("Email:", order=4, td="underline"),
                            dmc.Text("cdri@cdri.org.kh"),
                            dmc.Space(h=10),
                            
                            # dmc.Title("Address:", order=4, td="underline"),
                            # dmc.Text("#56 Street 315, Tuol Kork, Phnom Penh, Cambodia"),
                            # dmc.Text("PO Box 622"),
                            # dmc.Text("Postal Code: 120508"),
                        ],
                        span={"base": 12, "md": 4},
                    ),
                    dmc.GridCol(
                        children=[
                            dmc.Title("Sectors: ", order=4, td="underline"),
                            dmc.Box(
                                children=[
                                    dmc.Anchor(
                                        ">     Agriculture and Rural Development",
                                        href="/agriculture-and-rural-development",
                                        style={"color": "white", "display": "block"}
                                    ),
                                    dmc.Anchor(
                                        ">     Development Economics and Trade",
                                        href="/development-economics-and-trade",
                                        style={"color": "white", "display": "block"}
                                    ),
                                ]
                            )
                        ],
                        span={"base": 12, "md": 4},
                    )

                ],
            ),
            dmc.Divider(m=10),
            dmc.Text("Copyright © 2025 CDRI. All rights reserved.", ta="center"),
        ],
    )
