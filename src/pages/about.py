import dash_bootstrap_components as dbc
from dash import html, dash_table
import pandas as pd

# Sample data for the DataTable
data = {
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "Country": ["USA", "Canada", "UK"]
}
df = pd.DataFrame(data)

about_page = dbc.Container(
    [
        html.H1("About Page"),
        html.P("This is the About Page of the CDRI Data Hub."),
        
        dash_table.DataTable(
            id='sample-table',
            columns=[
                {"name": col, "id": col} for col in df.columns
            ],
            data=df.to_dict('records'),
            style_table={'marginTop': '20px'},  # Adding some spacing
            style_cell={
                'textAlign': 'left',
                'padding': '5px',
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        ),
    ],
    fluid=True,
    className="mt-4",
)