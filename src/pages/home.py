import dash_bootstrap_components as dbc
from dash import html, dcc
import dash_leaflet as dl

# Define the map
map_center = [45.5236, -122.6750]  # Example coordinates for Portland, OR
map_zoom = 13

# Create the map component
map_component = dl.Map(
    [
        dl.TileLayer(),  # Base map layer
        dl.Marker(position=map_center, children=[dl.Tooltip("Portland, OR")])  # Example marker
    ],
    id="map",
    style={'width': '100%', 'height': '500px'},
    center=map_center,
    zoom=map_zoom,
)

# Define the home page layout
home_page = dbc.Container(
    [
        html.H1("Home Page"),
        html.P("Welcome to the CDRI Data Hub Home Page!"),
        map_component,  # Add the map component to the page
    ],
    fluid=True,
    className="mt-4",
)