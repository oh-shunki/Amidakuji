"""あみだくじ抽籤制御"""
from werkzeug.security import generate_password_hash
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for, abort, g
    )

from .amida_map import get_goals
from .user_auth import user_auth_required

from .. import db
from ..conform import conform

bp = Blueprint("draw", __name__)

@bp.route("/")
@user_auth_required
def draw(amida_id_b62):
    """⑥ニックネーム入力画面制御"""
    amida = g.amida
    amida_id = g.amida_id

    # 開封済の場合はエラー
    if amida.get("is_opened"):
        abort(403, description="開封済みのあみだくじは抽籤できません。")

    line_count = amida.get("line_count")

    line_no = request.args.get("line_no")
    if not line_no:
        abort(400, description="線は指定されていません。やり直してください。")

    line = db.get_line_by_no_from_amida(amida_id, line_no)
    if not line:
        abort(400, description="存在のない線は抽籤できません。やり直してくささい。")

    # 状態は READY 以外の場合はエラー
    line_status = db.LineStatus(line.get("status"))
    if line_status != db.LineStatus.READY:
        abort(403, description="この抽籤はできません。")

    return render_template("amida/nickname.html", amida_id_b62=amida_id_b62)

@bp.route("/do", methods=("POST",))
@user_auth_required
def do_draw(amida_id_b62):
    """あみだくじ抽籤作業制御"""
    amida = g.amida
    amida_id = g.amida_id

    line_no = request.form.get("line_no")

    nickname = request.form.get("nickname", "").strip()
    password = request.form.get("password", "")

    error = None
    if not nickname:
        error = "ニックネームは必ず入力して下さい"
    elif not 1 <= len(nickname) <= 6:
        error = "ニックネームは6文字以内で入力してください"
    elif not db.is_nickname_usable(amida_id, nickname):
        error = "使用済みのニックネームです。他のニックネームを入力して、もう一度試してください。"
    elif not password:
        error = "パスワードは必ず入力して下さい"
    elif not (password.isascii() and 1 <= len(password) <= 20):
        error = "パスワードは 1～20 文字で入力してください"

    if error:
        flash(error)
        return redirect(url_for("amida.nickname.nickname",
                                amida_id_b62=amida_id_b62,
                                line_no=line_no))

    password_hash = generate_password_hash(password)

    if not db.do_draw(amida_id, line_no, nickname, password_hash):
        flash("失敗したのでやり直して下さい。")

    flash("成功しました")

    # 自動開封オンの場合は、余った本数チェック
    if amida.get("option_auto_open") and db.get_remain_line_count_from_amida(amida_id) == 0:
        amida_map = amida.get("amida_map")
        goals = get_goals(amida_map)

        db.do_open(amida_id, goals)

    session[f"{amida_id_b62}_draw_conform_once"] = True

    return redirect(url_for("amida.draw.draw_conform", amida_id_b62=amida_id_b62))

@bp.route("/conform")
@user_auth_required
def draw_conform(amida_id_b62):
    """⑦結果確認画面制御"""
    if not session.pop(f"{amida_id_b62}_draw_conform_once", None):
        abort(403, description="このページに直接アクセスすることはできません。")

    return conform(amida_id_b62, mode="draw")
