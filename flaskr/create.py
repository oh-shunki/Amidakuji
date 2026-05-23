"""あみだくじ作成制御"""
import json
import random

from werkzeug.security import generate_password_hash
from flask import Blueprint, redirect, render_template, request, url_for, abort

from . import db

from .amida.amida_form import get_and_validate_form
from .amida.amida_map import generate_map
from .utils import amida_id_to_b62
from .conform import conform

bp = Blueprint("create", __name__)

@bp.route("/", methods=("GET", "POST"))
def create():
    """②あみだくじ設定画面制御"""
    if request.method == "POST":
        errors, amida, amida_items = get_and_validate_form(request.form, mode="create")

        if errors:
            amida.pop("admin_password", None)
            amida.pop("user_password", None)
            return render_template("create.html", errors=errors,
                                                  amida=amida,
                                                  amida_items=amida_items)

        admin_password = amida.pop("admin_password")
        amida["admin_password_hash"] = generate_password_hash(admin_password)

        user_password = amida.pop("user_password")
        if user_password:
            amida["user_password_hash"] = generate_password_hash(user_password)
        else:
            amida["user_password_hash"] = None

        # アイテムを足して、ランダムに並び替える
        shortage = amida["line_count"] - len(amida_items)
        if shortage > 0:
            amida_items.extend([""] * shortage)

        random.shuffle(amida_items)

        # マップ生成
        amida_map = generate_map(amida["line_count"])
        amida["amida_map"] = json.dumps(amida_map)

        amida_id = db.create_amida(amida, amida_items)

        if not amida_id:
            abort(500, description="作成するとき、不明なエラーが出ました。")

        amida_id_b62 = amida_id_to_b62(amida_id)

        return redirect(url_for("create.create_conform", amida_id_b62=amida_id_b62))

    return render_template("create.html")

@bp.route("/conform/<amida_id_b62>")
def create_conform(amida_id_b62):
    """③作成確認画面制御"""
    return conform(amida_id_b62, mode="create")
