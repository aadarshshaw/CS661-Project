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
    html.H1(children='Annual CO2 Emission', style={'textAlign': 'center'}),
    html.P(children='Who emits the most CO2 each year? In the following visualization, we show annual CO2 emissions aggregated by countries and region, with a special focus on the leading emitters including India, China, and the United States.', style={'textAlign': 'left'}),
    html.P('We can explore how CO2 emissions change by country and over time in the following interactive map. By selecting any country from the dropdown list, you can see how its annual emissions have changed, and compare it with other countries.'),
    html.Div(children='''Select Countries for comparative analysis''', style={'textAlign': 'center'}),
    html.Div([
    dcc.Dropdown(
        id='country-selector',
        options=[{'label': i, 'value': i} for i in available_countries],
        value=['United States','India','China','Africa','South America','North America(excl. USA)'],
        multi=True,
        style={
            'width': '80%', 
            'margin': 'auto', 
            'fontFamily': 'Arial',  # Use a professional font
            'padding': '10px'  # Add padding
        }
    )
]),
    dcc.RadioItems(
        id='view-selector',
        options=[{'label': i, 'value': i} for i in ['Chart View', 'Map View']],
        value='Map View',
        style={
            'textAlign': 'center', 
            'fontFamily': 'Arial',  # Use a professional font
            'padding': '10px'  # Add padding
        }
    ),
    html.Div(id='view-container', style={
        'border': '1px solid #ddd',  # Use a more subtle border style
        'width': '90%',
        'height': '500px',
        'margin': 'auto',
        'fontFamily': 'Arial',  # Use a professional font
        'padding': '5px'  # Add padding
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
        yaxis_title="CO2 Emissions (in tons)"
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
                        color_continuous_scale=px.colors.diverging.Spectral_r,  # Use a sequential color scale
                        range_color=(0, percentile_98 ),  # Set the color range to include the 60th percentile of the data
                        projection='natural earth', title='CO2 Emissions by Country Over Time')

    
    # Map chart background color
    fig.update_geos(bgcolor='#F0F2F3', showcountries=True, showcoastlines=True, showland=True, landcolor="lightgray")

    # Add zoom control
    fig.update_layout(
        geo=dict(
            showframe=True,
            showcoastlines=False,
            projection_type='equirectangular'
        ),
        autosize=False,  # Set autosize to False
        width=985,  # Set the width of the figure
        height=485,  # Set the height of the figure
        margin=dict(autoexpand=True, l=0, r=0, t=0, b=0),
        dragmode='pan'
    )

    return fig


import pycountry
layout.children.append(html.Div([
    html.P('Asia is by far the largest emitter, accounting for around half of global emissions. As it is home to almost 60% of the world’s population this means that per capita emissions in Asia are slightly lower than the world average, however.'),
    html.P("China is, by a significant margin, Asia's and the world's largest emitter: it emits more than one-quarter of global emissions."),
    html.P('North America, dominated by the USA, is the second largest regional emitter at one-fourth of global emissions and it’s followed closely by Europe. Here we have grouped the countries in the European Union since they typically negotiate and set targets as a collective body. You can see the data for individual EU countries in the interactive maps that follow.'),
    html.P('Africa and South America are both fairly small emitters: accounting for 3-4% of global emissions each. Both have emissions similar in size to international aviation and shipping combined.')
]))
import pycountry
# Get a list of all country names
country_names = [country.name for country in pycountry.countries]

# Filter the DataFrame to only include rows where 'Entity' is a valid country name
df = df_flat[df_flat['Entity'].isin(country_names)]
# Assuming 'df' is your DataFrame containing the data
# Filter the data for the years 2010 to 2022
filtered_data = df[(df['Year'] >= 2000) & (df['Year'] <= 2022)]

# Calculate total emissions for each country
total_emissions = filtered_data.groupby('Entity')['Annual CO₂ emissions'].sum()

# Sort the DataFrame by total emissions and select the top 20 countries
total_emissions_sorted = total_emissions.sort_values(ascending=False).iloc[:20]

# Create a DataFrame with the top 20 countries and their total emissions
top_20_df = pd.DataFrame({'Country': total_emissions_sorted.index, 'Total Emissions': total_emissions_sorted.values})

# Create a bar plot
# Create a bar plot with a different color scale
fig = px.bar(top_20_df,
             x='Country',
             y='Total Emissions',
             color='Total Emissions',
             hover_name='Country',
             hover_data=['Total Emissions'],
             color_continuous_scale='tealgrn',  # Change the color scale here
             labels={'Country': 'Country', 'Total Emissions': 'Total CO₂ Emission (in tonnes)'},
             height=500)

# Add text before the graph
# Add text before the graph
layout.children.append(html.P(children='Now, let\'s delve into the analysis of Total CO₂ Emissions between the years 2010 and 2022, focusing on the Top 20 Countries.'))
fig.update_layout(uniformtext_minsize=15,
                  xaxis_tickangle=-45,
                  title='Total CO₂ Emission Between Years 2010 and 2022 - Top 20 Countries',
                  title_x=0.5,
                  font=dict(  # Change the text color here
                      color="white"
                  ))

# Make background transparent
fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})

