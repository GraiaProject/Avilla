<div align="center">

# Avilla

_The next-gen framework for IM development._

> 即刻动身, 踏上寻找第二个故乡的旅程.

</div>

<p align="center">
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="code_style" />
  <img src="https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336" />

</p>

Avilla 是 `Graia Project` 的 "下一代" 框架实现,
通过对 [ `OneBot` ](https://github.com/botuniverse/onebot), [ `Telegram Bot API` ](https://core.telegram.org/bots) 及其他的基于不同即时通讯软件实现的各式对接接口,
以及其他具有相应概念的 "异步消息流" 实例进行总结, 抽象其中最为基本的各式模型, 构造了一个理论上可以实现零成本切换对接平台的框架.

**该框架目前处于快速迭代状态, API 可能会发生 _剧烈_ 变化, 可能还不适合进行生产性的开发与运维**

> 项目名称取自日本轻小说 《魔女之旅》 的角色 "艾维莉亚(Avilla)".

|Docs|[![docs](https://img.shields.io/badge/docs%20on-readthedocs-black)](https://graia.readthedocs.io/)|[![docs](https://img.shields.io/badge/docs%20on-netlify-informational)](https://graia.netlify.app/)|[![docs](https://img.shields.io/badge/docs%20on-cloudflare-orange)](https://graia.pages.dev/)|
|:-:|:-:|:-:|:-:|

## Notable Features

 - **原生跨平台**: 开创性的 Relationship 操作模型, 配合最小功能单元, 行为扩展等诸多独特设计, 无论是简单的消息收发还是平台设计的独特交互, Avilla 都能处理地得心应手.
 - **原生多账号**: Avilla 在设计之初, 就考虑了同时管理多个账号, 甚至是多个平台上的多个账号这些问题, 并加以研究与解决. 而现在, 账号管理本应如此简单便捷而收放自如.
 - **一次编写, 多平台可用**: 得益于 Avilla 的强大抽象, 开发者只需面向 Avilla 就能完成核心业务的开发, 显著的减少了维护成本.
 - **平台特性友好**: Avilla 以 Activity, Reaction, Extension 等诸项设计, 使得开发者在运用平台特性的方式更加规范而不失表达性. 担心平台间特性的不通用? 你可以同时为多个平台编写不同的特性用例, Avilla 会自动应用可用的适配, 不改动核心逻辑的同时保证基本特性的可用!
  > 担心可用性? 我们同样提供了一些核心的非平台依赖实现, 例如 `TextCommand`, 这些组件仅要求平台实现最基本的交互实现, 剩下的一切交给 Avilla 处理!
 - **现有基建兼容**: 得益于 `Amnesia`, `Commander`, `Twilight`, `Alconna` 或是基于 `Launart` 编写的各式扩展, 可以直接与 Avilla 协同而无需任何迁移成本.
 - **高可伸缩性**: Avilla 既支持单文件使用, 亦支持基于 Graia Saya 驱动的模块系统编写应用.

## Quick Start

```py
from avilla.core import Avilla, Context, MessageReceived
from avilla.console.protocol import ConsoleProtocol

avilla = Avilla()
avilla.apply_protocols(ConsoleProtocol())


@avilla.listen(MessageReceived)
async def on_message_received(cx: Context, event: MessageReceived):
    await cx.scene.send_message("Hello, Avilla!")


avilla.launch()
```

## 部件发布情况

|               代号               |         对接平台          |              协议              |    开发进度     |                                                  PyPI                                                   |   维护者    |  开源协议  |
|:------------------------------:|:---------------------:|:----------------------------:|:-----------:|:-------------------------------------------------------------------------------------------------------:|:--------:|:------:|
|      [Core](avilla/core)       |           -           |              -               |  **Alpha**  |       [![image](https://img.shields.io/pypi/v/avilla-core)](https://pypi.org/project/avilla-core)       | Official |  MIT   |
|   [Console](avilla/console)    |         终端环境          |          `Console`           |  **Alpha**  |    [![image](https://img.shields.io/pypi/v/avilla-console)](https://pypi.org/project/avilla-console)    | Official |  MIT   |
| [Elizabeth](avilla/elizabeth)  |      Tencent QQ       |       `mirai-api-http`       |  **Alpha**  |  [![image](https://img.shields.io/pypi/v/avilla-elizabeth)](https://pypi.org/project/avilla-elizabeth)  | Official | AGPLv3 |
| [Onebot 11](avilla/onebot/v11) |        *多平台支持*        |         `OneBot v11`         |   **WIP**   | [![image](https://img.shields.io/pypi/v/avilla-onebot-v11)](https://pypi.org/project/avilla-onebot-v11) | Official |   -    |
|     [QQ API](avilla/qqapi)     | Tencent QQ / QQ-Guild | `QQ / QQ-Guild Official API` |   **WIP**   |      [![image](https://img.shields.io/pypi/v/avilla-qqapi)](https://pypi.org/project/avilla-qqapi)      | Official |  MIT   |
|       [Red](avilla/red)        |     Tencent QQNT      |        `Red Protocol`        |   **WIP**   |        [![image](https://img.shields.io/pypi/v/avilla-red)](https://pypi.org/project/avilla-red)        | Official |  MIT   |
|    [Satori](avilla/satori)     |        *多平台支持*        |    `Satori Protocol (v1)`    |   **WIP**   |     [![image](https://img.shields.io/pypi/v/avilla-satori)](https://pypi.org/project/avilla-satori)     | Official |  MIT   |
|  [Telegram](avilla/telegram)   |       Telegram        |          `Telegram`          |  **Draft**  |   [![image](https://img.shields.io/pypi/v/avilla-telegram)](https://pypi.org/project/avilla-telegram)   |    -     |   -    |
| [Nightcord](avilla/nightcord)  |        Discord        |        `Discord Bots`        |  **Draft**  |  [![image](https://img.shields.io/pypi/v/avilla-nightcord)](https://pypi.org/project/avilla-nightcord)  |    -     |   -    |
|      [Kook](avilla/kook)       |         Kook          |            `Kook`            |  **Draft**  |       [![image](https://img.shields.io/pypi/v/avilla-kook)](https://pypi.org/project/avilla-kook)       |    -     |   -    |
| [OneBot 12](avilla/onebot/v12) |        *多平台支持*        |         `OneBot v12`         | **Planned** |                                                    -                                                    |    -     |   -    |

## 我们的愿景

创造出比这之前还要更加具有潜力和创造性的作品, 借此有力促进社区的发展,
助力社区的艺术家们 (Developers & Artists) 以更高的效率, 基于更完善的底层, 创作出更加精彩的作品.

## 相关项目

<div align="center">

星座的光芒是由一个个星点共同组成的, 任何优秀的作品都绝不会是一个人的功绩.  
而若是没有这些项目, Avilla 的实现就无从谈起.  
排名不分顺序, 可能有许遗漏, 这里仅列出部分较为重要的项目.

</div>

  + [ `Nonebot Team` ](https://github.com/nonebot):
    - [ `Nonebot v2` ](https://github.com/nonebot/nonebot2): 同样是社区中赫赫有名的优秀框架.
  + [ `Arclet Project` ](https://github.com/ArcletProject): 在借鉴的基础上, 还进行了难能可贵的优秀创新, 仍在不断成长的框架实现.
  + [ `Mamoe Technologies` ](https://github.com/mamoe):
    - [ `mirai` ](https://github.com/mamoe/mirai)
    - [ `mirai-api-http` ](https://github.com/project-mirai/mirai-api-http)
  + [ `OneBot Spec` ](https://github.com/botuniverse/onebot): Avilla for OneBot 所依据的实现规范, 同时也是 Avilla Protocol 设计时的参考之一.
  + [ `go-cqhttp` ](https://github.com/Mrs4s/go-cqhttp): 可能是现在运用最为广泛的 OneBot v11 & v12 实现.

无论如何, Avilla 都是 Graia Project 下的一个子项目, 以下项目均在不同层面上支持了 Avilla 的开发:
  + [ `Broadcast Control` ](https://github.com/GraiaProject/BroadcastControl): 事件系统实现, 最为锋利的魔剑(Magic Sword).
  + [ `Ariadne` ](https://github.com/GraiaProject/Ariadne): 继承了前作的衣钵, 在 Avilla 尚未成熟之际撑起大梁的后续作品, 同样进行了可贵的创新.

<div align="center">

衷心感谢这些以及其他未被提及的项目.

</div>


## 开源协议

若非特殊说明, Avilla 及其子包默认使用 MIT 作为开源协议, 但如果你若引用到了使用 GPL/AGPL/LGPL 等具有传染性开源协议的项目, 无论是对 Avilla 实现或是使用了相应 Avilla 实现的项目仍需要遵循相关规则.
