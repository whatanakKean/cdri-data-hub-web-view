import dash_bootstrap_components as dbc

def breadcrumb():
    return dbc.Breadcrumb(
        items=[
            {"label": "Docs", "href": "/docs", "external_link": True},
            {
                "label": "Components",
                "href": "/docs/components",
                "external_link": True,
            },
            {"label": "Breadcrumb", "active": True},
        ],
        style={"padding-top": "1rem", "padding-left": "1rem"}
    )