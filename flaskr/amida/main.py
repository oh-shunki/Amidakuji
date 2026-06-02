"""あみだくじ全体制御"""
import random

from werkzeug.security import generate_password_hash, check_password_hash
from flask import (
    flash, redirect, render_template, request, session, url_for, abort, g
    )

from . import bp
from .amida_map import get_goals
from .user_auth import user_auth_required

from .. import db
from ..conform import conform

@bp.route("/")
@user_auth_required
def main(amida_id_b62):
    """あみだくじ画面制御
        ⑤あみだくじ画面（未開封）
        ⑨あみだくじ画面（開封済）
    """
    amida = g.amida
    amida_id = g.amida_id

    amida.pop("admin_password_hash", None)
    amida.pop("user_password_hash", None)

    amida["amida_lines_status"] = db.get_lines_status_str_from_amida(amida_id) or []
    amida["amida_nicknames"] = db.get_nicknames_from_amida(amida_id) or []
    amida["amida_items"] = db.get_items_from_amida(amida_id) or []

    if amida.get("is_opened"):
        # 開封済
        return render_template("amida/opened.html", amida_id_b62=amida_id_b62,
                                                    amida=amida)

    # 未開封

    # あみだくじマップを本数だけにする
    amida_map = amida.pop("amida_map", None)
    amida["amida_map"] = [[[0]] for _ in amida_map]

    # option_hide_items オンの場合
    if amida.get("option_hide_items"):
        # アイテムをランダムに並び替える
        random.shuffle(amida["amida_items"])

    return render_template("amida/unopened.html", amida_id_b62=amida_id_b62,
                                                  amida=amida)

@bp.route("/do_open", methods=("POST",))
@user_auth_required
def do_open(amida_id_b62):
    """あみだくじ開封作業制御"""
    amida = g.amida
    amida_id = g.amida_id

    # 開封済みの場合はエラー
    if amida.get("is_opened"):
        abort(403, description="このあみだくじはすでに開封済みです。")

    # 認証
    admin_password = request.form.get("admin_password")
    admin_password_hash = db.get_admin_password_hash_from_amida(amida_id)

    if check_password_hash(admin_password_hash, admin_password):
        # 認証成功、開封する

        amida_map = amida.get("amida_map")
        goals = get_goals(amida_map)

        if not db.do_open(amida_id, goals):
            abort(500, description="開封するとき、不明なエラーが出ました。")

        session[f"{amida_id_b62}_do_open_conform_once"] = True

        return redirect(url_for("amida.do_open_conform", amida_id_b62=amida_id_b62))

    # 認証エラー
    # 設定変更画面からの場合は元の画面にリダイレクト
    referrer = request.referrer
    if referrer and "/update" in referrer:
        session[f"{amida_id_b62}_admin_auth_once"] = True

        return redirect(url_for("amida.update.update", amida_id_b62=amida_id_b62))

    flash("正しい管理パスワードを入力してください")

    return redirect(url_for("amida.main", amida_id_b62=amida_id_b62))

@bp.route("/delete", methods=("POST",))
@user_auth_required
def delete_amida(amida_id_b62):
    """あみだくじ削除作業制御"""
    amida_id = g.amida_id

    # 認証
    admin_password = request.form.get("admin_password")
    admin_password_hash = db.get_admin_password_hash_from_amida(amida_id)

    if check_password_hash(admin_password_hash, admin_password):
        # 認証成功、削除する

        if not db.delete_amida(amida_id):
            abort(500, description="削除するとき、不明なエラーが出ました。")

        session["delete_conform_once"] = True

        return redirect(url_for("index.delete_conform", amida_id_b62=amida_id_b62))

    # 認証エラー、元の画面にリダイレクト
    session[f"{amida_id_b62}_admin_auth_once"] = True

    return redirect(url_for("amida.update.update", amida_id_b62=amida_id_b62))

@bp.route("/do_open/conform")
@user_auth_required
def do_open_conform(amida_id_b62):
    """⑫開封確認画面制御"""
    if not session.pop(f"{amida_id_b62}_do_open_conform_once", None):
        abort(403, description="このページに直接アクセスすることはできません。")

    return conform(amida_id_b62, mode="do_open")
