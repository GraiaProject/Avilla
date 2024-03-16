# Migrate to Flywheel

Flywheel 致力于用轻巧灵活的设计来迅捷而准确的构筑 Avilla 的所有设施，至少可以成为其中一些的重要基础；其部分内容将直接面向用户对接暴露。

对于被分配至此任务的开发者，需要先阅读 [Flywheel 的文档](https://github.com/GreyElaina/RvFlywheel#readme)。
同时，考虑到 Flywheel 的体量极小，也建议配合文档阅读其代码，透过此了解其基本原理。

## Todo List

- Overloads
  - [ ] `SelectorOverload`，取代现有的 `TargetOverload` 设施。
  - ~~`QueryOverload`~~，参考下文详细叙述。
  - ~~`MetadataOverload`~~，已可被 Flywheel 中的 `SimpleOverload` 取代。
  - ~~`ResourceOverload`~~，已可被 Flywheel 中的 `TypeOverload` 或 `SimpleOverload` 取代。

### Overloads

Overload 描述对单个参数的重载规则与模式。

#### 关于 Query

Avilla 中的 Query 机制致力于通过有规则的构造 Selector，以提供发现其他实体的方法。

在 Ryanvk v1.2 及之前版本中，这一行为需要直接从底层逻辑编写，但 Flywheel 的 Overload 形式或许提供了新的，更高效的方法。

```python
@Fn.declare
class query(FnCompose):
    src = TargetOverload("src")
    dst = TargetOverload("dst")
```

我们规定当注册实现...按照 Flywheel 的说法，应该是*收集*实现，我们总是获得完整的 `src` 与 `dst` 指定。

```python
@query.impl(src="::", dst="::group")

@query.impl(src="::group", dst="::group.member")

@query.impl(src="::group.member", dst="::group.member.message")
```

通过一定的算法，我们可以构造一条从 `::` 通向 `::group.member.message` 的道路，
这对于目前 Flywheel 来说不成问题。

### 基类

- [ ] Core
- 协议实现
  - [ ] qqapi
  - [ ] onebot
  - [ ] satori
  - and more...

在 Flywheel 中，我们需要构造一些包含了 `InstanceOf` 描述的基类，并让我们的实现继承。
`scoped_context` 的构造虽然可以使用非静态方法（`static=False`），
但在 Avilla 中这种方法可以被更易用，且更适合操作的 `InstanceOf + InstanceContext` 完成。

在现有 Ryanvk 1.2 情况中，我们通常使用 `avilla.core.ryanvk.collector` 中的各式 `Collector` 来辅助指定所使用的类型。

```python
# file: avilla.qqapi.perform.context

class QQAPIContextPerform((m := AccountCollector["QQAPIProtocol", "QQAPIAccount"]())._):
    ...
```

这在 Flywheel 中不再推荐，我们现在推荐使用这种形式。

```python
# file: avilla.qqapi.perform.base
class QQAPIPerformAccountBase:
    protocol = InstanceOf(QQAPIProtocol)
    account = InstanceOf(QQAPIAccount)

# file: avilla.qqapi.perform.account
class QQAPIAccountPerform(m := scoped_context.env().target, QQAPIPerformAccountBase):
    @some_fn.impl(...)
    async def some_impl(self):
        reveal_type(self.protocol)
        reveal_type(self.account)
```

由于我们一直以来推荐使用 *lazy loading* 模式，这套体系可以良好的组织以避免 circular import 的问题。

### Staff

在 Flywheel 中已经不存在 `Staff`，因为不再需要这样来封装对 `Fn` 的复杂封装。

相对的，我们建议协议实现的维护者提供形似 `TelegramAction` 的集合类来方便进行各种内部与外部的操作，如同之前的形似 `TelegramCapability` 的各式 Capability，只是这个名字更切题。

```python
class TelegramAction:
    @Fn.declare
    class serialize_message(FnCompose):
        ...

    @Fn.declare
    class deserialize_message(FnCompose):
        ...
    
    @Fn.declare
    class parse_event(FnCompose):
        ...
```

我们推荐在行为集合声明类中仅声明 `Fn` 的操作，而不是各种静态方法全部塞里面，那样的情况更适合存放在单独模块内。

因为 `FnOverload` 并不拘束于仅能在 `FnCompose` 内声明，你可以考虑在形似 `TelegramAction` 处声明共用的 `Overload` 集合。

当调用时，我们只需要根据类型检查器的提示使用即可，但注意，你依旧需要考虑前面提到过的 `InstanceOf` 情况，使用 `InstanceContext.scope` 上下文管理器注入。

另外，`InstanceContext` 可以长久持有，你完全可以直接在 `__init__` 之类的地方创建好，然后直接用。
这对于后面提到的 `CollectContext` 也是类似管用的。

```python
# when init
self.instance_ctx = InstanceContext()
self.instance_ctx[TelegramNetwork] = self

# when received data
with connection.instance_ctx:
    TelegramAction.parse_event(data)
```

### Endpoint

本来应该有的，现在已经被 `InstanceOf`…… 好像本来就是。

### 具体实现的模块如何导入

我们推荐声明一个 `_import_performs` 方法，然后在 `Protocol.ensure` 配合 `CollectContext` 使用。

当然，前提是你里面的全部用了 `@local_collect` 或是 `scoped_context.env()`。

```python
def _import_performs():
    ...

class Protocol:
    def ensure(self, avilla):
        with CollectContext() as self.perform_context:
            _import_performs()
```
