import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, register_page, Input, Output, callback
import dash_mantine_components as dmc
from assets.constants import months
from pathlib import Path

from util.content import create_Text

register_page(
    __name__,
    "/co2_vis",
    title="CO2 Emissions Visualisation",
    description="Visualisation of CO2 emission throughout the World",
)

df_filtered = pd.read_csv(
    Path(__file__).parents[2]
    / "Datasets"
    / "CO2_Emissions"
    / "CO2_emission_by_countries.csv"
)
df = pd.read_csv(
    Path(__file__).parents[2]
    / "Datasets"
    / "CO2_Emissions"
    / "co-emissions-per-capita.csv"
)


@callback(
    Output("map-graph", "figure"),
    Output("mini-graph-container", "figure"),
    Input("map-graph", "hoverData"),
)
def update_map(hoverData):
    return world_CO2_map(hoverData)


def world_CO2_map(hoverData):
    # Step 2: Filter data for year 2022
    df_2022 = df[
        df["Year"] == 2022
    ].copy()  # Make a copy to avoid SettingWithCopyWarning

    # Round the "Annual CO₂ Emissions per Capita (2022)" to 1 decimal place using .loc indexer
    df_2022.loc[:, "Annual CO₂ emissions (per capita)"] = df_2022[
        "Annual CO₂ emissions (per capita)"
    ].round(1)
    fig = px.choropleth(
        df_2022,
        locations="Entity",
        locationmode="country names",
        color="Annual CO₂ emissions (per capita)",
        projection="natural earth",
        hover_name="Entity",
        hover_data={
            "Entity": False,
            "Annual CO₂ emissions (per capita)": True,
        },  # Remove "Entity" from hover info
        title="Annual CO₂ Emissions per Capita (2022) (in tonnes per person)",
        color_continuous_scale=px.colors.sequential.YlOrBr,  # Change color scale
        range_color=(0, 20),  # Set color range from 0 to 20t
    )
    mini_fig = go.Figure()
    if hoverData is not None and "points" in hoverData:
        # Extract country name from hoverData
        country_name = hoverData["points"][0]["hovertext"]

        # Step 4: Implement hover functionality
        country_df = df[df["Entity"] == country_name]
        mini_graph = go.Scatter(
            x=country_df["Year"],
            y=country_df["Annual CO₂ emissions (per capita)"],
            mode="lines+markers",
            name="CO₂ emissions trend",
            marker=dict(size=1),
        )
        mini_fig.add_trace(mini_graph)
        mini_fig.update_layout(
            plot_bgcolor="rgba(0, 0, 0, 0)",
            paper_bgcolor="rgba(0, 0, 0, 0)",
            title="CO₂ emissions (per capita) trend - " + country_name,
            xaxis_title="Year",
            yaxis_title="Per Capita CO₂ emissions ",
        )
    else:
        country_name = "India"
        country_df = df[df["Entity"] == country_name]
        mini_graph = go.Scatter(
            x=country_df["Year"],
            y=country_df["Annual CO₂ emissions (per capita)"],
            mode="lines+markers",
            name="CO₂ emissions trend",
            marker=dict(size=1),
        )
        mini_fig.add_trace(mini_graph)
        mini_fig.update_layout(
            plot_bgcolor="rgba(0, 0, 0, 0)",
            paper_bgcolor="rgba(0, 0, 0, 0)",
            title="CO₂ emissions (per capita) trend - " + country_name,
            xaxis_title="Year",
            yaxis_title="Per Capita CO₂ emissions ",
        )

    return fig, mini_fig


def Countries_emitting_most_CO2():
    global df_filtered
    # Group the data by country and calculate the total CO2 emissions for each country
    total_emissions = df_filtered.groupby("Entity")["Annual CO2"].sum().reset_index()

    # Sort countries by total emissions and select the top 8
    top_emitters = total_emissions.nlargest(8, "Annual CO2")["Entity"]
    # Filter the data to include only the top 8 emitters
    df_filtered = df_filtered[df_filtered["Entity"].isin(top_emitters)]

    # Create a Plotly graph
    fig1 = go.Figure()

    # Iterate over each country to plot
    for country in total_emissions["Entity"]:
        country_data = df_filtered[df_filtered["Entity"] == country]
        fig1.add_trace(
            go.Scatter(
                x=country_data["Year"],
                y=country_data["Annual CO2"],
                mode="lines",
                name=country,
            )
        )

    # Update layout
    fig1.update_layout(
        title="Annual CO2 Emission by top 8 countries",
        xaxis_title="Year",
        yaxis_title="Annual CO2 emission",
        hovermode="x unified",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )

    # Show the interactive plot
    return fig1


