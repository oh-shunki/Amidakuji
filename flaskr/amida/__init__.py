from flask import Blueprint, request, abort, g

from .. import db
from ..utils import amida_id_b62_to_uuid

bp = Blueprint("amida", __name__)

from . import main

# Blueprintの登録
from . import user_auth

bp.register_blueprint(user_auth.bp, url_prefix="/user_auth")

from . import draw
bp.register_blueprint(draw.bp, url_prefix="/draw")

from . import update
bp.register_blueprint(update.bp, url_prefix="/update")

from . import cancel
bp.register_blueprint(cancel.bp, url_prefix="/cancel")

@bp.before_request
def validate_amida_id():
    """amida_id の有効性検証"""
    amida_id_b62 = request.view_args.get("amida_id_b62") if request.view_args else None

    try:
        amida_id = amida_id_b62_to_uuid(amida_id_b62)
    except ValueError:
        # ID 不正の場合はエラー
        abort(404)

    amida = db.get_amida(amida_id)

    # あみだくじが存在しない場合はエラー
    if not amida:
        abort(404)

    g.amida = amida
    g.amida_id = amida_id
