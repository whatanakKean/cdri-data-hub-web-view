import dash_mantine_components as dmc
from dash import callback, Input, Output

def breadcrumb():
    """
    Renders the breadcrumb component.
    """
    # Initialize Breadcrumbs with empty children
    return dmc.Breadcrumbs(id="breadcrumb", style={"padding": "1rem 0 0 1rem"}, children=[])

@callback(
    Output("breadcrumb", "children"),
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
    active_item = dmc.Anchor(page_labels.get(pathname, ""), href=pathname, style={"fontWeight": "bold"})
    return [
        dmc.Anchor("Home", href="/", style={"marginRight": "0.5rem"}),
        active_item
    ]