import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, register_page, Input, Output, callback
import dash_mantine_components as dmc
from assets.constants import months
from pathlib import Path

from util.content import create_Text

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

    fig.update_geos(
        showframe=False,
        showcoastlines=False,
        projection_type="equirectangular",
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

    fig.update_geos(
        showframe=False,
        showcoastlines=False,
        projection_type="equirectangular",
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
        create_Text(
            """Since the dawn of the industrial age, fossil fuels have been a key enabler of economic development, providing the fuel that generated most of the world’s electricity, powering automobiles, ships and aircraft, and fuelling industrial activity. As a result, economic growth has been closely tied to a rise in greenhouse gas emissions through most of modern economic history.
"""
        ),
        create_Text(
            """This relationship, however, is changing. With growing concern regarding climate change and global warming, there have beensteady improvements in the energy intensity of economic growth (meaning that less energy is required to produce an additional unit of global GDP). More recently, a dramatic rise in clean energy deployment, there has been a growing divergence between GDP growth and CO2 emissions in most economies around the world.
"""
        ),
        dmc.Container(
            create_select_continent(),
            size="lg",
            pt=20,
            style={
                "position": "fixed",
                "z-index": "100",
                "bottom": "0",
                "width": "100%",
                "background-color": "white",
                "margin-left": "-10px",
                "padding-bottom": "10px",
            },
        ),
        dmc.Grid(
            children=[
                dmc.Col(
                    dcc.Graph(
                        id="emm-gdp-graph",
                        figure=create_emm_gdp_graph(emm_gdp),
                        style={"height": "60vh"},
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
                create_Text(
                    """From the mapview given above, we observe the correlation between GDP and CO2 Emissions for countries across the past 2 decades (1999-2022). A positive (negative) correlation indicates that on an average, since 1999, an increase in GDP has been supplemented by an increase (decrease) in CO2 Emissions, and a decrease in CO2 Emissions has been accompanied by an a decrease (increase) in GDP. The higher the correlation value, the more ngeatively it is viewed, as it indicates the incapbility of decoupling GDP and CO2 Emissions. 
"""
                ),
                create_Text(
                    """In advanced economies, continued growth in GDP has been accompanied by a peak in CO2 emissions in 2007, followed by a decline. In many emerging and developing economies, the trajectories of CO2 emissions and GDP growth have also started to diverge.

"""
                ),
                dmc.Col(
                    dcc.Graph(
                        id="gdp-temp-graph",
                        figure=create_gdp_temp_graph(temp_gdp),
                        style={"height": "60vh"},
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
                create_Text(
                    """It has long been understood that economic outcomes are related to climate. This climate-economy relationship determines the scope and magnitude of market impacts from climate change over the next 100 years and beyond. Consequently, an understanding of the climate-economy relationship is central to projections of damages from anticipated climate change, and to policymaking that weighs the benefits and costs of climate change mitigation. The mapview given above demonstrates the correlation between GDP and Temperature for countries across the past 2 decades (1999-2022). A positive (negative) correlation indicates that on an average, since 1999, an increase in temperature has still been associated with an overall increase (decrease) in GDP and vice versa. A majority of higher GDP countries, sustained by non-agricultural production tend to have positive correlation values. On the other hand, a majority of lower GDP countries, sustained by agricultural production tend to have negative correlation values.
"""
                ),
                dmc.Container(
                    dmc.Space(h=300),
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
