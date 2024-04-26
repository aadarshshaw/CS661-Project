import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, register_page, Input, Output, callback
import dash_mantine_components as dmc
from assets.constants import months
from util.climate_spiral import create_climate_spiral
from pathlib import Path
from util.content import create_Text

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
    )

    return fig


layout = html.Div(
    [
        dmc.Text(
            "Surface Temperature Visualization", align="center", style={"fontSize": 30}
        ),
        create_Text(
            """Global warming is the long-term warming of the planet’s overall temperature. Though this warming trend has been going on for a long time, its pace has significantly increased in the last hundred years due to the burning of fossil fuels. As the human population has increased, so has the volume of fossil fuels burned. Fossil fuels include coal, oil, and natural gas, and burning them causes what is known as the “greenhouse effect” in Earth’s atmosphere.
"""
        ),
        create_Text(
            """The greenhouse effect is when the sun’s rays penetrate the atmosphere, but when that heat is reflected off the surface cannot escape back into space. Gases produced by the burning of fossil fuels prevent the heat from leaving the atmosphere. These greenhouse gasses are carbon dioxide, chlorofluorocarbons, water vapor, methane, and nitrous oxide. The excess heat in the atmosphere has caused the average global temperature to rise overtime, otherwise known as global warming.
"""
        ),
        create_Text(
            """Given the tremendous size and heat capacity of the global oceans, it takes a massive amount of added heat energy to raise Earth’s average yearly surface temperature even a small amount. The roughly 2-degree Fahrenheit (1 degrees Celsius) increase in global average surface temperature that has occurred since the pre-industrial era (1850-1900) might seem small, but it means a significant increase in accumulated heat.
"""
        ),
        create_Text(
            """That extra heat is driving regional and seasonal temperature extremes, reducing snow cover and sea ice, intensifying heavy rainfall, and changing habitat ranges for plants and animals—expanding some and shrinking others.
"""
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
                        create_Text(
                            """Over the last couple of centuries (from 1750-2023), we observe a massive rise in temperature for all countries, with higher spikes in more recent years, with the temperature (both globally and across a multitutde of countries) increasing at an almost exponential pace, which is rather alarming. While there are some natural causes partially responsible for this phenomenon, the data collected suggests that human activities, particularly emissions of heat-trapping greenhouse gases are majorly responsible for this rise in temperature.

"""
                        ),
                        create_Text(
                            """The world map above visualizes the temperature across most countries from 1750-2023. For a majority of such countries, the last 10 years of temperature recorded have been the highest recorded for that country since 1750.
"""
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
                        create_Text(
                            """Considering that the highest and lowest temperatures on Earth are likely more than 55°C apart, the concept of Global Average Land Temperature might seem futile. Temperatures vary from night to day and between seasonal extremes in the Northern and Southern Hemispheres. This means that some parts of Earth are quite cold while other parts are downright hot. However, the concept of a global average temperature is convenient for detecting and tracking changes in certain parameters (such as Amount of sunlight Earth absorbs - Amount it radiates to space as heat over time).
"""
                        ),
                        create_Text(
                            """The graph above shows the Global Average Land Temperature from 1750-Present. It demonstrates the steady rise in Global Average Land Temperature in recent years (1879-Present), which coincides with the on-set of the Industrial Revolution, and further adds to the theory that human activities are the primary reason behind this rise in temperature. 
"""
                        ),
                        dmc.Col(
                            dcc.Graph(
                                figure=create_climate_spiral(2024),
                                id="climate-spiral",
                            ),
                        ),
                        create_Text(
                            """The Temperature Spiral was first published on 9 May 2016 by British climate scientist Ed Hawkins to portray global average temperature anomaly (change) since 1850. It is said to be a "simple and effective demonstration of the progression of global warming", especially for the masses. NASA recreated the Climate Spiral in 2023 for the years 1880-2022. Both of these versions have gone viral and gained the attention of a majority of viewers, with Ed Hawkin's version being shown at the Summer Olympics in 2016. 
"""
                        ),
                        create_Text(
                            """Our version of the Temperature Spiral, is based on data from 1880-2023. The dimensions can be well represented by Polar coordinates. Temperature is along the r-axis and different values are indicated by concentric circles (-1 °C, 0 °C and 1 °C are shown in the plot), Months are along the θ axis (Jan-Dec are shown at regular intervals of θ = 2π/12) and Year along the z-axis (1880-2023).
"""
                        ),
                        dmc.Col(
                            dcc.Graph(
                                figure=create_global_temp_anomaly_plot(2023),
                                id="global-temp-anomaly-plot",
                            ),
                        ),
                        create_Text(
                            """The graph above shows temperature anomalies globally since 1880. For a particular area, these values are not absolute temperatures, but changes from the norm for that area. This concept can extended to a "Global" one as well. The data reflects how much warmer or cooler the Earth was compared to a base period of 1951-1980. (The global mean surface air temperature for that period was 14°C (57°F), with an uncertainty of several tenths of a degree.)

"""
                        ),
                        create_Text(
                            """From the maps shown prior, we infer that global warming does not mean temperatures rise everywhere at every time by same rate. Temperatures might rise 5 degrees in one region and drop 2 degrees in another. For instance, exceptionally cold winters in one place might be balanced by extremely warm winters in another part of the world. Generally, warming is greater over land than over the oceans because water is slower to absorb and release heat (thermal inertia). Warming may also differ substantially within specific land masses and ocean basins.

"""
                        ),
                        create_Text(
                            """In the chart above, the years from 1750 to 1939 tend to be cooler, then level off by the 1950s. Decades within the base period (1951-1980) do not appear particularly warm or cold because they are the standard against which other years are measured.

"""
                        ),
                        create_Text(
                            """The leveling off of temperatures in the middle of the 20th century can be explained by natural variability and by the cooling effects of aerosols generated by factories, power plants, and motor vehicles in the years of rapid economic growth after World War II. Fossil fuel use also increased after the war (5 percent per year), boosting greenhouse gases. Cooling from aerosol pollution happened rapidly. In contrast, greenhouse gases accumulated slowly, but they remain in the atmosphere for a much longer time. According to former GISS director James Hansen, the strong warming trend of the past four decades likely reflects a shift from balanced aerosol and greenhouse gas effects on the atmosphere to a predominance of greenhouse gas effects after aerosols were curbed by pollution controls.
"""
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
                        create_Text(
                            """The chart above demonstrates the country-by-country monthly Temperature data from 1750-2013. The dropdown menu placed above can be used to select multiple countries, and compare the progression of their monthly temperature for a particular year by visualizing them in the same plot. We observe a seasonal trend, with temperature being higher in majority of the Summer and Autumn months  (May-Sep), and being lower in the Winter and Spring months (Jan-Apr and Oct-Dec)."""
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
