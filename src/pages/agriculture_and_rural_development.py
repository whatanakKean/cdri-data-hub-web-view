import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback, State, Patch
import pandas as pd
import dash_ag_grid as dag
import plotly.graph_objects as go

df = pd.read_csv('https://raw.githubusercontent.com/plotly/Figure-Friday/main/2024/week-32/irish-pay-gap.csv')
df['Report Link'] = df['Report Link'].apply(lambda x: f'[Report]({x})')
df['Company'] = df.apply(lambda row: f'[{row["Company Name"]}]({row["Company Site"]})', axis=1)
df.rename(columns={'Q1 Men': 'Q1 Male'}, inplace=True)

numeric_columns = [
   'Mean Hourly Gap', 'Median Hourly Gap', 'Mean Bonus Gap', 'Median Bonus Gap', 'Mean Hourly Gap Part Time',
   'Median Hourly Gap Part Time', 'Mean Hourly Gap Part Temp', 'Median Hourly Gap Part Temp', 'Percentage Bonus Paid Female',
   'Percentage Bonus Paid Male', 'Percentage BIK Paid Female', 'Percentage BIK Paid Male', 'Q1 Female', 'Q1 Male', 'Q2 Female',
   'Q2 Male', 'Q3 Female', 'Q3 Male', 'Q4 Female', 'Q4 Male', 'Percentage Employees Female', 'Percentage Employees Male'
]

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
        [year_radio, company_dropdown ],
        className="bg-light",
    ),
    className="mb-4"
)


metadata_card = dcc.Markdown(
    """
    Starting from 2022, Gender Pay Gap Reporting is a regulatory requirement that mandates employers in Ireland with
     more than 250 employees to publish information on their gender pay gap.
     
     [Data source](https://paygap.ie/)
     
     [Data source GitHub](https://github.com/zenbuffy/irishGenderPayGap/tree/main)
     
     This site was created for Plotly's Figure Friday challenge. For additional data visualizations of this dataset and
      to join the conversation, visit the [Plotly Community Forum](https://community.plotly.com/t/figure-friday-2024-week-32/86401)
    """
)

info = dbc.Accordion([ 
    dbc.AccordionItem(metadata_card, title="Metadata")
],  start_collapsed=True)


def make_bar_chart(data):
    if not data or not data[0]:
        return html.Div("No data available for the selected company and year.")

    data = data[0]

    # Separate the data for male and female
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    male_percentages = [data[f'{q} Male'] for q in quarters]
    female_percentages = [data[f'{q} Female'] for q in quarters]

    quarter_labels = {
        'Q1': 'Lower (Q1)',
        'Q2': 'Lower Middle (Q2)',
        'Q3': 'Upper Middle (Q3)',
        'Q4': 'Upper (Q4)'
    }
    custom_labels = [quarter_labels[q] for q in quarters]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=custom_labels,
        x=male_percentages,
        name='Male',
        orientation='h',
        marker=dict(color='#19A0AA'),
        text=male_percentages,
        textfont_size=14,
        textposition='inside',  # Position the text inside the bars
    ))

    fig.add_trace(go.Bar(
        y=custom_labels,
        x=female_percentages,
        name='Female',
        orientation='h',
        marker=dict(color='#F15F36'),
        text=female_percentages,
        textfont_size=14,
        textposition='inside',
    ))

    fig.update_layout(
        xaxis=dict(ticksuffix='%'),
        yaxis=dict(title='Quartile', categoryorder='array', categoryarray=quarters),
        barmode='stack',
        template='plotly_white',
        legend=dict(
            orientation='h',  # Horizontal legend
            yanchor='bottom',
            y=-0.25,  # Position below the chart
            xanchor='center',
            x=0.5,  # Centered horizontally
            traceorder='normal'
        ),
        margin=dict(l=10, r=10, t=10, b=10),
    )

    return dbc.Card([
        dbc.CardHeader(html.H2("Proportion of men and women in each pay quartile"), className="text-center"),
        dcc.Graph(figure=fig, style={"height": 250}, config={'displayModeBar': False})
    ])


@callback(
    Output("bar-chart-card", "children"),
    Input("store-selected", "data")
)
def update_bar_chart(data):
    return make_bar_chart(data)


