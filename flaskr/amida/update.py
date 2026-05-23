import random

from werkzeug.security import generate_password_hash
from flask import Blueprint, redirect, render_template, request, url_for, abort

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
    try:
        amida_id = amida_id_b62_to_uuid(amida_id_b62)
    except ValueError:
        # このIDのはBase62型ではない
        abort(404)

    amida = db.get_amida(amida_id)

    # このIDは存在していない
    if amida is None:
        abort(404)

    if request.method == "POST":
        errors, amida, amida_items = get_and_validate_form(request.form, mode="update")

        if errors:
            amida.pop("admin_password", None)
            amida.pop("user_password", None)
            return render_template("update.html", errors=errors,
                                                  amida=amida,
                                                  amida_items=amida_items)

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

        # アイテムを足して、ランダムに並び替える
        line_count = db.get_line_count_from_amida(amida_id)
        shortage = line_count - len(amida_items)
        if shortage > 0:
            amida_items.extend([""] * shortage)

        random.shuffle(amida_items)

        success = db.update_amida(amida, amida_items)

        if not success:
            abort(500, description="設定変更するとき、不明なエラーが出ました。")

        return redirect(url_for("amida.update.update_conform", amida_id_b62=amida_id_b62))

    # テンプレートに渡さない項目を削除
    amida.pop("admin_password", None)
    amida.pop("user_password", None)
    amida.pop("amida_map", None)

    # アイテム（当たりのみ）を取得
    amida_items = db.get_items_from_amida(amida_id)
    amida_items = [item for item in amida_items if item["title"]]
    print(amida_items)

    return render_template("amida/update.html", amida=amida, amida_items=amida_items)

@bp.route("/conform")
def update_conform(amida_id_b62):
    """⑪変更確認画面制御"""
    return conform(amida_id_b62, mode="update")
