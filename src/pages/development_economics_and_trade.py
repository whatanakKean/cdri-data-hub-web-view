import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import Dash, html, Output, Input, callback
from dash_extensions.javascript import arrow_function, assign

development_economics_and_trade = dl.Map(children=[
    dl.TileLayer(url="https://tile.openstreetmap.org/{z}/{x}/{y}.png")
], style={'height': '50vh'}, center=[56, 10], zoom=6)
