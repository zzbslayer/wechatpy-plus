from dispatcher.core import dispatcher

HELP_MSG='''微信公众号帮助
[帮助]: 帮助信息
[发送其他任意文本]: 复读机
'''
@dispatcher.text.on_fullmatch(fullmatch=["帮助", "help"])
async def help(wx_client, text_msg):
    user_id = text_msg.source
    wx_client.message.send_text(user_id=user_id, content=HELP_MSG)

@dispatcher.text
async def echo(wx_client, text_msg):
    user_id = text_msg.source
    wx_client.message.send_text(user_id=user_id, content=text_msg.content)
