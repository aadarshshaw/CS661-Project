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
    "Datasets\GDP\Correlation - Emissions vs GDP.xlsx", sheet_name="Correlation-Country"
)
temp_gdp = pd.read_excel(
    "Datasets\GDP\Correlation - GDP vs Temp.xlsx", sheet_name="Correlation-Method 2"
)
countries = emm_gdp["Country"]

highest_gdp_idx, lowest_gdp_idx = np.argmax(emm_gdp["Rho"]), np.argmin(emm_gdp["Rho"])
highest_gdp_country, lowest_gdp_country = (
    emm_gdp.iloc[highest_gdp_idx, :],
    emm_gdp.iloc[lowest_gdp_idx, :],
)


def create_emm_gdp_graph():
    fig = go.FigureWidget(
        data=go.Choropleth(
            locations=countries,
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


def create_gdp_temp_graph():
    fig = go.FigureWidget(
        data=go.Choropleth(
            locations=countries,
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


layout = html.Div(
    [
        dmc.Text("GDP Visualisation", align="center", style={"fontSize": 30}),
        dmc.Grid(
            children=[
                dmc.Col(
                    dcc.Graph(
                        id="emm-gdp-graph",
                        figure=create_emm_gdp_graph(),
                    ),
                    span=12,
                ),
                dmc.Col(
                    Tile(
                        "Highest Correlation",
                        f"{highest_gdp_country['Rho']:.2f}",
                        highest_gdp_country["Country"],
                    ),
                    span=4,
                ),
                dmc.Col(
                    Tile(
                        "Lowest Correlation",
                        f"{lowest_gdp_country['Rho']:.2f}",
                        lowest_gdp_country["Country"],
                    ),
                    span=4,
                ),
                dmc.Col(
                    Tile("Average Correlation", f"{emm_gdp['Rho'].mean():.2f}", ""),
                    span=4,
                ),
                dmc.Col(
                    dcc.Graph(
                        id="gdp-temp-graph",
                        figure=create_gdp_temp_graph(),
                    ),
                    span=12,
                ),
            ],
        ),
    ]
)