def Percentage_Share_of_CO2_per_country():
    global df_filtered

    # Group the data by year and calculate the total CO2 emissions for each year
    total_emissions_yearly = df_filtered.groupby("Year")["Annual CO2"].sum()

    # Group the data by country and calculate the total CO2 emissions for each country
    total_emissions_country = df_filtered.groupby("Entity")["Annual CO2"].sum()

    # Sort countries by total emissions and select the top 8
    top_emitters = total_emissions_country.nlargest(8).index

    # Create a Plotly graph
    fig = go.Figure()

    # Iterate over each country to plot
    for country in top_emitters:
        # Calculate the share of CO2 emissions for each country
        share = (
            df_filtered[df_filtered["Entity"] == country]
            .groupby("Year")["Annual CO2"]
            .sum()
            / total_emissions_yearly
        ) * 100
        fig.add_trace(go.Scatter(x=share.index, y=share, mode="lines", name=country))

    # Update layout
    fig.update_layout(
        title="Share of CO2 Emissions by Top 8 Countries",
        xaxis_title="Year",
        yaxis_title="Share of CO2 Emissions (%)",
        hovermode="x unified",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )

    # Show the interactive plot
    return fig


def World_CO2_emission():
    global df_filtered

    # Group the data by year and calculate the total CO2 emissions for each year
    total_world_emissions = (
        df_filtered.groupby("Year")["Annual CO2"].sum().reset_index()
    )

    # Create a Plotly graph
    fig1 = go.Figure()

    # Plot total world emissions
    fig1.add_trace(
        go.Scatter(
            x=total_world_emissions["Year"],
            y=total_world_emissions["Annual CO2"],
            mode="lines",
            name="World",
            line=dict(color="black"),
        )
    )

    # Update layout
    fig1.update_layout(
        title="Annual CO2 Emission by World",
        xaxis_title="Year",
        yaxis_title="Annual CO2 emission",
        hovermode="x unified",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )

    # Show the interactive plot
    return fig1


layout = html.Div(
    [
        dmc.Text("CO2 Visualization", align="center", style={"fontSize": 30}),
        dmc.Text(
            """When examining carbon dioxide (CO2) emissions, a crucial metric is per capita emissions, which signifies the average amount of CO2 emitted by an individual in a given country each year. By dividing a country's total emissions by its population, we derive this insightful statistic. By analyzing per capita emissions globally, we gain insight into the relative environmental impact of individuals across different regions.
It's essential to note that these figures are based on production-based emissions, meaning they account for emissions generated within a country's borders without considering the impact of international trade. These production-based metrics are fundamental for climate policy and have been meticulously tracked since the mid-18th century, providing historical context to global emission trends.
""",
            size="sm",
        ),
        dmc.Grid(
            children=[
                dmc.Col(
                    [
                        dcc.Graph(id="map-graph", figure=world_CO2_map(None)[0]),
                    ],
                    span=12,
                ),
                dmc.Col(
                    [
                        dcc.Graph(
                            id="mini-graph-container", figure=world_CO2_map(None)[1]
                        )
                    ],
                    span=12,
                ),
                create_Text(
                    "Insights that can be drawn from CO2 emission trend (Regionwise) Chart:"
                ),
                create_Text(
                    "Temporal patterns: Graph reveals emissions patterns over 100+ years."
                ),
                create_Text(
                    "Historical Context: Offers historical backdrop to emissions evolution."
                ),
                create_Text(
                    "Comparative Analysis: Enables comparison between regions' emission trajectories."
                ),
                create_Text(
                    "Policy Relevance: Informs climate policies and intervention strategies."
                ),
                create_Text(
                    "Environmental Footprint: Highlights region's contribution to global emissions."
                ),
                dmc.Col(
                    dcc.Graph(
                        id="CO2-emm-top-countries",
                        figure=Countries_emitting_most_CO2(),
                    ),
                    span=12,
                ),
                dmc.Col(
                    dcc.Graph(
                        id="Percentage-CO2-Countries",
                        figure=Percentage_Share_of_CO2_per_country(),
                    ),
                    span=12,
                ),
                dmc.Col(
                    dcc.Graph(
                        id="World-CO2-emm",
                        figure=World_CO2_emission(),
                    ),
                    span=12,
                ),
            ],
        ),
    ]
)
