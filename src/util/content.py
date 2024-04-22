import dash_mantine_components as dmc


def create_Text(text):
    return dmc.Container(
        [
            dmc.Space(h=10),
            dmc.Text(text, size="sm", align="justify"),
            dmc.Space(h=10),
        ]
    )