# Hide color scale axis
fig.update(layout_coloraxis_showscale=False)

# Add the graph to the layout
layout.children.append(dcc.Graph(id='bar-graph', figure=fig, style={'height': '600px', 'width': '1000px'}))

layout.children.append(html.P(children='Now observe the CO2 emission of different regions.'))

######


df_path_region = (
    Path(__file__).parents[2]
    / "Datasets"
    / "annual_co2_emissions_by_region"
    / "annual-co-emissions-by-region.csv"
)

df_dash_region = pd.read_csv(df_path_region)
# Get a list of all unique regions
regions = df_dash_region['Entity'].unique()
layout.children.append(html.Div([
    dcc.Dropdown(
        id='region-dropdown',
        options=[{'label': i, 'value': i} for i in regions],
        value=['United States','Europe','Asia','Africa','Oceania'],
        multi=True
    ),
    dcc.Graph(id='region-graph')
]))

# Group the data frame by Entity and Year columns and sum the CO2 emission
total_reg = df_dash_region.groupby(["Entity", "Year"])["Annual CO₂ emissions by region"].sum()

# Create a data frame from the resulting series
df_reg = pd.DataFrame(total_reg)

# Resulting data frame will have 2 index columns: Entity and Year
# We should reset the index to convert them into columns
df_reg.reset_index(level=0, inplace=True)
df_reg.reset_index(level=0, inplace=True)

@callback(
    Output('region-graph', 'figure'),
    [Input('region-dropdown', 'value')]
)
def update_graph(selected_regions):
    df_selected = df_reg[df_reg['Entity'].isin(selected_regions)]
    
    fig = px.area(df_selected,
                  x="Year",
                  y="Annual CO₂ emissions by region",
                  color="Entity",
                  facet_col="Entity",  # Add this line
                  labels={'Entity':'Region','Annual CO₂ emissions by region':'CO₂ Emission'},
                  height=350)

    fig.update_layout(title="Change in CO₂ Emission Between Years 1750 and 2020 - Regions",
                      title_x=0.50)
    
    return fig

# #######
layout.children.append(html.P(children='From the above graph, we can observe although Europe and United States are the regions having most of the CO2 emission in total, Asia\'s CO2 emission has skyrocketed in the last 2 decades.'))
# # Group the data frame by Entity and sum the CO2 emission
# total_r = df_dash_region.groupby(['Entity'])["Annual CO₂ emissions by region"].sum()

# # Create a data frame from the resulting series
# df_total_r = pd.DataFrame(total_r)

# # Sort the dataframe
# df_total_r = df_total_r.sort_values('Annual CO₂ emissions by region', ascending = False)

# # Reset the index to convert Entity into a column
# df_total_r.reset_index(level=0, inplace=True)

# # Plot the bar chart
# fig = px.bar(df_total_r,
#               x = 'Entity',
#               y = 'Annual CO₂ emissions by region',
#               color='Annual CO₂ emissions by region',
#               hover_name = 'Entity',
#               hover_data = ['Annual CO₂ emissions by region'],
#               color_continuous_scale = 'Peach',
#               labels={'Entity':'Country','Annual CO₂ emissions by region':'Total CO₂ Emission'},
#               height=500)

# # Adjust text label size & angle and the title
# fig.update_layout(uniformtext_minsize = 15,
#                   xaxis_tickangle = -45,
#                   title = 'Total CO₂ Emission Between Years 1750 and 2022 - Countries',
#                   title_x = 0.5)

# # Make background transparent
# fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
#                    'paper_bgcolor': 'rgba(0, 0, 0, 0)'})

# # Show color scale axis
# fig.update(layout_coloraxis_showscale = True)
# # Add the graph to the layout
# layout.children.append(dcc.Graph(id='bar-graph', figure=fig, style={'height': '600px', 'width': '1000px'}))
