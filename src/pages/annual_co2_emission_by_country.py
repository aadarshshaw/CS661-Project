import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, register_page, Input, Output, callback
import dash_mantine_components as dmc
from assets.constants import months
from pathlib import Path
import plotly.express as px

register_page(
    __name__,
    "/annual_co2_emission",
    title="Climate Change Visualisation",
    description="Climate Change Visualisation",
)

df_path = (
    Path(__file__).parents[2]
    / "Datasets"
    / "annual_co2_emissions_by_country"
    / "annual-co2-emissions-per-country.csv"
)

df_dash = pd.read_csv(df_path)

# Drop rows with missing values in the 'Entity' column
df_dash = df_dash.dropna(axis=0, subset=['Entity'])

# Create a figure for the bar chart of top 5 CO2-emitting countries in 2016
CO2_df2020 = df_dash.loc[df_dash['Year'] == 2016]
top5 = CO2_df2020.sort_values(by=['Annual CO₂ emissions'], ascending=False).head(5)
bar_fig = px.bar(top5.sort_values(by=['Annual CO₂ emissions']), x='Entity', y='Annual CO₂ emissions',
                 labels={'value': 'CO2 emissions (kt)'}, title='CO2 emissions (kt) - Top 5 nations in Year 2016')
bar_fig.update_xaxes(fixedrange=True)

# Load flat dataframe for dropdown options
df_flat = pd.read_csv(df_path)
available_countries = df_flat['Entity'].unique()
# Define the slider

# Define the layout of the dashboard
layout = html.Div(children=[
    html.H1(children='CO2 Emission by Country', style={'textAlign': 'center'}),
    html.Div(children='''Select Countries for comparative analysis''', style={'textAlign': 'center'}),
    html.Div([
        dcc.Dropdown(
            id='country-selector',
            options=[{'label': i, 'value': i} for i in available_countries],
            value=['United States','India','China','Africa','South America','North America(excl. USA)'],  # Default selected countries
            multi=True,  # Allow multiple selection
            style={'width': '80%', 'margin': 'auto'}  # Adjust width and center dropdown
        )
    ]),
    dcc.RadioItems(
        id='view-selector',
        options=[{'label': i, 'value': i} for i in ['Chart View', 'Map View']],
        value='Map View',  # Default view
        style={'textAlign': 'center'}
    ),
    html.Div(id='view-container', style={  # Add styles to this div
        'border': '2px solid black',  # Border style
        'width': '90%',  # Width of the div
        'height': '600px',  # Height of the div
        'margin': 'auto'  # Center the div
    }) 
])

@callback(
    Output('view-container', 'children'),
    Input('view-selector', 'value'),
    Input('country-selector', 'value')
)
def update_view(selected_view, selected_countries):
    # Define the slider
    # Calculate the step size
    step_size = (2022 - 1800) // 10

# Create a dictionary of labels
    marks = {i: str(i) for i in range(1800, 2022, step_size)}

    if selected_view == 'Chart View':
        # Generate the chart figure based on the selected countries
        chart_fig = update_graph(selected_countries)
        return dcc.Graph(id='co2-time-series', figure=chart_fig)
    else:
        # Generate the map figure based on the selected countries
        map_fig = update_choropleth(selected_countries)
        return [dcc.Graph(id='choropleth-map', figure=map_fig)]


# Define callback function to update the graph based on dropdown selection
@callback(
    Output('co2-time-series', 'figure'),
    Input('country-selector', 'value')
)
def update_graph(selected_countries):
    # Filter dataframe based on selected countries
    filtered_df = df_dash[df_dash['Entity'].isin(selected_countries)]

    # Plot multiple time series
    fig = go.Figure()

    for country in selected_countries:
        country_data = filtered_df[filtered_df['Entity'] == country]
        fig.add_trace(go.Scatter(x=country_data['Year'], y=country_data['Annual CO₂ emissions'], mode='lines', name=country))

    fig.update_layout(
        title="CO2 Emissions Over Time",
        xaxis_title="Year",
        yaxis_title="CO2 Emissions (kt)"
    )

    return fig


# Define callback function to update choropleth map
@callback(
    Output('choropleth-map', 'figure'),
    Input('country-selector', 'value')
)

def update_choropleth(selected_countries=None):


    filtered_df_dash = df_dash.sort_values('Year')
    # If no countries are selected, select all
    if not selected_countries:
        selected_countries = filtered_df_dash['Entity'].unique()

    # Filter dataframe based on selected countries
    filtered_df = filtered_df_dash[df_dash['Entity'].isin(selected_countries)]
    
    # Sort the data frame by 'Year'
    
    # Calculate the 98th percentile of the data
    percentile_98 = np.percentile(filtered_df['Annual CO₂ emissions'], 98)

    # Calculate the minimum and maximum of the data
    min_emissions = filtered_df['Annual CO₂ emissions'].min()
    max_emissions = filtered_df['Annual CO₂ emissions'].max()

    # Create choropleth map
    fig = px.choropleth(filtered_df, locations='Code', color='Annual CO₂ emissions',
                        hover_name='Entity', animation_frame='Year',
                        color_continuous_scale=px.colors.sequential.Plasma_r,  # Use a sequential color scale
                        range_color=(0, percentile_98 ),  # Set the color range to include the 60th percentile of the data
                        projection='natural earth', title='CO2 Emissions by Country Over Time')

    
    # Map chart background color
    fig.update_geos(bgcolor='#F0F2F3', showcountries=True, showcoastlines=True, showland=True, landcolor="lightgray")

    # Add zoom control
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
        ),
        autosize=True,
        margin=dict(autoexpand=True, l=0, r=0, t=0, b=0),
        dragmode='pan'
    )

    return fig




