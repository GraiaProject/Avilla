from arclet.alconna import Alconna, Args, Option, Subcommand, count

alc = Alconna(
    "pip",
    Subcommand(
        "install",
        Args["package", str],
        Option("-r|--requirement", Args["file", str]),
        Option("-i|--index-url", Args["url", str])
    ),
    Option("-v|--version", action=count),
)
