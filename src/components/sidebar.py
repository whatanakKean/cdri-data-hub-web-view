import dash_bootstrap_components as dbc
from dash import html, dcc

# Sidebar components
def sidebar(data):
    sector_dropdown = html.Div(
        [
            dbc.Label("Select Sector", html_for="sector-dropdown"),
            dcc.Dropdown(
                id="sector-dropdown",
                options=[{'label': sector, 'value': sector} for sector in data["Sector"].dropna().unique()],
                value='Agriculture',
                clearable=False,
                maxHeight=600,
                optionHeight=50
            ),
        ],  className="mb-4",
    )

    subsector_1_dropdown = html.Div(
        [
            dbc.Label("Select Sub-Sector (1)", html_for="subsector-1-dropdown"),
            dcc.Dropdown(
                id="subsector-1-dropdown",
                options=[{'label': subsector_1, 'value': subsector_1} for subsector_1 in data["Sub-Sector (1)"].dropna().unique()],
                value='Production',
                clearable=False,
                maxHeight=600,
                optionHeight=50
            ),
        ],  className="mb-4",
    )

    subsector_2_dropdown = html.Div(
        [
            dbc.Label("Select Sub-Sector (2)", html_for="subsector-2-dropdown"),
            dcc.Dropdown(
                id="subsector-2-dropdown",
                options=[{'label': subsector_2, 'value': subsector_2} for subsector_2 in data["Sub-Sector (2)"].dropna().unique()],
                value='Rice',
                clearable=False,
                maxHeight=600,
                optionHeight=50
            ),
        ],  className="mb-4",
    )

    province_dropdown = html.Div(
        [
            dbc.Label("Select Province", html_for="province-dropdown"),
            dcc.Dropdown(
                id="province-dropdown",
                options=[
                    {'label': 'All Provinces', 'value': 'All'},
                    *[{'label': province, 'value': province} for province in data["Province"].dropna().unique()]
                ],
                value='All',  # Default value to "All Provinces"
                clearable=False,
                maxHeight=600,
                optionHeight=50
            ),
        ], className="mb-4",
    )

    control_panel = dbc.Card(
        dbc.CardBody(
            [sector_dropdown, subsector_1_dropdown, subsector_2_dropdown, province_dropdown],
            className="bg-light",
        ),
        className="mb-4 mt-2"
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
