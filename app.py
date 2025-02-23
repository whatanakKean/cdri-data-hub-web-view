# ********************** #

# Author: Whatnak KEAN   #

# ********************** #


from dash import html, dcc, Dash, _dash_renderer
from dash.dependencies import Input, Output, State
from dash_extensions.enrich import DashProxy, ServersideOutputTransform
from dash_iconify import DashIconify
import dash_mantine_components as dmc

_dash_renderer._set_react_version("18.2.0")


from src.components.banner import banner
from src.components.footer import footer
from src.components.breadcrumb import breadcrumb
from src.pages.home import home_page
from src.pages.data_explorer import data_explorer_page
# from src.pages.sector import sector_page
from src.pages.agriculture_and_rural_development import agriculture_and_rural_development
from src.pages.development_economics_and_trade import development_economics_and_trade
from src.pages.education import education
from src.pages.not_found import not_found_page

# Initialize the Dash app
app = DashProxy(
    __name__,
    external_stylesheets=[
        dmc.styles.ALL,
        dmc.styles.CAROUSEL,
        "https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css",  # Animation CSS
    ],
    transforms=[ServersideOutputTransform()],
    suppress_callback_exceptions=True,
)

# Define the app title
app.title = "CDRI Data Hub"
app._favicon = ("favicon.ico")

app.layout = dmc.MantineProvider(
    dmc.AppShell(
        [
            dcc.Location(id="url", refresh=True),
            *banner(),
            dmc.AppShellMain(
                [
                    # breadcrumb(),
                    html.Div(id="page-content"),
                ]
            ),
            footer(),
            dcc.Store(id="scroll-to-top-trigger"),
            dmc.Affix(
                dmc.Button(
                    DashIconify(icon="ic:baseline-arrow-upward", width=20),
                    id="back-to-top-btn",
                    color="#336666",
                    size="xs"
                ),
                position={"bottom": 10, "right": 10},
            ),
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

# Client-side callback for smooth scrolling
app.clientside_callback(
    """
    function(trigger) {
        if (trigger) {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
        return null;  // Reset the trigger
    }
    """,
    Output("scroll-to-top-trigger", "data"),
    Input("back-to-top-btn", "n_clicks"),
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
        "/data-explorer": data_explorer_page,
        "/agriculture-and-rural-development": agriculture_and_rural_development,
        "/development-economics-and-trade": development_economics_and_trade,
        "/education": education,
    }
    return page_routes.get(pathname, not_found_page)

server = app.server

# Run the server
if __name__ == "__main__":
    app.run_server(debug="True", port=8050, processes=1, threaded=True)