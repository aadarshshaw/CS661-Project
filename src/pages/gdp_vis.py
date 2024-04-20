import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, register_page, Input, Output, callback
import dash_mantine_components as dmc
from assets.constants import months
from pathlib import Path

register_page(
    __name__,
    "/gdp_vis",
    title="GDP Visualisation",
    description="Visualisation of GDP data and Correlation with C02 and Temperature",
)

emm_gdp = pd.read_excel(
    Path(__file__).parents[2]
    / "Datasets"
    / "GDP"
    / "Correlation - Emissions vs GDP.xlsx",
    sheet_name="Correlation-Country",
)
temp_gdp = pd.read_excel(
    Path(__file__).parents[2] / "Datasets" / "GDP" / "Correlation - GDP vs Temp.xlsx",
    sheet_name="Correlation-Method 2",
)

continents = emm_gdp["Continent"].unique()
continents = np.append(continents, "World")

highest_gdp_idx, lowest_gdp_idx = np.argmax(emm_gdp["Rho"]), np.argmin(emm_gdp["Rho"])
highest_gdp_country, lowest_gdp_country = (
    emm_gdp.iloc[highest_gdp_idx, :],
    emm_gdp.iloc[lowest_gdp_idx, :],
)

highest_temp_country, lowest_temp_country = (
    temp_gdp.iloc[np.argmax(temp_gdp["Rho"]), :],
    temp_gdp.iloc[np.argmin(temp_gdp["Rho"]), :],
)


def create_emm_gdp_graph(emm_gdp):
    fig = go.Figure(
        data=go.Choropleth(
            locations=emm_gdp["Country"],
            z=emm_gdp["Rho"],
            locationmode="country names",
            # text=countries,
            marker=dict(line=dict(color="rgb(0,0,0)", width=1)),
            colorscale="RdBu_r",
            zmin=-1,
            zmax=1,
        )
    )

    fig.update_layout(
        title="Correlation between CO2 emissions and GDP",
    )
    return fig


def create_gdp_temp_graph(temp_gdp):
    fig = go.Figure(
        data=go.Choropleth(
            locations=temp_gdp["Country"],
            z=temp_gdp["Rho"],
            locationmode="country names",
            # text=countries,
            marker=dict(line=dict(color="rgb(0,0,0)", width=1)),
            colorscale="RdBu",
            zmin=-1,
            zmax=1,
        )
    )

    fig.update_layout(
        title="Correlation between GDP and Temp",
    )

    return fig


def Tile(title, corr, country):
    return dmc.Card(
        radius="md",
        p="xl",
        withBorder=True,
        m=5,
        children=[
            dmc.Text(title, size="md"),
            dmc.Text(corr, size="xl", mt="md", weight="bold"),
            dmc.Text(country, size="sm", color="dimmed", mt="sm"),
        ],
    )


def create_select_continent():
    return dmc.Select(
        id="continent-select",
        data=[{"label": continent, "value": continent} for continent in continents],
        placeholder="Select a Continent",
        value=continents[-1],
    )


