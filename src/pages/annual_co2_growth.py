import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import dcc, html, register_page, Input, Output, callback
import dash_mantine_components as dmc

# Load data
df = pd.read_csv('Datasets/Annual_perc_change in co2/change-co2-annual-pct.csv')

# Calculate total emissions for each country
total_emissions = df.groupby('Entity')['Annual CO₂ emissions growth (%)'].sum()

# Get the top 10 countries
top_countries = df["Entity"].tolist()

# Filter the data for the top 10 countries
df_top_countries = df[df['Entity'].isin(top_countries[:])]

# Register the page
register_page(
    __name__,
    "/co2_growth_annually",
    title="CO2 Growth Annually",
    description="Annual Growth in CO2",
)

layout = html.Div([
    html.H1("Annual percentage change in CO₂ emissions"), 
    html.P('This interactive chart shows the year-on-year growth rate of CO2 emissions. A positive figure in a given year indicates that emissions were higher than the previous year. A negative figure indicates they were lower than the year before. For example, a change of 1.5% indicates that global emissions were 1.5% higher than the previous year (–1.5% would mean they were 1.5% lower).This measure allows us to see firstly where emissions are rising, and where they are falling; and secondly, the rate at which emissions are changing – whether the growth in emissions is slowing down or accelerating.'),
    html.Div([
        html.Div([
            html.Label("Select Plot Type:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='plot-type-dropdown',
                options=[
                    {'label': 'Map', 'value': 'choropleth'},
                    {'label': 'Chart', 'value': 'scatter'}
                ],
                value='choropleth',  # Select Choropleth map initially
                style={'width': '100%'}
            ),
        ], style={'marginBottom': '20px'}),
        html.Div([
            html.Label("Select Countries:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='country-dropdown-growth',
                options=[{'label': i, 'value': i} for i in df_top_countries['Entity'].unique()],
                value=['World'],
                multi=True,
                style={'width': '100%'}
            )
        ], style={'marginBottom': '20px'}),
        html.Div([
            html.Label("Select CO₂ emissions growth range (%):", style={'fontWeight': 'bold'}),
            dcc.RangeSlider(
                id='growth-range-slider',
                min=-50,
                max=50,
                value=[-50, 50],
                step=1,
                marks={
                    -50: '-50%',
                    -40: '-40%',
                    -30: '-30%',
                    -20: '-20%',
                    -10: '-10%',
                    0: '0%',
                    10: '10%',
                    20: '20%',
                    30: '30%',
                    40: '40%',
                    50: '50%'
                },
            ),
        ], style={'marginBottom': '20px'}),
        html.Div([
            html.Label("Select Year:", style={'fontWeight': 'bold'}),
            dcc.Slider(
                id='year-slider-growth',
                min=df['Year'].min(),
                max=df['Year'].max(),
                value=df['Year'].min(),
                marks={
                    str(df['Year'].min()): str(df['Year'].min()),
                    str(df['Year'].max()): str(df['Year'].max()),
                    str(df['Year'].min()): str(df['Year'].min())  # current value
                },
                step=1
            )
        ], style={'marginBottom': '20px'}),
    ], style={'width': '50%', 'margin': 'auto'}),
    dcc.Graph(id='plot-growth', style={'height': '80vh', 'marginTop': '50px'}),
])

# Define the callback for updating the dropdown based on plot type
@callback(
    Output('country-dropdown-growth', 'enabled'),
    Input('plot-type-dropdown', 'value')
)
def update_dropdown_disabled(plot_type):
    return plot_type != 'scatter'


# Define the callback for updating the slider based on plot type
@callback(
    Output('year-slider-growth', 'disabled'),
    Input('plot-type-dropdown', 'value')
)
def update_slider_disabled(plot_type):
    return plot_type != 'choropleth'

# Define the callback for updating the plot
@callback(
    Output('plot-growth', 'figure'),
    [Input('plot-type-dropdown', 'value'),
     Input('country-dropdown-growth', 'value'),
     Input('year-slider-growth', 'value'),
     Input('growth-range-slider', 'value')]  # Add the range slider as an input
)

def update_plot(plot_type, selected_countries, selected_year, growth_range):
    # Ensure selected_countries is a list
    if not isinstance(selected_countries, list):
        selected_countries = [selected_countries]

    if plot_type == 'scatter':
        fig = go.Figure()

        for country in selected_countries:
            df_country = df_top_countries[df_top_countries['Entity'] == country]
            fig.add_trace(
                go.Scatter(x=df_country['Year'], y=df_country['Annual CO₂ emissions growth (%)'], mode='lines', name=country,
                                       ))

        fig.update_layout(
            title_text="Annual percentage change in CO₂ emissions",
            xaxis_title='Year',
            yaxis_title='Annual percentage change in CO₂ emissions',
            hovermode='x unified',
           
        )
    else:  # plot_type == 'choropleth'
        df_year = df[df['Year'] == selected_year]
        df_top_countries_year = df_top_countries[df_top_countries['Year'] == selected_year]

        # Filter the data based on the selected growth range
        df_top_countries_year = df_top_countries_year[
            (df_top_countries_year['Annual CO₂ emissions growth (%)'] >= growth_range[0]) &
            (df_top_countries_year['Annual CO₂ emissions growth (%)'] <= growth_range[1])
        ]

        fig = px.choropleth(
            df_top_countries_year,  
            locations='Code',  # column with ISO 3166-1 alpha-3 country codes
            color='Annual CO₂ emissions growth (%)',  # column with color values
            hover_name='Entity',  # column to add to hover information
            color_continuous_scale=px.colors.sequential.Plasma_r,  # Change color scale
            range_color=(0, 20), 
            labels={'Annual CO₂ emissions growth (%)'},  # replaces default colorbar title
        )

        fig.update_layout(
            title_text='Annual CO₂ emissions growth (%) in'  + ' ' + str(selected_year),
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='equirectangular'
            )
        )

    return fig