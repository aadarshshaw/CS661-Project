import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, register_page, Input, Output, callback
import dash_mantine_components as dmc
from assets.constants import months
from util.climate_spiral import create_climate_spiral
from pathlib import Path

register_page(
    __name__,
    "/surface_temp_vis",
    title="Climate Change Visualisation",
    description="Climate Change Visualisation",
)

min_temp, max_temp = -37.658, 38.84200000000001
min_year, max_year = 1750, 2023

parsed_path = (
    Path(__file__).parents[2]
    / "Datasets"
    / "Surface Temperatures"
    / "AnnualTempByCountry.xlsx"
)
global_temp_path = (
    Path(__file__).parents[2]
    / "Datasets"
    / "Surface Temperatures"
    / "GlobalLandTemperaturesByCountry.csv"
)

global_temp_anomaly_path = (
    Path(__file__).parents[2] / "Datasets" / "Surface Temperatures" / "TempAnomaly.csv"
)

global_mean_temp_path = (
    Path(__file__).parents[2]
    / "Datasets"
    / "Surface Temperatures"
    / "GlobalMeanTemp.csv"
)

df = pd.read_excel(parsed_path, sheet_name="Complete")
global_temp_country = pd.read_csv(global_temp_path)
global_mean_temp = pd.read_csv(global_mean_temp_path)
global_mean_temp.index = global_mean_temp["Year"]
global_temp_country["dt"] = pd.to_datetime(global_temp_country["dt"])
global_temp_anomaly = pd.read_csv(global_temp_anomaly_path)

countries = df["Country"].tolist()
selected_countries = []


def getMeanTemperature(year):
    return np.array(df[year])


initial_year = min_year
initial_year_data = getMeanTemperature(2023)


def create_slider(min_year, max_year):
    return dmc.Grid(
        align="center",
        justify="center",
        children=[
            dmc.Col(dmc.Text("Year:"), span=1),
            dmc.Col(
                dmc.Slider(
                    id="year-slider",
                    min=min_year,
                    max=max_year,
                    step=1,
                    value=max_year,
                    updatemode="drag",
                    marks=[
                        {"value": i, "label": str(i)}
                        for i in range(min_year, max_year + 1, 50)
                    ],
                ),
                span=11,
            ),
        ],
        m=20,
    )


def create_surface_plot(year):
    globe = go.Figure(
        data=go.Choropleth(
            locations=countries,
            z=getMeanTemperature(year),
            locationmode="country names",
            # text=countries,
            marker=dict(
                line=dict(color="rgb(0,0,0)", width=1),
            ),
            colorscale="RdBu_r",
            zmin=min_temp,
            zmax=max_temp,
            colorbar=dict(
                title="Temperature (°C)",
            ),
        )
    )

    globe.update_layout(
        # title="Average land temperature in countries",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        geo=dict(
            showframe=False,
            showocean=True,
            oceancolor="rgb(0,155,255)",
            projection=dict(
                type="orthographic",
                rotation=dict(lon=60, lat=10),
            ),
            lonaxis=dict(showgrid=True, gridcolor="rgb(102, 102, 102)"),
            lataxis=dict(showgrid=True, gridcolor="rgb(102, 102, 102)"),
        ),
        # width=800,
        height=500,
        autosize=True,
    )

    return globe


def Tile(title, temp, country):
    return dmc.Card(
        radius="md",
        p="xl",
        withBorder=True,
        m=5,
        children=[
            dmc.Text(title, size="md"),
            dmc.Text(temp, size="xl", mt="md", weight="bold"),
            dmc.Text(country, size="sm", color="dimmed", mt="sm"),
        ],
    )


def create_select(id):
    return dmc.MultiSelect(
        id=id,
        placeholder="Select a country",
        label="Select Countries",
        data=countries,
        searchable=True,
        nothingFound="No options found",
        value=["United States", "India", "China"],
    )


def create_button(id, text, color):
    return dmc.Button(id=id, color=color, children=[dmc.Text(text)])


