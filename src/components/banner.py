import dash_mantine_components as dmc
from dash import Input, Output, State, callback

logo = "https://cdri.org.kh/storage/images/CDRI%20Logo_1704186788.png"
buttons = [
    dmc.Button("Home", variant="subtle", color="gray"),
    dmc.Button("Blog", variant="subtle", color="gray"),
    dmc.Button("Contacts", variant="subtle", color="gray"),
    dmc.Button("Support", variant="subtle", color="gray"),
]

def banner():
    return dmc.AppShell(
        [
            dmc.AppShellHeader(
                dmc.Group(
                    [
                        dmc.Group(
                            [
                                dmc.Image(src=logo, h=40)
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
                        ),
                    ],
                    justify="space-between",
                    style={"flex": 1},
                    h="100%",
                    px="md",
                ),
            ),
            dmc.AppShellNavbar(
                id="navbar",
                children=buttons,
                py="md",
                px=4,
            )
        ],
        header={"height": 60},
        navbar={
            "width": 300,
            "breakpoint": "sm",
            "collapsed": {"desktop": True, "mobile": True},
        },
        padding="md",
        id="appshell",
    )


# Callback to toggle navbar visibility
@callback(
    Output("appshell", "navbar"),
    Input("burger", "opened"),
    State("appshell", "navbar"),
)
def toggle_navbar(opened, navbar):
    navbar["collapsed"] = {"mobile": not opened, "desktop": True}
    return navbar
