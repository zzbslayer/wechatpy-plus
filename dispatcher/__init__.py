import json
from functools import wraps
from wechatpy import parse_message, create_reply
from wechatpy.messages import BaseMessage
from typing import List
from json.decoder import JSONDecodeError

from infra.wechat import get_wx_client
from dispatcher.core import TriggerFunction, dispatcher
from utils.logger import logger

''' Sample Message
{
    type: 'event',
    event: 'scan',
    scene_id: {
        "etype": "subscription",
        "module_id": 1, 
        "cron": {
            "second": 1
        }
    }
}
'''

def dispatcher_error_handler(func):
    @wraps(func)
    async def wrapper(msg):
        try:
            return await func(msg)
        except (JSONDecodeError, KeyError) as e:
            logger.exception('400: Bad request')
            #return create_reply('400: Bad request', msg)
        except Exception as e:
            logger.exception('500: Internal Server Error')
            #return create_reply('500: Internal Server Error', msg)
    return wrapper

def message_preprocess(msg):
    msg = parse_message(msg)
    logger.info(f'Receive message {msg.id}: {msg}')
    key_list = [msg.type]
    etype = None
    
    if msg.type == "event":
        if msg.event in ['subscribe_scan', 'scan']:
            event_body = json.loads(msg.scene_id)
            etype = event_body.get('etype')
        key_list.append(msg.event)

    msg.__setattr__('_etype', etype)
    return msg, key_list

async def invoke_trigger_function(tf, msg):
    if tf == None:
        logger.info(f'Message {msg.id} triggered nothing')
        reply_str = None
    else:
        logger.info(f'Message {msg.id} triggered {tf.__name__}')
        reply_str = await tf.func(get_wx_client(), msg)
    return create_reply(reply_str, msg)

@dispatcher_error_handler
async def msg_dispatcher(msg):
    msg, key_list = message_preprocess(msg)
    tf = dispatcher.find_trigger_function(key_list, msg)
    return await invoke_trigger_function(tf, msg)

'''
import submodules here
'''
from . import common
from . import subscription