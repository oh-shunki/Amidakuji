"""あみだくじ設定変更制御"""
import random

from werkzeug.security import generate_password_hash, check_password_hash
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for, abort, g
    )

from .user_auth import user_auth_required
from .amida_form import get_and_validate_form

from .. import db
from ..utils import amida_id_b62_to_uuid
from ..conform import conform

bp = Blueprint("update", __name__)

@bp.route("/", methods=("GET", "POST"))
@user_auth_required
def update(amida_id_b62):
    """➉設定変更画面制御"""
    # 開封・削除から飛ばせる場合でも一回許可する
    allowed_once = session.pop(f"{amida_id_b62}_admin_auth_once", None)

    error = None
    if allowed_once:
        error = "パスワードが違います"

    if request.method == "GET" and not allowed_once:
        # 直接 GET の場合はエラー
        abort(403, description="このページに直接アクセスすることはできません。")

    amida = g.amida
    amida_id = g.amida_id

    # 開封済みの場合はエラー
    if amida.get("is_opened"):
        abort(403, description="開封済みのあみだくじは設定を変更できません。")

    # 認証
    admin_password = request.form.get("admin_password", "")
    admin_password_hash = amida.get("admin_password_hash")

    if not (allowed_once or check_password_hash(admin_password_hash, admin_password)):
        flash("正しい管理パスワードを入力してください")

        return redirect(url_for("amida.main", amida_id_b62=amida_id_b62))

    # テンプレートに渡さない項目を削除
    amida.pop("admin_password", None)
    amida.pop("user_password", None)
    amida.pop("amida_map", None)

    # アイテム（当たりのみ）を取得
    amida_items = db.get_items_from_amida(amida_id)
    amida_items = [item for item in amida_items if item["title"]]

    return render_template("amida/update.html", amida_id_b62=amida_id_b62,
                                                amida=amida,
                                                amida_items=amida_items,
                                                error=error)

@bp.route("/do", methods=("POST",))
@user_auth_required
def do_update(amida_id_b62):
    """設定変更実行"""
    amida = g.amida
    amida_id = g.amida_id

    line_count = amida.get("line_count")

    errors, amida, amida_items = get_and_validate_form(request.form,
                                                       mode="update",
                                                       current_line_count=line_count)

    if errors:
        abort(500, description="更新するとき、不明なエラーが出ました。")

    admin_password = amida.pop("admin_password")
    if admin_password:
        amida["admin_password_hash"] = generate_password_hash(admin_password)
    else:
        amida["admin_password_hash"] = None

    user_password = amida.pop("user_password")
    if user_password:
        amida["user_password_hash"] = generate_password_hash(user_password)
    else:
        amida["user_password_hash"] = None

    amida["amida_id"] = amida_id_b62_to_uuid(amida_id_b62)

    # DB からアイテムを取得
    db_items = db.get_items_from_amida(amida_id)
    db_items_title = [item["title"] for item in db_items if item.get("title")]

    # 比較する前にソート
    amida_items.sort()
    db_items_title.sort()

    # アイテムが変更される限り、更新する
    if amida_items == db_items_title:
        amida_items = None

    else:
        # アイテムを足して、ランダムに並び替える
        line_count = db.get_line_count_from_amida(amida_id)
        shortage = line_count - len(amida_items)
        if shortage > 0:
            amida_items.extend([""] * shortage)

        random.shuffle(amida_items)

    success = db.update_amida(amida, amida_items)

    if not success:
        abort(500, description="設定変更するとき、不明なエラーが出ました。")

    session[f"{amida_id_b62}_update_conform_once"] = True

    return redirect(url_for("amida.update.update_conform", amida_id_b62=amida_id_b62))

@bp.route("/conform")
def update_conform(amida_id_b62):
    """⑪変更確認画面制御"""
    if not session.pop(f"{amida_id_b62}_update_conform_once", None):
        abort(403, description="このページに直接アクセスすることはできません。")

    return conform(amida_id_b62, mode="update")
