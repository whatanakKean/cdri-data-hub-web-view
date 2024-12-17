import dash_bootstrap_components as dbc
from dash import callback, Input, Output

def breadcrumb():
    """
    Renders the breadcrumb component.
    """
    return dbc.Breadcrumb(id="breadcrumb", style={"padding": "1rem 0 0 1rem"})

@callback(
    Output("breadcrumb", "items"),
    [Input("url", "pathname")]
)
def update_breadcrumb_items(pathname):
    """
    Dynamically updates breadcrumb items based on the URL.
    """
    page_labels = {
        "/about": "About",
        "/agriculture-and-rural-development": "Agriculture & Rural Development",
        "/development-economics-and-trade": "Development Economics & Trade",
        "/educational-research-and-innovation": "Educational Research & Innovation",
        "/natural-resource-and-environment": "Natural Resource & Environment",
        "/governance-and-inclusive-society": "Governance & Inclusive Society",
    }
    active_item = {"label": page_labels.get(pathname, ""), "active": True}
    return [{"label": "Home", "href": "/", "external_link": True}] + [active_item]
