import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Load and preprocess data
df = pd.read_csv('https://raw.githubusercontent.com/tomasduricek/animated-graphs/main/retail_data.csv')
df['date'] = pd.to_datetime(df['date'].astype(str).str[:7], format="%Y-%m")
df = df.sort_values(['date', 'retail_group'], ignore_index=True)

RETAIL_GROUP_COLORS = ['#1F4068', '#527A82', '#DE8918', '#BF3200']
FIRST_DAY_OF_ALL_YEARS = df[df['date'].dt.month == 1]['date'].unique()
N_UNIQUE_RETAIL_GROUPS = df['retail_group'].nunique()

# Create indexed dataframe for animation
df_indexed = pd.DataFrame()
for index in np.arange(start=0, stop=len(df)+1, step=N_UNIQUE_RETAIL_GROUPS):
    df_slicing = df.iloc[:index].copy()
    df_slicing['frame'] = (index//N_UNIQUE_RETAIL_GROUPS)
    df_indexed = pd.concat([df_indexed, df_slicing])

# Create base plots
scatter_plot = px.scatter(
    df_indexed,
    x='date',
    y='average_monthly_income',
    color='retail_group',
    animation_frame='frame',
    color_discrete_sequence=RETAIL_GROUP_COLORS
)

for frame in scatter_plot.frames:
    for data in frame.data:
        data.update(mode='markers', showlegend=True, opacity=1)
        data['x'] = np.take(data['x'], [-1])
        data['y'] = np.take(data['y'], [-1])

line_plot = px.line(
    df_indexed,
    x='date',
    y='average_monthly_income',
    color='retail_group',
    animation_frame='frame',
    color_discrete_sequence=RETAIL_GROUP_COLORS,
    line_shape='spline'
)
line_plot.update_traces(showlegend=False)

# Create combined figure
combined_plot = go.Figure(
    data=line_plot.data + scatter_plot.data,
    frames=[go.Frame(data=f.data, name=f.name) for f in line_plot.frames],
    layout=line_plot.layout
)

# Update frames for autoscaling
frames = []
for frame in combined_plot.frames:
    x_data = [x for trace in frame.data for x in (trace.x if trace.x is not None else [])]
    y_data = [y for trace in frame.data for y in (trace.y if trace.y is not None else [])]
    
    new_frame = go.Frame(
        data=frame.data,
        layout=go.Layout(
            xaxis={
                'range': [min(x_data) if x_data else None, 
                         (max(x_data) + pd.DateOffset(months=2)) if x_data else None],
                'tickformat': '%Y',
                'tickvals': FIRST_DAY_OF_ALL_YEARS
            },
            yaxis={
                'range': [min(y_data) * 0.3 if y_data else None,
                         max(y_data) * 1.5 if y_data else None],
                'nticks': 6
            }
        )
    )
    frames.append(new_frame)

combined_plot.frames = frames

# Final layout adjustments
combined_plot.update_layout(
    yaxis=dict(
        gridcolor='#7a98cf',
        griddash='dot',
        gridwidth=0.5,
        linewidth=2,
        tickwidth=2,
        title="Average price (k)",
        title_font=dict(size=16)
    ),
    xaxis=dict(
        linewidth=2,
        tickwidth=2,
        title="Date",
        title_font=dict(size=16)
    ),
    font=dict(size=18),
    showlegend=True,
    legend=dict(title='Retail group'),
    title="Monthly Retail Prices During Covid-19",
    plot_bgcolor='#fffcf7',
    paper_bgcolor='#fffcf7',
    title_x=0.5
)

combined_plot.update_traces(
    line=dict(width=5),
    marker=dict(size=12)
)

# Remove sliders and adjust animation
combined_plot['layout'].pop('sliders', None)
combined_plot.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 150
combined_plot.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 120

# Create Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Retail Prices Animation", style={'textAlign': 'center'}),
    dcc.Graph(
        id='animated-graph',
        figure=combined_plot,
        config={'responsive': True}
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)