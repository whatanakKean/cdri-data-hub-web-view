import dash_mantine_components as dmc
from dash import Input, Output, State, callback

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
                    # dmc.MenuItem(
                    #     "Educational Research and Innovation",
                    #     href="/educational-research-and-innovation"
                    # ),
                    # dmc.MenuItem(
                    #     "Natural Resource and Environment",
                    #     href="/natural-resource-and-environment"
                    # ),
                    # dmc.MenuItem(
                    #     "Governance and Inclusive Society",
                    #     href="/governance-and-inclusive-society"
                    # ),
                ]
            ),
        ],
    ),
    dmc.Anchor(dmc.Button("About", variant="subtle", color="white"), href="https://cdri.org.kh/page/about-cdri")
]

def banner():
    return [
        dmc.AppShellHeader(
                dmc.Group(
                    [
                        dmc.Group(
                            [
                                dmc.Anchor(dmc.Image(src=logo, h=40), href="/")
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