def create_global_temp_plot(year):
    if year > 2020:
        year = 2020
    fig = go.Figure()
    temps = []
    for y in range(min_year, year + 1):
        temps.append(global_mean_temp.loc[y]["MeanTemp"])
    fig.add_trace(go.Scatter(x=list(range(min_year, year + 1)), y=temps))
    fig.update_layout(
        title="Global Average Land Temperature",
        xaxis=dict(title="Year"),
        yaxis=dict(title="Temperature (°C)"),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    return fig


def create_global_temp_anomaly_plot(year):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=global_temp_anomaly[global_temp_anomaly["Year"] <= year]["Year"],
            y=global_temp_anomaly[global_temp_anomaly["Year"] <= year]["Anomaly"],
            marker=dict(
                color=np.where(
                    global_temp_anomaly[global_temp_anomaly["Year"] <= year]["Anomaly"]
                    > 0,
                    "crimson",
                    "blue",
                )
            ),
        )
    )
    fig.update_layout(
        title="Global Average Land Temperature Anomaly",
        xaxis=dict(title="Year"),
        yaxis=dict(title="Temperature Anomaly (°C)"),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    return fig


def create_country_temp_plot(year, selected_countries):
    if selected_countries is None:
        return go.Figure(
            layout=dict(
                title="Average land temperature in countries",
                xaxis=dict(
                    title="Month",
                    tickvals=list(range(1, 13)),
                    ticktext=months,
                    showgrid=False,
                    tickangle=-45,
                ),
                yaxis=dict(title="Temperature (°C)"),
                plot_bgcolor="rgba(0, 0, 0, 0)",
                paper_bgcolor="rgba(0, 0, 0, 0)",
            ),
        )
    fig = go.Figure()
    for country in selected_countries:
        c = global_temp_country[
            pd.Series(
                np.array(global_temp_country["Country"] == country)
                & np.array(global_temp_country["dt"].dt.year == int(year))
            )
        ]
        fig.add_trace(
            go.Scatter(
                x=c["dt"].dt.month,
                y=c["AverageTemperature"],
                mode="lines+markers",
                name=country,
            )
        )

    fig.update_layout(
        title="Average land temperature in countries",
        xaxis=dict(
            title="Month",
            tickvals=list(range(1, 13)),
            ticktext=months,
            showgrid=False,
            tickangle=-45,
        ),
        yaxis=dict(title="Temperature (°C)"),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )

    return fig


layout = html.Div(
    [
        dmc.Text(
            "Surface Temperature Visualization", align="center", style={"fontSize": 30}
        ),
        dmc.Container(
            create_slider(min_year, max_year),
            size="lg",
            pt=20,
            style={
                "position": "fixed",
                "z-index": "100",
                "bottom": "0",
                "width": "100%",
                "padding-left": "0px",
                "background-color": "white",
                "margin-left": "-10px",
            },
        ),
        dmc.Grid(
            children=[
                dmc.Grid(
                    align="center",
                    children=[
                        dmc.Col(
                            dcc.Graph(
                                figure=create_surface_plot(2023),
                                id="surface-temperature-plot",
                            ),
                            span=12,
                        ),
                        dmc.Col(
                            Tile(
                                "Data Available for",
                                str(np.sum(~df[2023].isna())),
                                "Countries",
                            ),
                            span=4,
                            id="data-available",
                        ),
                        dmc.Col(
                            Tile(
                                "Max Temp",
                                str(round(max_temp, 2)) + "°C",
                                df["Country"][np.argmax(df[2023])],
                            ),
                            span=4,
                            id="max-temp",
                        ),
                        dmc.Col(
                            Tile(
                                "Min Temp",
                                str(round(min_temp, 2)) + "°C",
                                df["Country"][np.argmin(df[2023])],
                            ),
                            span=4,
                            id="min-temp",
                        ),
                    ],
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(
                            dcc.Graph(
                                figure=create_global_temp_plot(2020),
                                id="global-temp-plot",
                            ),
                        ),
                        dmc.Col(
                            dcc.Graph(
                                figure=create_climate_spiral(2024),
                                id="climate-spiral",
                            ),
                        ),
                        dmc.Col(
                            dcc.Graph(
                                figure=create_global_temp_anomaly_plot(2023),
                                id="global-temp-anomaly-plot",
                            ),
                        ),
                    ],
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(
                            create_select("country-select"),
                            span=12,
                        ),
                        dmc.Col(
                            dcc.Graph(
                                figure=create_country_temp_plot(2023, []),
                                id="country-temp-plot",
                            ),
                            span=12,
                        ),
                    ],
                    grow=True,
                ),
                dmc.Container(
                    dmc.Space(h="80px"),
                ),
            ]
        ),
    ]
)


@callback(
    [
        Output("surface-temperature-plot", "figure"),
        Output("max-temp", "children"),
        Output("min-temp", "children"),
        Output("data-available", "children"),
        Output("climate-spiral", "figure"),
    ],
    Input("year-slider", "value"),
    prevent_initial_call=True,
)
def update_surface_plot(value):
    return (
        create_surface_plot(value),
        Tile(
            "Max Temp",
            str(round(np.nanmax(getMeanTemperature(value)), 2)) + "°C",
            df["Country"][np.argmax(df[value])],
        ),
        Tile(
            "Min Temp",
            str(round(np.nanmin(getMeanTemperature(value)), 2)) + "°C",
            df["Country"][np.argmin(df[value])],
        ),
        # Tile(
        #     "Global Avg Temp",
        #     str(round(np.nanmean(getMeanTemperature(value)), 2)) + "°C",
        #     "World",
        # ),
        Tile(
            "Data Available for",
            str(np.sum(~df[value].isna())),
            "Countries",
        ),
        create_climate_spiral(value),
    )


@callback(
    Output("country-temp-plot", "figure"),
    [
        Input("year-slider", "value"),
        Input("country-select", "value"),
    ],
    prevent_initial_call=True,
)
def update_country_temp_plot(year, countries):
    return create_country_temp_plot(year, countries)


@callback(
    [
        Output("global-temp-plot", "figure"),
        Output("global-temp-anomaly-plot", "figure"),
    ],
    Input("year-slider", "value"),
    prevent_initial_call=True,
)
def update_global_temp_plot(year):
    return create_global_temp_plot(year), create_global_temp_anomaly_plot(year)
