import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import dcc, html, register_page, Input, Output, callback
import dash_mantine_components as dmc

# Load data
df = pd.read_csv('Datasets/annual_share_of_co2/annual-share-of-co2-emissions.csv')

# Calculate total emissions for each country
total_emissions = df.groupby('Entity')['Share of global annual CO₂ emissions'].sum()

# Get the top 10 countries
top_countries = df["Entity"].tolist()

# Filter the data for the top 10 countries
df_top_countries = df[df['Entity'].isin(top_countries[:])]

# Register the page
register_page(
    __name__,
    "/annual_share_of_co2",
    title="Annual share of co2",
    description="Annual share of co2",
)

layout = html.Div([
    dmc.Text(" Percentage CO2 Emission Share", align="center", style={"fontSize": 30}), 
    html.Div([
        html.Div([
            html.Label("Select Plot Type:"),
            dcc.Dropdown(
                id='plot-type-dropdown',
                options=[
                    {'label': 'Choropleth Map', 'value': 'choropleth'},
                    {'label': 'Scatter Plot', 'value': 'scatter'}
                ],
                value='choropleth',  # Select Choropleth map initially
                style={'width': '100%'}
            ),
        ], style={'marginBottom': '20px'}),
        html.Div([
            html.Label("Select Countries:"),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': i, 'value': i} for i in df_top_countries['Entity'].unique()],
                value=['China', 'United States', 'India', 'United Kingdom', 'Canada', 'European Union (27)'],
                multi=True,
                style={'width': '100%'}
            )
        ], style={'marginBottom': '20px'}),
        html.Div([
            html.Label("Select Year:"),
            dcc.Slider(
                id='year-slider',
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
    dcc.Graph(id='plot', style={'height': '70vh', 'marginTop': '50px'}),
])


# Define the callback for updating the dropdown based on plot type
@callback(
    Output('country-dropdown', 'disabled'),
    Input('plot-type-dropdown', 'value')
)
def update_dropdown_disabled(plot_type):
    return plot_type != 'scatter'


# Define the callback for updating the slider based on plot type
@callback(
    Output('year-slider', 'disabled'),
    Input('plot-type-dropdown', 'value')
)
def update_slider_disabled(plot_type):
    return plot_type != 'choropleth'

@callback(
    Output('plot', 'figure'),
    [Input('plot-type-dropdown', 'value'),
     Input('country-dropdown', 'value'),
     Input('year-slider', 'value')]
)

def update_plot(plot_type, selected_countries, selected_year):
    # Ensure selected_countries is a list
    if not isinstance(selected_countries, list):
        selected_countries = [selected_countries]

    if plot_type == 'scatter':
        fig = go.Figure()

        for country in selected_countries:
            df_country = df_top_countries[df_top_countries['Entity'] == country]
            fig.add_trace(
                go.Scatter(x=df_country['Year'], y=df_country['Share of global annual CO₂ emissions'], mode='lines', name=country,
                                       ))

        fig.update_layout(
            title_text="Share of CO2 emissions (%) by countries over time",
            xaxis_title='Year',
            yaxis_title='Share of CO2 Emission (%)',
            hovermode='x unified',
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=2,
                             label="2y",
                             step="year",
                             stepmode="backward"),
                        dict(count=5,
                             label="5y",
                             step="year",
                             stepmode="backward"),
                        dict(count=10,
                             label="10y",
                             step="year",
                             stepmode="todate"),
                        dict(count=50,
                             label="50y",
                             step="year",
                             stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            )
        )
    else:  # plot_type == 'choropleth'
        df_year = df[df['Year'] == selected_year]
        df_top_countries_year = df_top_countries[df_top_countries['Year'] == selected_year]


        colorscale = [
            [0, '#FFFFE0'],  # Light Yellow
            [0.5, '#008000'],  # Green
            [1, '#00008B']  # Dark Blue
        ]
        fig = px.choropleth(
            df_top_countries_year,  
            locations='Code',  # column with ISO 3166-1 alpha-3 country codes
            color='Share of global annual CO₂ emissions',  # column with color values
            hover_name='Entity',  # column to add to hover information
            color_continuous_scale=colorscale,  # Change color scale
            range_color=(0, 20), 
            projection='natural earth',
            labels={'Share of global annual CO₂ emissions':'Percentage Share'},  # replaces default colorbar title
        )

        fig.update_layout(
            title_text='Global CO2 Emissions Share (%) in'  + ' ' + str(selected_year),
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='equirectangular'
            )
        )

    return fig