# -*- coding: utf-8 -*-
from infra.quart_app import app
from infra.scheduler import init_scheduler
#from infra.mysql import init_pool, init_tables
from infra.wechat import init_wx_client
from utils.logger import logger

import os, asyncio, json
from quart import request

from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature

from dispatcher import msg_dispatcher
from service import wechat_service
from utils.deco import controller, api_controller
from config import APP_ID, APP_SECRET, APP_TOKEN, APP_AES_KEY

@app.before_serving
async def startup():
    loop = asyncio.get_event_loop()
    init_scheduler(loop)
    # await init_pool(loop)
    # await init_tables()
    init_wx_client(APP_ID, APP_SECRET)

@app.route("/wechat", methods=["GET", "POST"])
@controller
async def wechat():
    signature = request.args.get("signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")
    encrypt_type = request.args.get("encrypt_type", "raw")
    msg_signature = request.args.get("msg_signature", "")
    request_body = await request.data
    check_signature(APP_TOKEN, signature, timestamp, nonce)

    if request.method == "GET":
        echo_str = request.args.get("echostr", "")
        return echo_str

    # POST request
    if encrypt_type == "raw":
        # plaintext mode
        reply = await msg_dispatcher(request_body)
        if reply != None:
            return reply.render()
        else:
            return ""
    else:
        # encryption mode
        from wechatpy.crypto import WeChatCrypto
        crypto = WeChatCrypto(APP_TOKEN, APP_AES_KEY, APP_ID)
        msg = crypto.decrypt_message(request_body, msg_signature, timestamp, nonce)
        reply = await msg_dispatcher(msg)
        return crypto.encrypt_message(reply.render(), nonce, timestamp)

@app.route("/api/generateQrCode", methods=["POST"])
@api_controller
async def getSubcriptionQrCode():
    request_body = await request.get_json()
    return await wechat_service.generate_qr_code(request_body)

if __name__ == '__main__':
    app.run('0.0.0.0', 80)