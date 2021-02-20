# wechatpy-plus
基于 wechatpy 的增强版微信公众号开发框架

Enhanced wechat official account development framework based on wechatpy.

# Hello World Example
```python
from wechatpy.client import WeChatClient
from wechatpy.messages import BaseMessage

# 发送 hello，回复 hello world
@dispatcher.text.on_fullmatch('hello')
async def hello_world(wx_client: WeChatClient, msg: BaseMessage):
    open_id = event_msg.source
    wx_client.message.send_text(user_id=open_id, content='hello world')

# 关注/扫码关注回复 hello world
@dispatcher.event.subscribe
@dispatcher.event.subscribe_scan
async def subscription_hello_world(wx_client: WeChatClient, msg: BaseMessage):
    open_id = event_msg.source
    wx_client.message.send_text(user_id=open_id, content='hello world')
```

# 使用方法
## 消息分发
dispatcher 按照如下所示的树形结构进行消息分发。将消息分为两类，事件类型 `EventDispatcher` 和文字类型 `TextDispatcher`。

```
Tree structure of dispatcher:

dispatcher / DispatcherNode
├── event / DispatcherNode
│    ├── scan           / EventDispatcherNode
│    │                    └── EtypeTrigger
│    ├── subscribe      / EventDispatcherNode
│    │                    └── EtypeTrigger
│    ├── subscribe_scan / EventDispatcherNode
│    │                    └── EtypeTrigger
│    └── ...
├── text / TextDispatcherNode
│          ├── PrefixTrigger
│          ├── SuffixTrigger
│          ├── KeywordTrigger
│          ├── RexTrigger
│          └── EtypeTrigger
└── ...
```

文字类型消息被分发到 `@dispatcher.text` 后，可以通过前缀匹配 `@dispatcher.text.on_prefix`、正则匹配 `@dispatcher.text.on_regex` 等方式，进一步分发至相应函数

而事件类型消息，由于没有额外的信息，消息被分发到比如 `@dispatcher.subscribe` 后，无法进行进一步的分发，只能用唯一一个函数来处理关注事件。

但二维码扫描事件 `@dispatcher.scan` 可以在 `scene_id` 中携带额外参数（[详见微信开发文档](https://developers.weixin.qq.com/doc/offiaccount/Account_Management/Generating_a_Parametric_QR_Code.html)），因此本框架规定 `scene_id` 是一个 JSON 字符串，其对应的 JSON 对象如下所示。通过读取 `scene_id` 可以通过 `etype` 对事件消息进一步分发。
```
{
    'etype': 1
    ..other paramters..
}
```
> 二维码若携带如上所示的参数，那么该二维码扫描事件将会被分发至 `@dispatcher.scan.on_etype(etype=1)`

## 额外参数
对文字类型消息使用前缀、正则等方式进行消息分发时，在 `msg` 参数中会有额外的信息。

- `on_prefix` 会在 `msg` 中注入 `dispatcher.trigger.PrefixHandlerParameter` 对象，包含触发的前缀 `prefix` 与剩余字符串 `remain`。如下示例代码中，如果向公众号发送消息 `前缀匹配123`，将会收到消息 `123`。

```python
@dispatcher.text.on_prefix('前缀匹配')
def prefix_handler(wx_client, msg):
    open_id = event_msg.source
    ret_msg = msg.param.remain
    wx_client.message.send_text(user_id=open_id, content=ret_msg)
```

- `on_suffix` 会在 `msg` 中注入 `dispatcher.trigger.SuffixHandlerParameter` 对象，包含触发的后缀 `suffix` 与剩余字符串 `remain`。
- `on_keyword` 会在 `msg` 中注入 `dispatcher.trigger.KeywordHandlerParameter` 对象，包含触发的关键词 `keyword`。
- `on_rex` 会在 `msg` 中注入 `dispatcher.trigger.RexHandlerParameter` 对象，包含正则匹配成功后返回的 `match` 对象。

# Tips
## 推送消息失败
由于发送消息使用[客服消息接口](https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Service_Center_messages.html)，客服消息只有在用户与公众号进行特定交互后的 48 小时内能够成功发送。

因此，如果需要实现推送功能，请使用[模板消息](https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Template_Message_Interface.html)进行推送。模板消息没有限制。

## wechatpy 暂不支持异步
本项目使用 quart 进行异步开发，但 wechatpy 暂不支持异步使用。[wechatpy 异步支持计划](https://github.com/wechatpy/wechatpy/issues/580)

## 不加 on 的装饰器
`@dispatcher.scan` 等价于 `@dispatcher.scan.on_etype(etype='*')`，只有在所有 `etype` 都匹配不到时，才会触发。

# 感谢
本项目主要使用或参考了以下项目
- [quart](https://gitlab.com/pgjones/quart)
- [wechatpy](https://github.com/wechatpy/wechatpy)
- [HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)