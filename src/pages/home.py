import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import html

sector = [
    {"name": "Agriculture and Rural Development", 
     "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Cambodian_farmers_planting_rice.jpg/1200px-Cambodian_farmers_planting_rice.jpg", 
     "isEnabled": True, 
     "href": "/agriculture-and-rural-development"},
    {"name": "Education", 
     "image": "https://cdri.org.kh/storage/images/banner_1630049852.jpg", 
     "isEnabled": True, 
     "href": "/education"},
    {"name": "Development Economics and Trade", 
     "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Phnompenhview.jpg/450px-Phnompenhview.jpg", 
     "isEnabled": True, 
     "href": "/"},
    {"name": "Natural Resources and Environment", 
     "image": "	https://cdri.org.kh/storage/images/CNRE_1630041306.jpg", 
     "isEnabled": True, 
     "href": "/"},
    {"name": "Governance and Inclusive Society", 
     "image": "https://cdri.org.kh/storage/images/cgis_banner_16300551491_1716455322.jpg", 
     "isEnabled": True, 
     "href": "/"},
]

home_page = html.Main([  
    # Home Section
    html.Div(
        style={
            "height": "500px",
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
                className="animate__animated animate__fadeInUp animate__fast"
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
                "CDRI Data Hub is a centralized repository for research data, offering reliable knowledge and insights across various sectors in Cambodia. It supports evidence-based decision-making by providing datasets, visualization tools, and knowledge tailored to researchers, policymakers, and private sector.",
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
                    "color": "#336666",
                    "marginBottom": "2rem",  
                    "textAlign": "center",
                    "textDecoration": "underline"
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
                                    "fontSize": "14px",
                                    "lineHeight": "1.5",
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
                                    "fontSize": "14px",
                                    "lineHeight": "1.5",
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
                            DashIconify(icon="icon-park:peoples-two", width=50),
                            dmc.Text(
                                "Foster collaboration among researchers, policymakers, and private sector.",
                                size="md",
                                style={
                                    "fontSize": "14px",
                                    "lineHeight": "1.5",
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
                    "color": "#336666",
                    "marginBottom": "2rem",  
                    "textAlign": "center",
                    "textDecoration": "underline"
                },
            ),
            dmc.Grid(
                justify="center",
                children=[
                    dmc.GridCol(
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
                                # dmc.Group(
                                #     children=[
                                #         dmc.Text(sector_data["name"], w=500),
                                #     ],
                                #     justify="space-between",
                                #     mt="md",
                                #     mb="xs",
                                # ),
                                # Use dmc.Anchor for links
                                dmc.Anchor(
                                    children=dmc.Button(
                                        sector_data["name"] if sector_data["isEnabled"] else "Coming Soon",
                                        color="#336666" if sector_data["isEnabled"] else "gray",
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
                        ),
                        span={"base": 12, "md": 6, "lg":6}
                    )
                    for sector_data in sector
                ]
            ),
        ]
    )
])
