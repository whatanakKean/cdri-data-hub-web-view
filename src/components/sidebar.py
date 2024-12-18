import dash_mantine_components as dmc
from dash import html, dcc

# Sidebar components
def sidebar(data):
    sector_dropdown = dmc.Select(
        label="Select Sector",
        id="sector-dropdown",
        data=[{'label': sector, 'value': sector} for sector in data["Sector"].dropna().unique()],
        value='Agriculture',
        clearable=False,
        searchable=True,
        maxDropdownHeight=600,
        style={"marginBottom": "16px"}
    )

    subsector_1_dropdown = dmc.Select(
        label="Select Sub-Sector (1)",
        id="subsector-1-dropdown",
        data=[{'label': subsector_1, 'value': subsector_1} for subsector_1 in data["Sub-Sector (1)"].dropna().unique()],
        value='Production',
        clearable=False,
        searchable=True,
        maxDropdownHeight=600,
        style={"marginBottom": "16px"}
    )

    subsector_2_dropdown = dmc.Select(
        label="Select Sub-Sector (2)",
        id="subsector-2-dropdown",
        data=[{'label': subsector_2, 'value': subsector_2} for subsector_2 in data["Sub-Sector (2)"].dropna().unique()],
        value='Rice',
        clearable=False,
        searchable=True,
        maxDropdownHeight=600,
        style={"marginBottom": "16px"}
    )

    province_dropdown = dmc.Select(
        label="Select Province",
        id="province-dropdown",
        data=[
            {'label': 'All Provinces', 'value': 'All'},
            *[{'label': province, 'value': province} for province in data["Province"].dropna().unique()]
        ],
        value='All',  # Default value to "All Provinces"
        clearable=False,
        searchable=True,
        maxDropdownHeight=600,
        style={"marginBottom": "16px"}
    )

    control_panel = dmc.Paper(
        [
            sector_dropdown,
            subsector_1_dropdown,
            subsector_2_dropdown,
            province_dropdown
        ],
        shadow="xs",
        p="md",
        radius="md",
        withBorder=True,
        style={"marginBottom": "16px"}
    )

    info = dmc.Accordion(
        chevronPosition="right",
        variant="contained",
        children=[
            dmc.AccordionItem(
                value="bender",
                children=[
                    dmc.AccordionControl(
                        dmc.Group(
                            [
                                html.Div(
                                    [
                                        dmc.Text("Metadata"),
                                        dmc.Text("Fascinated with cooking, though has no sense of taste", size="sm", fw=400, c="dimmed"),
                                    ]
                                ),
                            ]
                        )
                    ),
                    dmc.AccordionPanel(dmc.Text("Bender Bending Rodríguez, (born September 4, 2996), designated Bending Unit 22, and commonly "
                                            "known as Bender, is a bending unit created by a division of MomCorp in Tijuana, Mexico, "
                                            "and his serial number is 2716057. His mugshot id number is 01473. He is Fry's best friend.", size="sm")),
                ]
            )
        ]
    )

    return dmc.Stack([control_panel, info])