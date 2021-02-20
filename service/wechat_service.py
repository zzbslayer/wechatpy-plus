import json, datetime

from infra.wechat import get_wx_client
from config import QR_CODE_EXPIRATION
from utils.logger import logger

async def generate_qr_code(body: dict) -> str:
   json_body = {
      "expire_seconds": QR_CODE_EXPIRATION, 
      "action_name": "QR_STR_SCENE", 
      "action_info": {
         "scene": {
            "scene_str": json.dumps(body)
         }
      }
   }
   ticket = await get_qr_code_ticket(json_body)
   return { 
      'url': await get_qr_code_url(ticket),
      "expire_seconds": QR_CODE_EXPIRATION,
   }

async def get_qr_code_ticket(json_body: dict) -> str:
   '''Example
   {
      "expire_seconds": 604800, 
      "action_name": "QR_STR_SCENE", 
      "action_info": {
         "scene": {
            "scene_str": "test"
         }
      }
   }
   '''
   client = get_wx_client()
   logger.info(f"Generate qrcode of body: {json.dumps(json_body)}")
   return client.qrcode.create(json_body)["ticket"]

async def get_qr_code_url(ticket):
   client = get_wx_client()
   return client.qrcode.get_url(ticket)