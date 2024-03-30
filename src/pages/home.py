import dash_mantine_components as dmc
from dash import html, register_page
from assets.constants import introduction, team

register_page(
    __name__,
    "/",
    title="Climate Change Visualisation",
    description="Climate Change Visualisation",
)


def create_title(title, id):
    return dmc.Text(title, align="center", style={"fontSize": 30}, id=id)


def create_head(text):
    return dmc.Text(text, align="center", my=10, mx=0)


def Tile(image, name, branch, email):
    return dmc.Card(
        radius="md",
        p="xl",
        withBorder=True,
        m=5,
        children=[
            dmc.Image(
                src=image,
                alt="",
                width=100,
                height=100,
                radius="lg",
            ),
            dmc.Text(name, size="lg", mt="md"),
            dmc.Divider(
                style={"width": 50},
                size="sm",
                color=dmc.theme.DEFAULT_COLORS["indigo"][5],
                my=10,
            ),
            dmc.Text(branch, size="sm", color="dimmed", mt="sm"),
            dmc.Anchor(
                email, href="mailto:" + email, size="sm", color="dimmed", mt="sm"
            ),
        ],
    )


layout = dmc.Container(
    children=[
        html.Div(
            [
                dmc.Container(
                    mt=30,
                    children=[
                        create_title(
                            "Climate Change and Global Warming Visualisation", "title"
                        ),
                        create_head("Group 9"),
                    ],
                ),
                dmc.Text(introduction),
                dmc.Space(h="md"),
                dmc.Divider(color="gray"),
                dmc.Text("The Team", align="center", size="md", mt=20),
                dmc.Container(
                    mt=30,
                    children=[
                        dmc.SimpleGrid(
                            cols=3,
                            mt=20,
                            breakpoints=[
                                {"maxWidth": "xs", "cols": 1},
                                {"maxWidth": "xl", "cols": 2},
                            ],
                            children=[
                                Tile(
                                    image=member["image"],
                                    name=member["name"],
                                    branch=member["department"],
                                    email=member["email"],
                                )
                                for member in team
                            ],
                        ),
                    ],
                ),
            ],
        )
    ],
)
