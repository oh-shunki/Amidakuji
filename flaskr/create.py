"""あみだくじ作成制御"""
from flask import Blueprint, redirect, render_template, request, url_for

from . import db
from .utils import amida_id_to_b62, amida_id_b62_to_uuid
from .conform import conform

bp = Blueprint("create", __name__)

@bp.route("/", methods=("GET", "POST"))
def create():
    """②あみだくじ設定画面制御"""
    if request.method == "POST":
        pass
        # 作成処理はここ
        # amida_id = db.create_amida(...)
        # if amida_id:
        #   amida_id_b62 = amida_id_to_b62(amida_id)
        #
        # return redirect(url_for("create.create_conform", amida_id_b62=amida_id_b62))

    return render_template("create.html")

@bp.route("/conform")
def create_conform():
    """③作成確認画面制御"""
    amida_id_b62 = request.args.get("amida_id_b62")
    return conform(amida_id_b62, mode="create")
