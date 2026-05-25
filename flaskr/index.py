"""初期画面制御"""
from flask import Blueprint, render_template

from .conform import conform

bp = Blueprint("index", __name__)

@bp.route("/")
def index():
    """①初期画面制御"""
    return render_template("index.html")

@bp.route("/delete/conform")
def delete_conform():
    """⑬削除確認画面制御"""
    return conform(mode="delete")
