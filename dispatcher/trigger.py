import re
import pygtrie
import zhconv
from typing import List

from utils.format import normalize_str
from utils.logger import logger

from wechatpy.messages import TextMessage, BaseMessage

'''
etype trigger is designed for event message
others are designed for text message
text message is a kind of event message
'''
class TriggerFunction:
    def __init__(self, func):
        self.func = func
        self.__name__ = func.__name__


class BaseParameter:
    def __init__(self, msg:str):
        self.plain_text = msg
        self.norm_text = normalize_str(msg)

class PrefixHandlerParameter(BaseParameter):
    def __init__(self, msg:str, prefix):
        super().__init__(msg)
        self.prefix = prefix
        self.remain = msg[len(prefix):].strip()
    
    @property
    def args(self):
        return self.remain.split(' ')

class SuffixHandlerParameter(BaseParameter):
    def __init__(self, msg:str, suffix):
        super().__init__(msg)
        self.suffix = suffix
        self.remain = msg[:-len(suffix)].strip()

class KeywordHandlerParameter(BaseParameter):
    def __init__(self, msg:str, keyword: str):
        super().__init__(msg)
        self.keyword = keyword

class RexHandlerParameter(BaseParameter):
    def __init__(self, msg:str, match):
        super().__init__(msg)
        self.match = match

class BaseTrigger:
    def add(self, x, tf: TriggerFunction):
        raise NotImplementedError

    def find_handler(self, msg: BaseMessage):
        raise NotImplementedError

class EtypeTrigger(BaseTrigger):
    def __init__(self):
        super().__init__()
        self.all_etype = {}
    
    def add(self, etype, tf: TriggerFunction):
        if etype in self.all_etype:
            other = self.all_etype[etype]
            logger.warning(f'Failed to add etype trigger `{etype}`: Conflicts between {tf.__name__} and {other.__name__}')
            return
        self.all_etype[etype] = tf
        logger.debug(f'Succeed to add etype trigger `{etype}`')
    
    def find_handler(self, msg: BaseMessage):
        for etype in self.all_etype:
            if etype == '*':
                continue;
            if etype == msg._etype:
                return self.all_etype[etype]
        return self.all_etype.get('*')


class PrefixTrigger(BaseTrigger):
    def __init__(self):
        super().__init__()
        self.trie = pygtrie.CharTrie()

    def add(self, prefix: str, tf: TriggerFunction):
        if prefix in self.trie:
            other = self.trie[prefix]
            logger.warning(f'Failed to add prefix trigger `{prefix}`: Conflicts between {tf.__name__} and {other.__name__}')
            return
        self.trie[prefix] = tf
        self.trie[zhconv.convert(prefix, "zh-hant")] = tf
        logger.debug(f'Succeed to add prefix trigger `{prefix}`')

    def find_handler(self, text_msg: TextMessage):
        raw_msg = text_msg.content
        item = self.trie.longest_prefix(raw_msg)
        if not item:
            return None
        prefix = item.key
        text_msg.__setattr__('param', PrefixHandlerParameter(raw_msg, prefix))
        return item.value

class SuffixTrigger(BaseTrigger):   
    def __init__(self):
        super().__init__()
        self.trie = pygtrie.CharTrie()

    def add(self, suffix: str, tf: TriggerFunction):
        suffix_r = suffix[::-1]
        if suffix_r in self.trie:
            other = self.trie[suffix_r]
            logger.warning(f'Failed to add suffix trigger `{suffix}`: Conflicts between {tf.__name__} and {other.__name__}')
            return
        self.trie[suffix_r] = tf
        self.trie[zhconv.convert(suffix_r, "zh-hant")] = tf
        logger.debug(f'Succeed to add suffix trigger `{suffix}`')

    def find_handler(self, text_msg: TextMessage):
        raw_msg = text_msg.content
        item = self.trie.longest_prefix(raw_msg)
        if not item:
            return None
        suffix = item.key[::-1]
        text_msg.__setattr__('param', SuffixHandlerParameter(raw_msg, suffix))
        return item.value

class KeywordTrigger(BaseTrigger):
    def __init__(self):
        super().__init__()
        self.allkw = {}

    def add(self, keyword: str, tf: TriggerFunction):
        keyword = normalize_str(keyword)
        if keyword in self.allkw:
            other = self.allkw[keyword]
            logger.warning(f'Failed to add keyword trigger `{keyword}`: Conflicts between {tf.__name__} and {other.__name__}')
            return
        self.allkw[keyword] = tf
        self.allkw[zhconv.convert(keyword, "zh-hant")] = tf
        logger.debug(f'Succeed to add keyword trigger `{keyword}`')

    def find_handler(self, text_msg: TextMessage):
        raw_msg = text_msg.content
        for kw in self.allkw:
            if kw in raw_msg:
                text_msg.__setattr__('param', KeywordHandlerParameter(raw_msg, kw))
                return self.allkw[kw]
        return None

class RexTrigger(BaseTrigger):
    def __init__(self):
        super().__init__()
        self.allrex = {}
      
    def add(self, rex: re.Pattern, tf: TriggerFunction):
        self.allrex[rex] = tf
        logger.debug(f'Succeed to add rex trigger `{rex.pattern}`')

    def find_handler(self, text_msg: TextMessage):
        raw_msg = text_msg.content
        for rex in self.allrex:
            match = rex.search(raw_msg)
            if match:
                text_msg.__setattr__('param', RexHandlerParameter(raw_msg, match))
                return self.allrex[rex]
        return None
