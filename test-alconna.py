from arclet.alconna import Alconna, Args, Option, Subcommand, count
from avilla.console.protocol import ConsoleProtocol
from avilla.core import Avilla, Context
from avilla.core.builtins.command import AvillaCommands, Match

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

@cmd.on("ping")
async def ping(ctx: Context):
    await ctx.scene.send_message("pong")

@cmd.on(alc)
async def test(package: Match[str], ctx: Context):
    await ctx.scene.send_message(f"installing {package.result}")

@cmd.on("add test {a:int} {b:int}")
async def add_test(ctx: Context, a: int, b: int):
    await ctx.scene.send_message(f"test {a} + {b} = {a + b}")

@cmd.on("add {a:int} {b:int}")
async def add(ctx: Context, a: int, b: int):
    await ctx.scene.send_message(f"{a} + {b} = {a + b}")

avilla.launch()
