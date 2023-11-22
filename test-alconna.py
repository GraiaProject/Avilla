from arclet.alconna import Alconna, Args, CommandMeta, Option, Subcommand, count
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
    Option("--version", help_text="显示版本号"),
    Option("-v|--verbose", action=count),
    meta=CommandMeta(
        "模拟 pip 命令",
        "pip install [package] [-r|--requirement <file>] [-i|--index-url <url>]",
        "pip install -r requirements.txt",
    )
)


avilla = Avilla()
avilla.apply_protocols(ConsoleProtocol())
cmd = AvillaCommands(need_tome=True, remove_tome=True)

@cmd.on("ping")
async def ping(ctx: Context):
    await ctx.scene.send_message("pong")

@(
cmd.command("help [name:str]", "菜单命令")
    .example("help help")
)
async def help_(ctx: Context, name: Match[str]):
    if name.available:
        try:
            await ctx.scene.send_message(cmd.get_help(name.result))
        except ValueError:
            await ctx.scene.send_message("没有这个命令")
    else:
        await ctx.scene.send_message(cmd.all_helps)

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
