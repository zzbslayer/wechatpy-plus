import traceback
from quart import abort
from functools import wraps
from wechatpy import parse_message, create_reply

from wechatpy.exceptions import InvalidSignatureException, InvalidAppIdException

from utils.logger import logger

def controller(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            res =  await func(*args, **kwargs)
            return res
        except (InvalidSignatureException, InvalidAppIdException):
            logger.exception('403: Permission denied')
            abort(403)
        except Exception as e:
            logger.exception('500: Internal Server Error')
            abort(500)
    return wrapper

def api_controller(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            res =  await func(*args, **kwargs)
            return { 'code': 200, 'data': res, 'msg': 'success' }
        except (InvalidSignatureException, InvalidAppIdException):
            logger.exception('403: Permission denied')
            return { 'code': 403, 'msg': 'Permission Denied' }
        except Exception as e:
            logger.exception('500: Internal Server Error')
            return { 'code': 500, 'msg': 'Internal Server Error' }
    return wrapper