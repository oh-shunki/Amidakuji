"""あみだくじ全体制御"""
import json
import random

from werkzeug.security import generate_password_hash, check_password_hash
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
    """あみだくじ画面制御
        ⑤あみだくじ画面（未開封）
        ⑨あみだくじ画面（開封済）
    """
    try:
        amida_id = amida_id_b62_to_uuid(amida_id_b62)
    except ValueError:
        # このIDのはBase62型ではない
        abort(404)

    amida = db.get_amida(amida_id)

    # このIDは存在していない
    if amida is None:
        abort(404)

    amida.pop("admin_password_hash", None)
    amida.pop("user_password_hash", None)

    amida["amida_lines_status"] = db.get_lines_status_str_from_amida(amida_id) or []
    amida["amida_nicknames"] = db.get_nicknames_from_amida(amida_id) or []
    amida["amida_items"] = db.get_items_from_amida(amida_id) or []

    amida_map_json = amida.pop("amida_map", None)
    amida_map = json.loads(amida_map_json)

    # 開封済
    if amida.get("is_opened"):
        amida["amida_map"] = amida_map

        return render_template("amida/opened.html", amida_id_b62=amida_id_b62,
                                                    amida=amida)

    # 未開封
    option_hide_items = amida.get("option_hide_items")

    # option_hide_items オンの場合はアイテムをランダムに並び替える
    if option_hide_items:
        random.shuffle(amida["amida_items"])

    # あみだくじマップを本数だけにする
    amida["amida_map"] = [[[0]] for _ in amida_map]

    return render_template("amida/unopened.html", amida_id_b62=amida_id_b62,
                                                  amida=amida)

@bp.route("/do_draw", methods=("POST",))
@user_auth_required
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

    # 開封済みの場合はエラー
    if amida.get("is_opened"):
        abort(403, description="開封済みのあみだくじは抽籤できません。")

    line_count = amida.get("line_count")

    # line_no の検証
    try:
        line_no = int(request.form.get("line_no"))
        if not 0 <= line_no < line_count:
            raise ValueError("Invalid line_no")

    except (ValueError, TypeError) as e:
        abort(400, description=e)

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

    success = db.do_draw(amida_id, line_no, nickname, password_hash)
    if success:
        flash("成功しました")
    else:
        flash("失敗しました")

    return redirect(url_for("amida.do_draw_conform", amida_id_b62=amida_id_b62))

@bp.route("/do_open", methods=("POST",))
@user_auth_required
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

@bp.route("/delete", methods=("POST",))
@user_auth_required
def delete_amida(amida_id_b62):
    """あみだくじ削除作業制御"""
    try:
        amida_id = amida_id_b62_to_uuid(amida_id_b62)
    except ValueError:
        # このIDのはBase62型ではない
        abort(404)

    amida = db.get_amida(amida_id)

    # このIDは存在していない
    if amida is None:
        abort(404)

    # 認証
    admin_password = request.form.get("admin_password")
    admin_password_hash = db.get_admin_password_hash_from_amida(amida_id)

    if check_password_hash(admin_password_hash, admin_password):
        # 認証成功、削除する

        if not db.delete_amida(amida_id):
            abort(500, description="削除するとき、不明なエラーが出ました。")

        return redirect(url_for("index.delete_conform", amida_id_b62=amida_id_b62))

    # 認証エラー
    flash("正しい管理パスワードを入力してください")

    session[f"{amida_id_b62}_admin_auth_once"] = True

    return redirect(url_for("amida.update.update", amida_id_b62=amida_id_b62))

@bp.route("/do_draw/conform")
@user_auth_required
def do_draw_conform(amida_id_b62):
    """⑦結果確認画面制御"""
    return conform(amida_id_b62, mode="do_draw")

@bp.route("/do_open/conform")
@user_auth_required
def do_open_conform(amida_id_b62):
    """⑫開封確認画面制御"""
    return conform(amida_id_b62, mode="do_open")
