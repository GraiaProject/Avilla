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

## Roadmap

* `Avilla Protocol` : 对各式常见的行为进行抽象, 并通过可扩展的模型, 实现尽可能的功能可迁移性.
  - 使用 [Launart](https://github.com/GraiaProject/Launart) 调度启动任务与应用实例的生命周期;
  - 创新性的 Relationship 模型, 携带有进行任意操作所需的基本信息, 规范化行为模式与实现的编写;
  - 使用 `Selector`, 实现了信息与对象本身的解耦, 减少平台实现的负担;
  - 规范化的 `Resource` 抽象优化了对不同资源与资源类型的操作, 尤其是其内容的获取与其元信息的操作;
  - 规范各式请求为 `Request`;
  - 将各式元信息放缩为各个最小功能单元及其之间的组合, 不失表现性和可扩展性;
  - 使用各式如 `Broadcast Control` 的注入入口, 极大简化了接口的使用;
  - 复用来自 `Amnesia` 的通用接口;
* And more...

```py
from creart import create
from graia.amnesia.builtins.aiohttp import AiohttpService
from graia.broadcast import Broadcast

from avilla.core import Avilla, MessageReceived, Relationship, Selector
from avilla.elizabeth.connection.config import WebsocketClientConfig
from avilla.elizabeth.protocol import ElizabethProtocol

broadcast = create(Broadcast)
avilla = Avilla(broadcast, [
    ElizabethProtocol(
        WebsocketClientConfig("bot-account", "mah-verify-code")
    )
], [AiohttpService()])

@broadcast.receiver(MessageReceived)
async def on_message_received(event: MessageReceived, rs: Relationship):
    if Selector.fragment().as_dyn().group("*").member("master-account").match(rs.ctx):
        await rs.send_message("Hello, Avilla!")

avilla.launch_manager.launch_blocking(loop=broadcast.loop)
```

## 部件发布情况

|代号|协议|开发进度|PyPI|维护者|
| :-: | :-: | :-: | :-: | :-: |
|      [Core](avilla/core)      |        -         | **Alpha** |       [![image](https://img.shields.io/pypi/v/avilla-core)](https://pypi.org/project/avilla-core)       | Official |
| [Elizabeth](avilla/elizabeth) | `mirai-api-http` |  **WIP**  |  [![image](https://img.shields.io/pypi/v/avilla-elizabeth)](https://pypi.org/project/avilla-elizabeth)  | Official |
|    [-](avilla/onebot/v11)     |   `OneBot v11`   |  **WIP**  | [![image](https://img.shields.io/pypi/v/avilla-onebot-v11)](https://pypi.org/project/avilla-onebot-v11) | Official |
|    [-](avilla/onebot/v12)     |   `OneBot v12`   | **Draft** | [![image](https://img.shields.io/pypi/v/avilla-onebot-v12)](https://pypi.org/project/avilla-onebot-v12) | Official |
|     [-](avilla/telegram)      |    `Telegram`    | **Draft** |   [![image](https://img.shields.io/pypi/v/avilla-telegram)](https://pypi.org/project/avilla-telegram)   |    -     |
| [Nightcord](avilla/nightcord) |  `Discord Bots`  | **Draft** |  [![image](https://img.shields.io/pypi/v/avilla-nightcord)](https://pypi.org/project/avilla-nightcord)  | Official |

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
