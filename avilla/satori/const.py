from avilla.core.platform import Abstract, Land, Platform

def platform(land: str):
    return Platform(
        Land(
            land,
            [{"name": "satorijs"}],
            humanized_name=land.title(),
        ),
        Abstract(
            "satori",
            [{"name": "satorijs"}],
            humanized_name="Satori",
        ),
        Abstract(
            "satori",
            [{"name": "GraiaProject"}],
            humanized_name="Satori Protocol for Avilla",
        ),
    )
