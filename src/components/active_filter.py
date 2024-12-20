dmc.Group(
                                [
                                    dmc.Text("Active Filters:", size="sm", style={"paddingRight": "0px"}),
                                    dmc.ScrollArea(
                                        id="active-filters-container",
                                        scrollbarSize=0,
                                        style={
                                            "whiteSpace": "nowrap",
                                            "flexWrap": "nowrap",
                                            "display": "flex",
                                        },
                                    ),
                                ],
                                style={            
                                    "whiteSpace": "nowrap",
                                    "flexWrap": "nowrap",
                                    "display": "flex",
                                },
                            ),

# Callback to dynamically update active filters
@callback(
    Output("active-filters-container", "children"),
    [
        Input("sector-dropdown", "value"),
        Input("subsector-1-dropdown", "value"),
        Input("subsector-2-dropdown", "value"),
        Input("province-dropdown", "value"),
    ]
)
def update_active_filters(sector, subsector_1, subsector_2, province):
    filters = []
    if sector:
        filters.append(f"Sector: {sector}")
    if subsector_1:
        filters.append(f"Sub-Sector (1): {subsector_1}")
    if subsector_2:
        filters.append(f"Sub-Sector (2): {subsector_2}")
    if province:
        filters.append(f"Province: {province}")

    # Create a list of badges for each active filter
    return [
        dmc.Badge(
            filter_text, 
            color="blue", 
            variant="dot",
            size="sm",
            style={"marginRight": "8px", "marginBottom": "5px"}
        )
        for filter_text in filters
    ]