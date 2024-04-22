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

co2 = pd.read_csv(
    Path(__file__).parents[2]
    / "Datasets"
    / "Correlation Data"
    / "correlation - co2 vs population.csv"
)
temp = pd.read_csv(
    Path(__file__).parents[2]
    / "Datasets"
    / "Correlation Data"
    / "correlation_temperature.csv"
)


@callback(Output("heatmap-graph", "figure"), [Input("heatmap-graph", "hoverData")])
def update_map(hoverData):
    return updateco2_heatmap(hoverData)


def updateco2_heatmap(hoverData):
    fig = px.choropleth(
        co2,
        locations="Country",
        locationmode="country names",
        color="Correlation",
        color_continuous_scale="RdBu_r",
        range_color=(-1, 1),
        title="Correlation World Heatmap for Population vs CO2",
        labels={"Correlation": "Correlation"},
    )

    # Customize the map layout
    fig.update_layout(geo=dict(showcoastlines=True, projection_type="equirectangular"))

    # Add hover information
    if hoverData is not None:
        country_name = hoverData["points"][0]["location"]
        correlation_value = hoverData["points"][0]["z"]
        fig.update_traces(hoverinfo="location+z", hoverlabel=dict(namelength=0))

    return fig


def updatetemp_heatmap(hoverData):
    fig = px.choropleth(
        temp,
        locations="Country",
        locationmode="country names",
        color="Correlation",
        color_continuous_scale="RdBu_r",
        range_color=(-1, 1),
        title="Correlation World Heatmap for Population vs Temperature",
        labels={"Correlation": "Correlation"},
    )

    # Customize the map layout
    fig.update_layout(geo=dict(showcoastlines=True, projection_type="equirectangular"))

    # Add hover information
    if hoverData is not None:
        country_name = hoverData["points"][0]["location"]
        correlation_value = hoverData["points"][0]["z"]
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
                    children="The majority of countries exhibit positive correlations between CO2 emissions and population growth. This suggests that as population grows, there tends to be an increase in CO2 emissions, likely due to higher energy consumption, industrial activities, and transportation demands associated with larger populations.",
                    style={"textAlign": "left"},
                ),
                html.P(
                    "While positive correlations are widespread, the strength of the correlation varies across regions. Some regions, like Eastern Europe and parts of Asia, demonstrate stronger positive correlations between CO2 emissions and population growth, indicating potentially higher levels of industrialization and urbanization in these areas."
                ),
                html.P(
                    "While the general trend is positive, there are exceptions. Some countries, like Afghanistan and parts of Africa, show negative correlations. This could be due to factors such as lower industrialization levels, reliance on renewable energy sources, or other socio-economic factors influencing CO2 emissions independently of population growth. Understanding the nuances of these exceptions can provide valuable insights into effective climate and population policies."
                ),
                dmc.Col(
                    dcc.Graph(
                        id="Percentage-CO2-Countries",
                        figure=updatetemp_heatmap(None),
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
                    " While negative correlations are predominant, there are notable exceptions. Some countries, like Luxembourg and Sweden, show positive correlations between temperature and population growth. This could be due to various factors such as robust economies, social policies, or geographic advantages that mitigate the adverse effects of temperature on population growth. Understanding the unique circumstances of these outliers can provide valuable insights into the complex relationship between temperature and population dynamics"
                ),
            ],
        ),
    ]
)
