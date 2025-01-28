import dash_mantine_components as dmc
from dash import Input, Output, State, callback, html
import sqlite3
import pandas as pd

conn = sqlite3.connect("./src/data/data.db")
data = pd.read_sql_query(f"SELECT * FROM agriculture_data;", conn)

agriculture_menu_items = [
    dmc.MenuItem(name, href=f"/{name.lower().replace(' ', '-')}")
    for name in data['Series Name'].unique()
]

logo = "https://cdri.org.kh/storage/images/CDRI%20Logo_1704186788.png"
buttons = [
    dmc.Anchor(dmc.Button("Home", variant="subtle", color="white"), href="/"),
    dmc.Menu(
        [
            dmc.MenuTarget(dmc.Button("Sector", variant="subtle", color="white")),
            dmc.MenuDropdown(
                [
                    dmc.MenuItem(
                        "Agriculture and Rural Development",
                        href="/agriculture-and-rural-development"
                    ),
                    dmc.MenuItem(
                        "Development Economics and Trade",
                        href="/development-economics-and-trade"
                    )
                ]
            ),
        ],
        trigger="hover",
    ),
    dmc.Anchor(dmc.Button("Data Explorer", variant="subtle", color="white"), href="/data-explorer"),
    dmc.Anchor(dmc.Button("About", variant="subtle", color="white"), href="https://cdri.org.kh/page/about-cdri")
]

def banner():
    return [
        dmc.AppShellHeader(
                dmc.Group(
                    [
                        dmc.Group(
                            [
                                dmc.Anchor(dmc.Image(
                                    src="https://cdri.org.kh/storage/images/CDRI%20Logo_1704186788.png",
                                    style={"width": "150px", "height": "auto"}
                                ), href="/")
                            ],
                        ),
                        dmc.Group(
                            children=buttons,
                            ml="xl",
                            gap=0,
                            visibleFrom="sm",
                        ),
                        dmc.Burger(
                            id="burger",
                            size="sm",
                            hiddenFrom="sm",
                            opened=False,
                            color="white"
                        ),
                    ],
                    justify="space-between",
                    style={"flex": 1},
                    h="100%",
                    px="md",
                ),
                style={"backgroundColor": "#336666"}
            ),
            dmc.AppShellNavbar(
                id="navbar",
                children=buttons,
                py="md",
                px=4,
                style={"backgroundColor": "#336666"}
            ),
            dmc.Drawer(
                title="Insight",
                opened=False,  # Drawer is initially closed
                size="lg",
                position="right",  # You can choose "left", "right", "top", "bottom"
                children=buttons
            )
        ]


# Callback to toggle navbar visibility
@callback(
    Output("appshell", "navbar"),
    Input("burger", "opened"),
    State("appshell", "navbar"),
)
def toggle_navbar(opened, navbar):
    navbar["collapsed"] = {"mobile": not opened, "desktop": True}
    return navbar

@callback(
    Output("burger", "opened"),
    Input('url', 'href')
)
def close_menu_on_navigation(href):
    return False


@callback(
    Output("drawer", "opened"),
    Input("insight-button", "n_clicks"),
    prevent_initial_call=True
)
def toggle_drawer(n_clicks):
    if n_clicks:
        return True  # Open the drawer
    return False  # Close the drawer