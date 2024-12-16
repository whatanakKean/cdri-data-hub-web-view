import dash_bootstrap_components as dbc
from dash import html, dcc

# Sidebar components
def sidebar(df):
    company_dropdown = html.Div(
        [
            dbc.Label("Select a Company", html_for="company-dropdown"),
            dcc.Dropdown(
                id="company-dropdown",
                options=[{'label': company, 'value': company} for company in sorted(df["Company Name"].unique())],
                value='Ryanair',
                clearable=False,
                maxHeight=600,
                optionHeight=50
            ),
        ],  className="mb-4",
    )

    year_radio = html.Div(
        [
            dbc.Label("Select Year", html_for="date-checklist"),
            dbc.RadioItems(
                options=[{'label': str(year), 'value': year} for year in [2023, 2022]],
                value=2023,
                id="year-radio",
            ),
        ],
        className="mb-4",
    )

    control_panel = dbc.Card(
        dbc.CardBody(
            [year_radio, company_dropdown],
            className="bg-light",
        ),
        className="mb-4 mt-4"
    )

    metadata_card = dcc.Markdown(
        """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

        [Data source](https://example.com/data)

        [Data source GitHub](https://github.com/example/repository)

        This site was created as part of a visualization challenge. For additional examples and to join the discussion, visit the 
        [Visualization Community Forum](https://example.com/forum)
        """
    )


    info = dbc.Accordion([ 
        dbc.AccordionItem(metadata_card, title="Metadata")
    ],  start_collapsed=True)

    return dbc.Col([control_panel, info], md=3)
