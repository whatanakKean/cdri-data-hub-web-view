import dash
import dash_mantine_components as dmc
from dash import html

# Define the home page layout with animations and fullpage sections
home_page = dmc.Container(
    [
        html.Div(
            id="fullpage",  # This div will be the container for fullpage.js
            children=[
                dmc.Stack(
                    [
                        html.H1("CDRI Data Hub"),
                        html.P("Welcome to the CDRI Data Hub Home Page!"),
                    ],
                    className="section animate__animated animate__fadeInUp",  # Transition up effect
                    style={"height": "100vh"},  # Ensure full viewport height for the section
                ),
                dmc.Stack(
                    [
                        html.H1("Sectors"),
                        dmc.Carousel(
                            [
                                dmc.CarouselSlide(dmc.Center(f"Sector {i}", bg="blue", c="white", h="100%"))
                                for i in range(1, 7)
                            ],
                            id="carousel-size",
                            withIndicators=True,
                            height=200,
                            slideSize="33.3333%",
                            slideGap="md",
                            loop=True,
                            align="start",
                            slidesToScroll=3,
                        ),
                    ],
                    className="section animate__animated animate__fadeInUp",  # Transition up effect
                    style={"height": "100vh"},  # Full height for this section
                ),
                dmc.Stack(
                    [
                        html.H1("More Information"),
                        html.P("Explore additional content here."),
                    ],
                    className="section animate__animated animate__fadeInUp",  # Transition up effect
                    style={"height": "100vh"},  # Ensure full height for the section
                ),
            ],
        ),
    ],
    fluid=True,
    className="mt-4",
)
