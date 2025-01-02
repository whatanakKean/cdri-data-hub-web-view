import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import html

sector = [
    {"name": "Agriculture and Rural Development", 
     "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Cambodian_farmers_planting_rice.jpg/1200px-Cambodian_farmers_planting_rice.jpg", 
     "isEnabled": True, 
     "href": "/agriculture-and-rural-development"},
    {"name": "Development Economics and Trade", 
     "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Phnompenhview.jpg/450px-Phnompenhview.jpg", 
     "isEnabled": False, 
     "href": "/development-economics-and-trade"},
    {"name": "Educational Research and Innovation", 
     "image": "https://opendevelopmentcambodia.net/wp-content/uploads/2021/05/8385981409_704990f061_o-1536x1025.jpg", 
     "isEnabled": False, 
     "href": "/educational-research-and-innovation"},
    {"name": "Natural Resource and Environment", 
     "image": "https://www.undp.org/sites/g/files/zskgke326/files/migration/kh/UNDP_KH_Kulen.jpg", 
     "isEnabled": False, 
     "href": "/natural-resource-and-environment"},
    {"name": "Governance and Inclusive Society", 
     "image": "https://upload.wikimedia.org/wikipedia/en/thumb/6/66/Cambodian_Peace_Palace_%28day%29.jpg/450px-Cambodian_Peace_Palace_%28day%29.jpg", 
     "isEnabled": False, 
     "href": "/governance-and-inclusive-society"}
]

home_page = html.Main([  
    # Home Section
    html.Div(
        style={
            "height": "600px",
            "backgroundImage": "url('./assets/background.jpg')",
            "backgroundSize": "cover",
            "backgroundPosition": "center",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center",
            "alignItems": "center",
        },
        children=[
            dmc.Stack(
                p="md",
                children=[
                    dmc.Title('CDRI Data Hub', order=1, style={'color': 'white', 'fontSize': '3rem'}),
                    dmc.Text("Empowering Evidence-Based Decision-Making", size="xl", style={'color': 'white', 'fontSize': '1.5rem'}),
                ],
            )
        ],
    ),
  
    # About Section
    dmc.Container(
        id='about',
        style={
            "height": "100%",
            "padding": "50px",  
            "textAlign": "center",  
        },
        children=[
            dmc.Text(
                "CDRI Data Hub is a centralized repository for research-related data, offering reliable information across various sectors in Cambodia. It supports evidence-based decision-making by providing datasets, visualization tools, and resources tailored to researchers, policymakers, and practitioners.",
                size="lg",
                py=3,
                fw=500,
                style={
                    "lineHeight": "1.6",  
                    "fontSize": "1rem",  # Make text size smaller for better readability on mobile
                },
            )
        ],
    ),

    # Mission Section
    dmc.Container(
        style={
            "height": "100%",
            "padding": "50px",  
            "textAlign": "center",  
        },
        children=[            
            dmc.Title(
                'Mission',
                order=2,
                style={
                    "position": "relative",
                    "fontSize": "2.5rem",  
                    "color": "#336666",    # Update the color
                    "marginBottom": "2rem",  
                    "textAlign": "center",
                    "textDecoration": "underline"  # Add underline
                },
            ),
            dmc.SimpleGrid(
                cols={"base": 1, "sm": 1, "lg": 3},
                children=[
                    html.Div(
                        style={
                            "padding": "20px",
                            "borderRadius": "8px",
                            "boxShadow": "0px 4px 8px rgba(0, 0, 0, 0.1)",
                        },
                        children=[
                            DashIconify(icon="icon-park:data-all", width=50),
                            dmc.Text(
                                "Provide accessible, high-quality data on various sectors in Cambodia.",
                                size="md",
                                style={
                                    "fontSize": "14px",  # Smaller font size for smaller screens
                                    "lineHeight": "1.5",  # Adjust line height for readability
                                },
                            ),
                        ],
                    ),
                    html.Div(
                        style={
                            "padding": "20px",
                            "borderRadius": "8px",
                            "boxShadow": "0px 4px 8px rgba(0, 0, 0, 0.1)",
                        },
                        children=[
                            DashIconify(icon="icon-park:data-file", width=50),
                            dmc.Text(
                                "Support decision-making through easy-to-use data visualization tools.",
                                size="md",
                                style={
                                    "fontSize": "14px",  # Smaller font size for better readability on small screens
                                    "lineHeight": "1.5",  # Adjust line height for readability
                                },
                            ),
                        ],
                    ),
                    html.Div(
                        style={
                            "padding": "20px",
                            "borderRadius": "8px",
                            "boxShadow": "0px 4px 8px rgba(0, 0, 0, 0.1)",
                        },
                        children=[
                            DashIconify(icon="fluent-color:building-people-16", width=50),
                            dmc.Text(
                                "Foster collaboration among researchers, policymakers, and practitioners.",
                                size="md",
                                style={
                                    "fontSize": "14px",  # Adjusted for smaller screens
                                    "lineHeight": "1.5",  # Adjust line height for better readability
                                },
                            ),
                        ],
                    ),
                ],
                style={
                    "marginTop": "20px",
                    "gap": "20px",
                }
            ),
        ]
    ),

    # Sector Section
    dmc.Container(
        style={
            "height": "100%",
            "padding": "50px",  
            "textAlign": "center",  
        },
        children=[            
            dmc.Title(
                'Sectors',
                order=2,
                style={
                    "position": "relative",
                    "fontSize": "2.5rem",  
                    "color": "#336666",    # Update the color
                    "marginBottom": "2rem",  
                    "textAlign": "center",
                    "textDecoration": "underline"  # Add underline
                },
            ),
            dmc.SimpleGrid(
                cols={"base": 1, "sm": 2, "lg": 3},
                children=[
                    dmc.Card(
                        children=[
                            dmc.CardSection(
                                dmc.Image(
                                    src=sector_data["image"],
                                    h=160,
                                    alt=sector_data["name"],
                                    className="image-hover-zoom",
                                )
                            ),
                            dmc.Group(
                                children=[
                                    dmc.Text(sector_data["name"], w=500),
                                ],
                                justify="space-between",
                                mt="md",
                                mb="xs",
                            ),
                            # Use dmc.Anchor for links
                            dmc.Anchor(
                                children=dmc.Button(
                                    "Explore Data" if sector_data["isEnabled"] else "Coming Soon",
                                    color="blue" if sector_data["isEnabled"] else "gray",
                                    mt="md",
                                    radius="md",
                                    fullWidth=True,
                                    disabled=not sector_data["isEnabled"],
                                ),
                                href=sector_data["href"] if sector_data["isEnabled"] else "#",
                                target="_self"
                            ),
                        ],
                        withBorder=True,
                        shadow="sm",
                        radius="md",
                    ) for sector_data in sector
                ]
            ),
        ]
    )
])
