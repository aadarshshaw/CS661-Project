import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, register_page, Input, Output, callback
import dash_mantine_components as dmc
from assets.constants import months
from pathlib import Path

register_page(
    __name__,
    "/population_vis",
    title="Population Growth Visualisation",
    description="Visualisation of Population throughout the World",
)

co2= pd.read_csv(Path(__file__).parents[2] 
                         / "Datasets" / "Correlation Data" / "correlation - co2 vs population.csv")
temp = pd.read_csv(Path(__file__).parents[2] 
                         / "Datasets" / "Correlation Data" / "correlation_temperature.csv")



@callback(
    Output('heatmap-graph', 'figure'),
    [Input('heatmap-graph', 'hoverData')]
)

def update_map(hoverData):
    return updateco2_heatmap(hoverData)


def updateco2_heatmap(hoverData):
    fig = px.choropleth(
        co2,
        locations='Country',
        locationmode='country names',
        color='Correlation',
        color_continuous_scale='RdBu_r',
        range_color=(-1, 1),
        title='Correlation World Heatmap for Population vs CO2',
        labels={'Correlation': 'Correlation'}
    )

    # Customize the map layout
    fig.update_layout(
        geo=dict(
            showcoastlines=True,
            projection_type='equirectangular'
        )
    )

    # Add hover information
    if hoverData is not None:
        country_name = hoverData['points'][0]['location']
        correlation_value = hoverData['points'][0]['z']
        fig.update_traces(hoverinfo="location+z", hoverlabel=dict(namelength=0))
    
    return fig

def updatetemp_heatmap(hoverData):
    fig = px.choropleth(
        temp,
        locations='Country',
        locationmode='country names',
        color='Correlation',
        color_continuous_scale='RdBu_r',
        range_color=(-1, 1),
        title='Correlation World Heatmap for Population vs Temperature',
        labels={'Correlation': 'Correlation'}
    )

    # Customize the map layout
    fig.update_layout(
        geo=dict(
            showcoastlines=True,
            projection_type='equirectangular'
        )
    )

    # Add hover information
    if hoverData is not None:
        country_name = hoverData['points'][0]['location']
        correlation_value = hoverData['points'][0]['z']
        fig.update_traces(hoverinfo="location+z", hoverlabel=dict(namelength=0))
    
    return fig


layout = html.Div(
    [
        dmc.Text("Population Visualization", align="center", style={"fontSize": 30}),
        dmc.Grid(
            children=[
                
                dmc.Col(
                    dcc.Graph(
                        id="CO2-emm-top-countries",
                        figure=updateco2_heatmap(None),
                    ),
                    span=12,
                ),
                html.P(
                children="The majority of countries exhibit negative correlations between temperature and population growth. This suggests that, in these countries, as temperatures increase, population growth tends to decrease. This trend could be attributed to factors such as increased heat stress, reduced agricultural productivity, and limited resources in warmer climates.",
                style={"textAlign": "left"},
                ),
                html.P(
                "Countries in certain regions, such as Central America and parts of Africa, demonstrate particularly strong negative correlations between temperature and population growth. This could indicate that these regions are more sensitive to temperature changes, possibly due to higher vulnerability to climate-related challenges like droughts, which can impact food security and economic stability, thereby influencing population growth."
                ),
                html.P(
                "While negative correlations are predominant, there are notable exceptions. Some countries, like Luxembourg and Sweden, show positive correlations between temperature and population growth"
                ),
                dmc.Col(
                    dcc.Graph(
                        id="Percentage-CO2-Countries",
                        figure=updatetemp_heatmap(None),
                    ),
                    span=12,
                ),
                 html.P(
                children="The majority of countries show positive correlations between temperature and population growth. This suggests that, in these countries, as temperatures rise, population growth tends to increase. This could be due to factors like improved living conditions in warmer climates or better adaptation to temperature changes.",
                style={"textAlign": "left"},
                ),
                html.P(
                "Some regions, such as Eastern Europe and parts of Asia, exhibit particularly strong positive correlations between temperature and population growth. This may indicate specific regional factors influencing population dynamics, such as economic development, social policies, or environmental conditions."
                ),
                html.P(
                "While positive correlations are predominant, there are exceptions. Some countries show negative or weak correlations, indicating diverse factors at play in different contexts. Understanding the reasons behind these exceptions can provide valuable insights into the complex relationship between temperature and population dynamics."
                )
                
            ],
        ),
    ]
)