@callback(
    Output("paygap-card", "children"),
    Input("store-selected", "data")
)
def make_pay_gap_card(data):
    if not data:
        return ""

    data = data[0]
    data = {k: (f"{v}%" if v else '') for k, v in data.items()}
    
    paygap = dbc.Row([
        dbc.Col([html.Div("Hourly Pay Gap", className="border-bottom border-3"),
                 html.Div("ALL"), html.Div("Part Time"), html.Div("Temporary")], style={"minWidth": 250}),
        dbc.Col([html.Div("Mean", className="border-bottom border-3"),
                 html.Div(f"{data['Mean Hourly Gap']}"), html.Div(f"{data['Mean Hourly Gap Part Time']}"),
                 html.Div(f"{data['Mean Hourly Gap Part Temp']}")]),
        dbc.Col([html.Div("Median", className="border-bottom border-3"),
                 html.Div(f"{data['Median Hourly Gap']}"), html.Div(f"{data['Median Hourly Gap Part Time']}"),
                 html.Div(f"{data['Median Hourly Gap Part Temp']}")])
    ], style={"minWidth": 400})

    mean = dbc.Alert(dcc.Markdown(f"** Mean Pay **\n### {data['Mean Hourly Gap']}  Higher for men"), color="dark")
    median = dbc.Alert(dcc.Markdown(f"** Median Pay **\n### {data['Median Hourly Gap']}  Higher for men"), color="dark")

    card = dbc.Card([
        dbc.CardHeader(html.H2("Hourly Pay Gap"), className="text-center"),
        dbc.CardBody([dbc.Row([dbc.Col(mean), dbc.Col(median)], className="text-center"), paygap])
    ])
    return card


@callback(
    Output("bonusgap-card", "children"),
    Input("store-selected", "data")
)
def make_bonus_gap_card(data):
    if not data or 'Mean Bonus Gap' not in data[0] or data[0]['Mean Bonus Gap'] == '':
        return ""

    data = data[0]
    data = {k: (f"{v}%" if v else '') for k, v in data.items()}
    
    bonusgap = dbc.Row([
        html.Div("Proportion of employees by gender to receive a bonus:", className="mb-1"),
        dbc.Col([html.Div("Bonus and BIK Pay Gap", className="border-bottom border-3"),
                 html.Div("Bonus"), html.Div("Benefits In Kind")], style={"minWidth": 250}),
        dbc.Col([html.Div("Men", className="border-bottom border-3"),
                 html.Div(f"{data['Percentage Bonus Paid Male']}"), html.Div(f"{data['Percentage BIK Paid Male']}")]),
        dbc.Col([html.Div("Women", className="border-bottom border-3"),
                 html.Div(f"{data['Percentage Bonus Paid Female']}"), html.Div(f"{data['Percentage BIK Paid Female']}")])
    ], style={"minWidth": 400})

    mean = dbc.Alert(dcc.Markdown(f"** Mean Bonus Pay **\n### {data['Mean Bonus Gap']}  Higher for men"), color="dark")
    median = dbc.Alert(dcc.Markdown(f"** Median Bonus Pay **\n### {data['Median Bonus Gap']}  Higher for men"), color="dark")

    card = dbc.Card([
        dbc.CardHeader(html.H2("Bonus Gap"), className="text-center"),
        dbc.CardBody([dbc.Row([dbc.Col(mean), dbc.Col(median)], className="text-center"), bonusgap])
    ])
    return card


@callback(
    Output("store-selected", "data"),
    Input("company-dropdown", "value"),
    Input("year-radio", "value"),
)
def pin_selected_report(company, yr):
    dff = df[(df["Company Name"] == company) & (df['Report Year'] == yr)]
    dff = dff.fillna('')
    records = dff.to_dict("records")
    return records


agriculture_and_rural_development = dbc.Container(
    [
        dcc.Store(id="store-selected", data={}),
        dbc.Row([
            dbc.Col([control_panel, info], md=3),
            dbc.Col(
                [
                    # dbc.Row([dbc.Col(html.Div(id="paygap-card")), dbc.Col(html.Div(id="bonusgap-card"))]),
                    html.Div(id="bar-chart-card", className="mt-4"),
                ], md=9
            ),
        ]),
    ],
    fluid=True,
)
