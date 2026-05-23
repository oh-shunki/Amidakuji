from flask import Blueprint

bp = Blueprint("amida", __name__)

from . import main

# Blueprintの登録
from . import user_auth
bp.register_blueprint(user_auth.bp, url_prefix="/user_auth")

from . import nickname
bp.register_blueprint(nickname.bp, url_prefix="/nickname")

from . import update
bp.register_blueprint(update.bp, url_prefix="/update")

#from . import cancel
#bp.register_blueprint(cancel.bp, url_prefix="/cancel")

