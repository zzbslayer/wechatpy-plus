import logging

from quart import Quart
from quart_cors import cors

app = Quart(__name__)
app = cors(app, allow_origin="*")
app.logger.setLevel(logging.INFO)

app.logger.info("<infra> quart app initialized")
