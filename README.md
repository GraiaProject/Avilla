<div align="center">

# Avilla

_The next-gen framework for IM development._ 

> 即刻动身, 踏上寻找第二个故乡的旅程.

</div>

<p align="center">
  <a href="https://github.com/howmanybots/onebot/blob/master/README.md">
    <img src="https://img.shields.io/badge/OneBot-v11-blue?style=flat&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABABAMAAABYR2ztAAAAIVBMVEUAAAAAAAADAwMHBwceHh4UFBQNDQ0ZGRkoKCgvLy8iIiLWSdWYAAAAAXRSTlMAQObYZgAAAQVJREFUSMftlM0RgjAQhV+0ATYK6i1Xb+iMd0qgBEqgBEuwBOxU2QDKsjvojQPvkJ/ZL5sXkgWrFirK4MibYUdE3OR2nEpuKz1/q8CdNxNQgthZCXYVLjyoDQftaKuniHHWRnPh2GCUetR2/9HsMAXyUT4/3UHwtQT2AggSCGKeSAsFnxBIOuAggdh3AKTL7pDuCyABcMb0aQP7aM4AnAbc/wHwA5D2wDHTTe56gIIOUA/4YYV2e1sg713PXdZJAuncdZMAGkAukU9OAn40O849+0ornPwT93rphWF0mgAbauUrEOthlX8Zu7P5A6kZyKCJy75hhw1Mgr9RAUvX7A3csGqZegEdniCx30c3agAAAABJRU5ErkJggg==" alt="onebot_v11">
  </a>
  <img alt="PyPI" src="https://img.shields.io/pypi/v/avilla-core" />
  <a href="https://autumn-psi.vercel.app/"><img src="https://img.shields.io/badge/docs_click here-vercel-black" /></a>
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
  + 特色
    - [x] `Service`: 向程序中其他部分提供经过通用抽象过的资源, 并对其加以维护, 使各部分稳定性增强, 耦合度降低.
      - [x] `AiohttpClient (http & websocket client)`
      - [x] `StarletteServer (http & websocket server)`
      - [x] `UvicornService (powerful ASGI server)`
      - `CacheManager (cache)`
        - [x] `RedisService (cache based on aioredis)`
      - [ ] `SqlmodelDatabase (database)`
    - [x] `Launch Component`: 统一的生命周期管理
    - [x] `Config`: 基于 `pydantic`, 支持作用域机制的配置系统.
    - [ ] `Commander`: 优雅的指令系统
    - [ ] `Permission`: 对标 `Luckperm`, 以低侵入度的方式提供简洁强大的权限管理能力
      - [ ] `Permissiver`: 权限管理指令, 基于 `Commander`
  + 杂项部分
    - [x] `Selector`: 实现了扁平化处理 "个体"(`Entity`) 与 "主线"(`Mainline`) 的能力.
    - [x] `Stream API`: 用于简化对获得的二进制信息处理.
    - [x] `Platform API`: 通过与 `Protocol` 协作, 扩展 Avilla Protocol, 使其能用于平台的特有特性.
  + 实现支持
   - [ ] `Avilla for OneBot` : 对  [ `OneBot` ](https://github.com/botuniverse/onebot) 的协议实现.

     - [ ] `Avilla for go-cqhttp` : 对 [ `go-cqhttp` ](https://github.com/Mrs4s/go-cqhttp) 的扩展 API 支持.

   - [ ] `Avilla for Telegram` : 对 [ `Telegram Bot API` ](https://core.telegram.org/bots) 的协议实现.
   - [ ] `Avilla for Discord` : 对 [ `Discord Bot` ](https://docs.botsfordiscord.com/) 的协议实现.
   - [ ] `Avilla for mirai-api-http` : 对 [ `mirai-api-http` ](https://github.com/project-mirai/mirai-api-http) 的支持.
* And more...

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

衷心感谢这些以及其他未被提及的项目.

## 开源协议

若非特殊说明, Avilla 及其子包默认使用 MIT 作为开源协议, 但如果你若引用到了使用 GPL/AGPL/LGPL 等具有传染性开源协议的项目, 仍需要遵循相关规则.
