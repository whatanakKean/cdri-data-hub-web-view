import dash_mantine_components as dmc
from dash import html

# Define the home page layout
home_page = dmc.Container(
    [
        html.H1("CDRI Data Hub"),
        html.P("Welcome to the CDRI Data Hub Home Page!"),
        dmc.Text(
            "Plotly Dash library is extremely useful for developers and data analysts for "
            "several reasons. With its simple interface and rich palette of components it "
            "is possible to quickly create interactive web applications allowing users to "
            "interact with data. This flexibility is supported by the ability to create "
            "different types of visualizations such as charts, tables and heatmaps which "
            "helps communicate information more effectively. Plotly Dash is built on "
            "Python making it easy to integrate with existing tools and libraries for data "
            "analysis. With this open-source tool and an active developer community you "
            "have access to regular updates and support. In addition the ease of deployment "
            "on different platforms makes Plotly Dash a great tool for sharing applications "
            "and integrating into different systems",
            size=12,
            id="animated-text",
            className="animate__animated animate__fadeInUp animate__faster",
        ),
        
        
    ],
    fluid=True,
    className="mt-4",
)
