import dash_mantine_components as dmc
from dash import html, dash_table
import pandas as pd

about_page = dmc.Container(
    [
        html.H1("About Page"),
        html.P("This is the About Page of the CDRI Data Hub."),
        
    ],
    fluid=True,
)