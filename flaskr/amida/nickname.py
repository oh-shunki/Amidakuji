"""ニックネーム入力制御"""
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for, abort
    )

from . import bp
from .user_auth import user_auth_required

from .. import db
from ..utils import amida_id_to_b62, amida_id_b62_to_uuid

bp = Blueprint("nickname", __name__)


@bp.route("/")
@user_auth_required
def nickname(amida_id_b62):
    """⑥ニックネーム入力画面制御"""
    try:
        amida_id = amida_id_b62_to_uuid(amida_id_b62)
    except ValueError:
        # このIDのはBase62型ではない
        abort(404)

    amida = db.get_amida(amida_id)

    # このIDは存在していない
    if amida is None:
        abort(404)

    # チェック：nickname, password
    # if エラー: flash()
    # else: return redirect(url_for("amida.do_draw.conform", amida_id_b62=amida_id_b62))

    return render_template("amida/nickname.html", amida_id_b62=amida_id_b62)
