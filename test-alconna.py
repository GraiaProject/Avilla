from arclet.alconna import Alconna, Args, Option, Subcommand, count
from avilla.console.protocol import ConsoleProtocol
from avilla.core import Avilla, Context
from avilla.core.builtins.command import AvillaCommands

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


avilla = Avilla()
avilla.apply_protocols(ConsoleProtocol())
cmd = AvillaCommands()

@cmd.on(Alconna("ping"))
async def test(ctx: Context):
    await ctx.scene.send_message("pong")

@cmd.on(alc)
async def test(package: str, ctx: Context):
    await ctx.scene.send_message(f"installing {package}")

avilla.launch()
