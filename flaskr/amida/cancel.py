"""あみだくじ抽籤取消制御"""
from werkzeug.security import check_password_hash
from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, abort, g
    )

from .user_auth import user_auth_required

from .. import db
from ..conform import conform

bp = Blueprint("cancel", __name__)

@bp.route("/", methods=("GET",))
@user_auth_required
def cancel(amida_id_b62):
    """⑧取消画面制御"""

    return render_template("amida/cancel.html")

@bp.route("/do", methods=("POST",))
@user_auth_required
def do_cancel(amida_id_b62):
    """取消処理制御"""
    amida = g.amida
    amida_id = g.amida_id

    # 開封済の場合はエラー
    if amida.get("is_opened"):
        abort(403, description="開封済みのあみだくじは抽籤取消できません。")

    line_no = request.form.get("line_no", "")
    line = db.get_line_by_no_from_amida(amida_id, line_no)

    # 状態は DRAWN 以外の場合はエラー
    line_status = db.LineStatus(line.get("status"))
    if line_status != db.LineStatus.DRAWN:
        abort(403, description="この抽籤は取消できません。")

    # 抽籤記録がない場合はエラー
    line_id = line.get("line_id")
    draw = db.get_draw(line_id)
    if draw is None:
        abort(404)

    password = request.form.get("password", "")
    password_hash = draw.get("password_hash", "")

    if password_hash is None:
        abort(404)

    error = None
    if not password:
        error = "パスワードが入力されていません"
    elif not check_password_hash(password_hash, password):
        error = "パスワードが違います"

    if error:
        flash(error)
        return redirect(url_for("amida.cancel.cancel",
                                amida_id_b62=amida_id_b62,
                                line_no=line_no))

    success = db.do_cancel(amida_id, line_no)
    if success:
        flash("成功しました")
    else:
        flash("失敗しました")

    return redirect(url_for("amida.cancel.cancel_conform", amida_id_b62=amida_id_b62))

@bp.route("/conform")
@user_auth_required
def cancel_conform(amida_id_b62):
    """⑦結果確認画面（取消）制御"""
    return conform(amida_id_b62, mode="cancel")
