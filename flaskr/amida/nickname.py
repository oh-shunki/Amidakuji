"""ニックネーム入力制御"""
from flask import (
    Blueprint, render_template
    )

from . import bp
from .user_auth import user_auth_required

bp = Blueprint("nickname", __name__)

@bp.route("/")
@user_auth_required
def nickname(amida_id_b62):
    """⑥ニックネーム入力画面制御"""

    return render_template("amida/nickname.html", amida_id_b62=amida_id_b62)