layout = html.Div(
    [
        dmc.Text("GDP Visualisation", align="center", style={"fontSize": 30}),
        dmc.Grid(
            children=[
                dmc.Col(
                    create_select_continent(),
                    span=12,
                ),
                dmc.Col(
                    dcc.Graph(
                        id="emm-gdp-graph",
                        figure=create_emm_gdp_graph(emm_gdp),
                    ),
                    span=12,
                ),
                dmc.Col(
                    Tile(
                        "Highest Correlation",
                        f"{highest_gdp_country['Rho']:.4f}",
                        highest_gdp_country["Country"],
                    ),
                    span=4,
                    id="highest-gdp-tile",
                ),
                dmc.Col(
                    Tile(
                        "Lowest Correlation",
                        f"{lowest_gdp_country['Rho']:.4f}",
                        lowest_gdp_country["Country"],
                    ),
                    span=4,
                    id="lowest-gdp-tile",
                ),
                dmc.Col(
                    Tile(
                        "Average Correlation", f"{emm_gdp['Rho'].mean():.4f}", "World"
                    ),
                    span=4,
                    id="average-gdp-tile",
                ),
                dmc.Col(
                    dcc.Graph(
                        id="gdp-temp-graph",
                        figure=create_gdp_temp_graph(temp_gdp),
                    ),
                    span=12,
                ),
                dmc.Col(
                    Tile(
                        "Highest Temp VS GDP Correlation",
                        f"{highest_temp_country['Rho']:.4f}",
                        highest_temp_country["Country"],
                    ),
                    span=4,
                    id="highest-temp-tile",
                ),
                dmc.Col(
                    Tile(
                        "Lowest Temp VS GDP Correlation",
                        f"{lowest_temp_country['Rho']:.4f}",
                        lowest_temp_country["Country"],
                    ),
                    span=4,
                    id="lowest-temp-tile",
                ),
                dmc.Col(
                    Tile(
                        "Average Correlation", f"{temp_gdp['Rho'].mean():.4f}", "World"
                    ),
                    span=4,
                    id="average-temp-tile",
                ),
            ],
        ),
    ]
)


@callback(
    [
        Output("emm-gdp-graph", "figure"),
        Output("gdp-temp-graph", "figure"),
        Output("highest-gdp-tile", "children"),
        Output("lowest-gdp-tile", "children"),
        Output("average-gdp-tile", "children"),
        Output("highest-temp-tile", "children"),
        Output("lowest-temp-tile", "children"),
        Output("average-temp-tile", "children"),
    ],
    [Input("continent-select", "value")],
)
def update_graphs(continent):
    if continent == "World":
        emm_gdp_filtered = emm_gdp
        temp_gdp_filtered = temp_gdp
    else:
        emm_gdp_filtered = emm_gdp[emm_gdp["Continent"] == continent]
        temp_gdp_filtered = temp_gdp[temp_gdp["Continent"] == continent]

    emm_gdp_fig = create_emm_gdp_graph(emm_gdp_filtered)
    gdp_temp_fig = create_gdp_temp_graph(temp_gdp_filtered)

    highest_gdp_country, lowest_gdp_country = (
        emm_gdp_filtered.iloc[np.argmax(emm_gdp_filtered["Rho"]), :],
        emm_gdp_filtered.iloc[np.argmin(emm_gdp_filtered["Rho"]), :],
    )

    highest_temp_country, lowest_temp_country = (
        temp_gdp_filtered.iloc[np.argmax(temp_gdp_filtered["Rho"]), :],
        temp_gdp_filtered.iloc[np.argmin(temp_gdp_filtered["Rho"]), :],
    )

    highest_gdp_tile = Tile(
        "Highest Correlation",
        f"{highest_gdp_country['Rho']:.4f}",
        highest_gdp_country["Country"],
    )

    lowest_gdp_tile = Tile(
        "Lowest Correlation",
        f"{lowest_gdp_country['Rho']:.4f}",
        lowest_gdp_country["Country"],
    )

    average_gdp_tile = Tile(
        "Average Correlation", f"{emm_gdp_filtered['Rho'].mean():.4f}", continent
    )

    highest_temp_tile = Tile(
        "Highest Temp VS GDP Correlation",
        f"{highest_temp_country['Rho']:.4f}",
        highest_temp_country["Country"],
    )

    lowest_temp_tile = Tile(
        "Lowest Temp VS GDP Correlation",
        f"{lowest_temp_country['Rho']:.4f}",
        lowest_temp_country["Country"],
    )

    average_temp_tile = Tile(
        "Average Correlation", f"{temp_gdp_filtered['Rho'].mean():.4f}", continent
    )

    return (
        emm_gdp_fig,
        gdp_temp_fig,
        highest_gdp_tile,
        lowest_gdp_tile,
        average_gdp_tile,
        highest_temp_tile,
        lowest_temp_tile,
        average_temp_tile,
    )
