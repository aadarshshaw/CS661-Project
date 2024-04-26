import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, register_page, Input, Output, callback
import dash_mantine_components as dmc
from assets.constants import months
from pathlib import Path
import math
import plotly.express as px

register_page(
    __name__,
    "/climate_change_indicators",
    title="Climate Change Indicators",
    description="Climate Change Indicators",
)


population = pd.read_csv("Datasets/population_and_co2/population_and_co2.csv")

all_gases = pd.read_csv("Datasets/population_and_co2/all_greenhouse_gases.csv")

all_gases_countrywise = pd.read_csv("Datasets/population_and_co2/cleaned_dataset .csv")




population["Density (P/Km²)"] = population["Density (P/Km²)"].apply(
    lambda x: math.log2(x + 1)
)


def create_population_graph():
    fig = px.scatter(
        population,
        x="Annual CO₂ emissions",
        y="Population (2020)",
        size="Land Area (Km²)",
        color="Density (P/Km²)",
        color_continuous_scale="Temps",
        hover_name="Entity",
        hover_data=["Entity", "Annual CO₂ emissions"],
        labels={
            "Entity": "Country",
            "Annual CO₂ emissions": "CO₂ Emission",
            "Population (2020)": "Population",
            "Density (P/Km²)": "Density (P/Km²)",
        },
        log_x=True,
        log_y=True,
        size_max=40,
    )

    # Update the title and adjust its location
    fig.update_layout(title="Population vs CO2 Emission, 2020", title_x=0.5)

    # Show the figure
    return fig

layout = html.Div(
    [
        html.H1(
            "Climate Change Indicators: Global Greenhouse Gas Emissions since 1990"
        ),
        
        dmc.Space(h="xl"),
        dmc.Grid(
            [
                dmc.Col(
                    [
                        dmc.Text("Select Country:"),
                    ],
                    span=3,
                ),
                dmc.Col(
                    [
                        dmc.Select(
                            id="country-dropdown",
                            data=[
                                {"label": i, "value": i}
                                for i in all_gases_countrywise["country"].unique()
                            ],
                            value = "World",
                        ),
                    ],
                    span=9,
                ),
            ],
        ),
        dmc.Space(h="xl"),
        dcc.Graph(id="greenhouse-gases-graph"),
        html.P(
            "This figure shows worldwide emissions of carbon dioxide, methane, nitrous oxide, and several fluorinated gases from 1990 to 2022."
        ),
        html.P(
            "From graph, it can be observed tht between 1990 and 2022, global emissions of all major greenhouse gases increased. Net emissions of carbon dioxide increased by 51 percent, which is particularly important because carbon dioxide accounts for about three-fourths of total global emissions. Methane emissions increased the least (17 percent) , while emissions of nitrous oxide increased by 24 percent. Emissions of fluorinated gases more than tripled. Hence, in our further analysis we have majorly focused on the CO2 emissions worldwide."
        ),
        # html.H1("Population vs CO2 Emission, 2020"),
        # html.P(
        #     "Lets see how the total CO2 emission of a country correlates to its population"
        # ),
        # dcc.Graph(
        #     id="population-co2-graph",
        #     figure=create_population_graph(),
        # ),
        # html.P(
        #     "In the above bubble chart,direct correlation between the population and the CO2 emission of the countries can be clearly observed: as population increases, CO2 emission increases as well."
        # ),
        # html.P(
        #     "Another dimension that can be easily observed from the bubble chart is the size of the bubbles, which represents the land area of every country. Moreover, color functionality allows us to see another dimension in the same chart: the density of every country. Again, not to see the correlation, but just to observe the country density along with all other features in just one visual."
        # ),
    ]
)

@callback(
    Output("greenhouse-gases-graph", "figure"),
    Input("country-dropdown", "value"),
)

def update_greenhouse_gases_graph(selected_country):

    country_data = all_gases_countrywise[
            all_gases_countrywise["country"] == selected_country
    ]
    # Create traces for each gas
    traces = []
    colors = ["rgba(0, 0, 255)", "rgba(0, 255, 255)", "rgba(255, 0, 0)"]
    for gas, color in zip(["total_co2", "methane", "nitrous_oxide"], colors):
        trace = go.Bar(
            x=country_data["year"], y=country_data[gas], name=gas, marker=dict(color=color)
        )
        traces.append(trace)

    # Create layout
    layout = go.Layout(
        title="Annual Gas Emissions" + " in " + selected_country,
        xaxis=dict(title="Year"),
        yaxis=dict(
            title="Emissions (million tonnes)"
        ),  # Replace with appropriate units
        barmode="group",
    )

    # Create figure
    fig = go.Figure(data=traces, layout=layout)

    return fig



