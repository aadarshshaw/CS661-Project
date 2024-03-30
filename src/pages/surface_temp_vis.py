import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, register_page, Input, Output, callback
import dash_mantine_components as dmc
from assets.constants import months
from pathlib import Path

register_page(
    __name__,
    "/surface_temp_vis",
    title="Climate Change Visualisation",
    description="Climate Change Visualisation",
)

min_temp, max_temp = -37.658, 38.84200000000001
min_year, max_year = "1743", "2013"

parsed_path = (
    Path(__file__).parents[2]
    / "Datasets"
    / "Surface Temperatures"
    / "ParsedSurfaceTemp.csv"
)
global_temp_path = (
    Path(__file__).parents[2]
    / "Datasets"
    / "Surface Temperatures"
    / "GlobalLandTemperaturesByCountry.csv"
)

df = pd.read_csv(parsed_path)
global_temp_country = pd.read_csv(global_temp_path)
global_temp_country["dt"] = pd.to_datetime(global_temp_country["dt"])

countries = df["Country"].tolist()
selected_countries = []


def getMeanTemperature(year):
    return np.array(df[year])


initial_year = min_year
initial_year_data = getMeanTemperature("2013")


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
    )


def create_button(id, text, color):
    return dmc.Button(id=id, color=color, children=[dmc.Text(text)])


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
        create_slider(1743, 2013),
        dmc.Grid(
            children=[
                dmc.Grid(
                    align="center",
                    children=[
                        dmc.Col(
                            dcc.Graph(
                                figure=create_surface_plot("2013"),
                                id="surface-temperature-plot",
                            ),
                            span=12,
                        ),
                        dmc.Col(
                            Tile(
                                "Data Available for",
                                str(np.sum(~df["2013"].isna())),
                                "Countries",
                            ),
                            span=3,
                            id="data-available",
                        ),
                        dmc.Col(
                            Tile(
                                "Max Temp",
                                str(round(max_temp, 2)) + "°C",
                                df["Country"][np.argmax(df["2013"])],
                            ),
                            span=3,
                            id="max-temp",
                        ),
                        dmc.Col(
                            Tile(
                                "Min Temp",
                                str(round(min_temp, 2)) + "°C",
                                df["Country"][np.argmin(df["2013"])],
                            ),
                            span=3,
                            id="min-temp",
                        ),
                        dmc.Col(
                            Tile(
                                "Global Avg Temp",
                                str(round(np.nanmean(getMeanTemperature("2013")), 2))
                                + "°C",
                                "World",
                            ),
                            span=3,
                            id="global-temp",
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
                                figure=create_country_temp_plot("2013", []),
                                id="country-temp-plot",
                            ),
                            span=12,
                        ),
                    ],
                    grow=True,
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
        Output("global-temp", "children"),
        Output("data-available", "children"),
    ],
    Input("year-slider", "value"),
    prevent_initial_call=True,
)
def update_surface_plot(value):
    return (
        create_surface_plot(str(value)),
        Tile(
            "Max Temp",
            str(round(np.nanmax(getMeanTemperature(str(value))), 2)) + "°C",
            df["Country"][np.argmax(df[str(value)])],
        ),
        Tile(
            "Min Temp",
            str(round(np.nanmin(getMeanTemperature(str(value))), 2)) + "°C",
            df["Country"][np.argmin(df[str(value)])],
        ),
        Tile(
            "Global Avg Temp",
            str(round(np.nanmean(getMeanTemperature(str(value))), 2)) + "°C",
            "World",
        ),
        Tile(
            "Data Available for",
            str(np.sum(~df[str(value)].isna())),
            "Countries",
        ),
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
