# ********************** #

# Author: Whatnak KEAN   #

# ********************** #


from dash import html, dcc
from dash.dependencies import Input, Output
from dash_extensions.enrich import DashProxy, ServersideOutputTransform
import dash_bootstrap_components as dbc


from src.components.banner import banner
from src.components.footer import footer
from src.components.breadcrumb import breadcrumb
from src.pages.home import home_page
from src.pages.about import about_page
from src.pages.agriculture_and_rural_development import agriculture_and_rural_development
from src.pages.development_economics_and_trade import development_economics_and_trade
from src.pages.educational_research_and_innovation import educational_research_and_innovation
from src.pages.natural_resource_and_environment import natural_resource_and_environment
from src.pages.governance_and_inclusive_society import governance_and_inclusive_society
from src.pages.not_found import not_found_page

# Initialize the Dash app with DashProxy for enhanced features
app = DashProxy(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    transforms=[ServersideOutputTransform()],
    suppress_callback_exceptions=True,
)

# Set the server for the app
server = app.server

# Define the app title
app.title = "CDRI Data Hub"

# Define the app layout
app.layout = dbc.Container(
    fluid=True,
    style={"padding": "0", "minHeight": "100vh"},
    children=[
        dcc.Location(id="url", refresh=False),
        banner(),
        breadcrumb(),
        html.Div(id="page-content"),
        footer(),
    ],
)

# Callback to display the correct page based on the URL
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")],
)

# Routes to page
def display_page(pathname):
    if pathname == "/":
        return home_page
    elif pathname == "/about":
        return about_page
    elif pathname == "/agriculture-and-rural-development":
        return agriculture_and_rural_development
    elif pathname == "/development-economics-and-trade":
        return development_economics_and_trade
    elif pathname == "/educational-research-and-innovation":
        return educational_research_and_innovation
    elif pathname == "/natural-resource-and-environment":
        return natural_resource_and_environment
    elif pathname == "/governance-and-inclusive-society":
        return governance_and_inclusive_society
    else:
        return not_found_page


# Run the server
if __name__ == "__main__":
    app.run_server(
        debug=True,
        # host="0.0.0.0",
        port=8050,
        processes=1,
        threaded=True,
    )