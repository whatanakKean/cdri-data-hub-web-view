# ********************** #

# Author: Whatnak KEAN   #

# ********************** #


from dash import html, dcc, Dash, _dash_renderer
from dash.dependencies import Input, Output, State
from dash_extensions.enrich import DashProxy, ServersideOutputTransform
import dash_mantine_components as dmc
_dash_renderer._set_react_version("18.2.0")


from src.components.banner import banner
from src.components.footer import footer
from src.components.breadcrumb import breadcrumb
from src.pages.home import home_page
from src.pages.about import about_page
from src.pages.agriculture_and_rural_development import agriculture_and_rural_development
from src.pages.development_economics_and_trade import development_economics_and_trade
# from src.pages.educational_research_and_innovation import educational_research_and_innovation
# from src.pages.natural_resource_and_environment import natural_resource_and_environment
# from src.pages.governance_and_inclusive_society import governance_and_inclusive_society
from src.pages.not_found import not_found_page

# Initialize the Dash app
app = DashProxy(
    __name__,
    external_stylesheets=[dmc.styles.ALL, dmc.styles.CHARTS, dmc.styles.CAROUSEL],
    transforms=[ServersideOutputTransform()],
    suppress_callback_exceptions=True,
)

# Define the app title
app.title = "CDRI Data Hub"
app._favicon = ("favicon.ico")

app.layout = dmc.MantineProvider(
    dmc.AppShell(
        [
            dcc.Location(id="url", refresh=False),
            *banner(),
            dmc.AppShellMain(
                # dcc.Loading(
                #     [
                #         breadcrumb(),
                #         html.Div(id="page-content"),
                #     ]
                # ),
                [
                    breadcrumb(),
                    html.Div(id="page-content"),
                ]
            ),
            footer()
        ],
        header={"height": 60},
        navbar={
            "width": 300,
            "breakpoint": "sm",
            "collapsed": {"desktop": True, "mobile": True},
        },
        id="appshell",
    )
)


# Callback to display the correct page based on the URL
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")],
)
def display_page(pathname):
    # Return the corresponding page or the 404 page if not found
    page_routes = {
        "/": home_page,
        "/about": about_page,
        "/agriculture-and-rural-development": agriculture_and_rural_development,
        "/development-economics-and-trade": development_economics_and_trade,
        # "/educational-research-and-innovation": educational_research_and_innovation,
        # "/natural-resource-and-environment": natural_resource_and_environment,
        # "/governance-and-inclusive-society": governance_and_inclusive_society,
    }
    return page_routes.get(pathname, not_found_page)

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True, port=8050, processes=1, threaded=True)