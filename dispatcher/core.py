from utils.logger import logger
from typing import List, Union
from functools import wraps

from wechatpy.messages import BaseMessage

from .dtype import dispatcher_type as dtype
from .trigger import TriggerFunction, BaseTrigger, EtypeTrigger, PrefixTrigger, SuffixTrigger, KeywordTrigger, RexTrigger

# TODO: Complement all message and event types
_dispatcher_structure = {
    "event": {
        "scan": dtype.EVENT_DISPATCHER,
        "subscribe": dtype.EVENT_DISPATCHER,
        "subscribe_scan": dtype.EVENT_DISPATCHER,
        "unsubscribe": dtype.EVENT_DISPATCHER,
    },
    "text": dtype.TEXT_DISPATCHER
}
'''
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
'''
class DispatcherNode(dict):
    def __init__(self, name=None):
        self.__name = name

    def get_name(self) -> str:
        return self.__name 

    def find_trigger_function(self, key_list: List[str], msg: BaseMessage) -> TriggerFunction:
        reversed_key_list = list(key_list)
        reversed_key_list.reverse()
        return self._find_trigger_function(reversed_key_list, msg)
    
    def _find_trigger_function(self, reversed_key_list: List[str], msg: BaseMessage) -> TriggerFunction:
        if len(reversed_key_list) == 0:
            return self._self_find_tf(msg)
        key = reversed_key_list.pop()
        if key not in self:
            return None
        return self[key]._find_trigger_function(reversed_key_list, msg)

    def _self_find_tf(self, msg):
        raise NotImplementedError

    def __getattr__(self, name):
        return self[name]

class EventDispatcherNode(DispatcherNode):
    def __init__(self, name=None):
        super().__init__(name)
        self._etype_triggers = EtypeTrigger()
    
    def _self_find_tf(self, msg):
        return self._etype_triggers.find_handler(msg)
    
    def on_etype(self, etype):
        def deco(func):
            @wraps(func)
            async def wrapper(client, msg):
                return await func(client, msg)
            tf = TriggerFunction(wrapper)
            self._etype_triggers.add(etype, tf)
            logger.info(f'"{func.__name__}" registered to "{self.get_name()}" as EtypeTrigger "{etype}"')
            return func
        return deco

    def __call__(self, func):
        return self.on_etype('*')(func)

class TextDispatcherNode(DispatcherNode):
    def __init__(self, name=None):
        super().__init__(name)
        self._prefix_triggers = PrefixTrigger()
        self._suffix_triggers = SuffixTrigger()
        self._keyword_triggers = KeywordTrigger()
        self._rex_triggers = RexTrigger()
        self._etype_triggers = EtypeTrigger()
        self._trigger_chain: List[BaseTrigger] = [ self._prefix_triggers, self._suffix_triggers, self._keyword_triggers, self._rex_triggers, self._etype_triggers ]
    
    def _self_find_tf(self, msg):
        for trigger in self._trigger_chain:
            tf = trigger.find_handler(msg)
            if tf:
                return tf
        return None
    
    def on_prefix(self, prefix: Union[str, List[str]]):
        def deco(func):
            @wraps(func)
            async def wrapper(client, msg):
                return await func(client, msg)
            tf = TriggerFunction(wrapper)
            if type(prefix) != list:
                self._prefix_triggers.add(prefix, tf)
            else:
                for p in prefix:
                    self._prefix_triggers.add(p, tf)
            logger.info(f'"{func.__name__}" registered to "{self.get_name()}" as PrefixTrigger "{prefix}"')
            return func
        return deco
    
    def on_fullmatch(self, fullmatch: Union[str, List[str]]):
        def deco(func):
            @wraps(func)
            async def wrapper(client, msg):
                if msg.param.remain != '':
                    logger.info(f'Message {msg.id} is ignored by fullmatch condition')
                    return
                return await func(client, msg)
            tf = TriggerFunction(wrapper)
            if type(fullmatch) != list:
                # on_fullmatch uses prefix trigger
                # so on_fullmatch may conflict with on_prefix
                self._prefix_triggers.add(fullmatch, tf)
            else:
                for f in fullmatch:
                    self._prefix_triggers.add(f, tf)
            logger.info(f'"{func.__name__}" registered to "{self.get_name()}" as FullmatchTrigger "{fullmatch}"')
            return func
        return deco
    
    def on_suffix(self, suffix: Union[str, List[str]]):
        def deco(func):
            @wraps(func)
            async def wrapper(client, msg):
                return await func(client, msg)
            tf = TriggerFunction(wrapper)
            if type(suffix) != list:
                self._suffix_triggers.add(suffix, tf)
            else:
                for s in suffix:
                    self._suffix_triggers.add(s, tf)
            logger.info(f'"{func.__name__}" registered to "{self.get_name()}" as SuffixTrigger "{suffix}"')
            return func
        return deco
    
    def on_keyword(self, keyword: Union[str, List[str]]):
        def deco(func):
            @wraps(func)
            async def wrapper(client, msg):
                return await func(client, msg)
            tf = TriggerFunction(wrapper)
            if type(keyword) != list:
                self._keyword_triggers.add(keyword, tf)
            else:
                for k in keyword:
                    self._keyword_triggers.add(k, tf)
            logger.info(f'"{func.__name__}" registered to "{self.get_name()}" as KeywordTrigger "{keyword}"')
            return func
        return deco
    
    def on_rex(self, rex: Union[str, List[str]]):
        def deco(func):
            @wraps(func)
            async def wrapper(client, msg):
                return await func(client, msg)
            tf = TriggerFunction(wrapper)
            self._rex_triggers.add(rex, tf)
            logger.info(f'"{func.__name__}" registered to "{self.get_name()}" as RexTrigger "{rex}"')
            return func
        return deco
    
    def on_etype(self, etype: Union[str, List[str]]):
        def deco(func):
            @wraps(func)
            async def wrapper(client, msg):
                return await func(client, msg)
            tf = TriggerFunction(wrapper)
            if type(etype) != list:
                self._etype_triggers.add(etype, tf)
            else:
                for c in etype:
                    self._etype_triggers.add(c, tf)
            logger.info(f'"{func.__name__}" registered to "{self.get_name()}" as EtypeTrigger "{etype}"')
            return func
        return deco

    def __call__(self, func):
        return self.on_etype('*')(func)

def _init_dispatcher(dispatcher_item: DispatcherNode, format_dict: dict):
    for key, value in format_dict.items():
        node_name = f'{dispatcher_item.get_name()}.{key}'
        if type(value) == int:
            if value == dtype.TEXT_DISPATCHER:
                dispatcher_item[key] = TextDispatcherNode(node_name)
            elif value == dtype.EVENT_DISPATCHER:
                dispatcher_item[key] = EventDispatcherNode(node_name)
            else:
                logger.warning(f'Unknow dtype {value}')
        else:
            dispatcher_item[key] = DispatcherNode(node_name)

        if type(value) == dict:
            _init_dispatcher(dispatcher_item[key], value)

def init_dispatcher_tree(format_dict: dict) -> DispatcherNode:
    dispatcher_root = DispatcherNode('dispatcher')
    _init_dispatcher(dispatcher_root, format_dict)
    return dispatcher_root

dispatcher = init_dispatcher_tree(_dispatcher_structure)