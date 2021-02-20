from dispatcher.core import dispatcher

@dispatcher.event.subscribe
@dispatcher.event.subscribe_scan
async def subscrpition_hello_world(wx_client, event_msg):
    user_id = event_msg.source
    wx_client.message.send_text(user_id=user_id, content='hello world')