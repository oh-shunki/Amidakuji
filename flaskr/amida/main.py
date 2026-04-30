"""あみだくじ全体制御"""
from werkzeug.security import check_password_hash
from flask import (
    flash, redirect, render_template, request, session, url_for, abort
    )

from . import bp
from .user_auth import user_auth_required

from .. import db
from ..utils import amida_id_to_b62, amida_id_b62_to_uuid
from ..conform import conform

@bp.route("/")
@user_auth_required
def main(amida_id_b62):
    """あみだくじ全体画面制御"""
    from .opened import opened
    from .unopened import unopened

    try:
        amida_id = amida_id_b62_to_uuid(amida_id_b62)
    except ValueError:
        # このIDのはBase62型ではない
        abort(404)

    amida = db.get_amida(amida_id)

    # このIDは存在していない
    if amida is None:
        abort(404)

    # 開封状態分岐
    is_opened = amida.get("is_opened")
    if is_opened:
        results = opened(amida)
        return render_template("amida/opened.html", results=results)

    results = unopened(amida)
    return render_template("amida/unopened.html", results=results)

@bp.route("/do_draw", methods=("POST",))
def do_draw(amida_id_b62):
    """あみだくじ抽籤作業制御"""
    try:
        amida_id = amida_id_b62_to_uuid(amida_id_b62)
    except ValueError:
        # このIDのはBase62型ではない
        abort(404)

    amida = db.get_amida(amida_id)

    # このIDは存在していない
    if amida is None:
        abort(404)

    # すでに開封済み
    is_opened = amida.get("is_opened")
    if is_opened:
        abort(409)

    # 抽籤処理はここ

    if successed:
        # 抽籤成功
        flash("成功しました")
        return redirect(url_for("amida.do_draw.conform", amida_id_b62=amida_id_b62))

    # 抽籤失敗
    flash("失敗しました")
    return redirect(url_for("amida.do_draw.conform", amida_id_b62=amida_id_b62))

@bp.route("/do_open", methods=("POST",))
def do_open(amida_id_b62):
    """あみだくじ開封作業制御"""
    try:
        amida_id = amida_id_b62_to_uuid(amida_id_b62)
    except ValueError:
        # このIDのはBase62型ではない
        abort(404)

    amida = db.get_amida(amida_id)

    # このIDは存在していない
    if amida is None:
        abort(404)

    # すでに開封済み
    is_opened = amida.get("is_opened")
    if is_opened:
        abort(409)

    # 認証
    admin_password = request.form.get("admin_password")
    admin_password_hash = db.get_admin_password_hash_from_amida(amida_id)

    if check_password_hash(admin_password_hash, admin_password):
        # 認証成功

        # 開封処理はここ
        return redirect(url_for("amida.do_open.conform", amida_id_b62=amida_id_b62))

    # 認証エラー
    flash("正しい管理パスワードを入力してください")
    return redirect(url_for("amida.main", amida_id_b62=amida_id_b62))

@bp.route("do_draw/conform")
def do_draw_conform(amida_id_b62):
    """⑦結果確認画面制御"""
    return conform(amida_id_b62, mode="do_draw")

@bp.route("do_open/conform")
def do_open_conform(amida_id_b62):
    """⑫開封確認画面制御"""
    return conform(amida_id_b62, mode="do_open")


# @bp.route("/opened_test")
# def opened_test(amida_id_b62):
#     results = {
#         "amida_id":"test_id",
#         "lines": [
#             {"line_id":1,"name":"Aさん"},
#             {"line_id":2,"name":"Bさん"}
#         ]
#     }

#     return render_template("amida/opened.html",results=results)