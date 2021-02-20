from wechatpy.client import WeChatClient
from utils.logger import logger

wx_client = None

def set_wx_client(client):
    global wx_client
    wx_client = client

def new_wx_client(id, secret):
    return WeChatClient(id, secret)

def get_wx_client():
    return wx_client

def init_wx_client(id, secret):
    client = new_wx_client(id, secret)
    set_wx_client(client)
    logger.info("<infra> wechat client initialized")