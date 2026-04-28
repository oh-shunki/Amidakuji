"""初期画面制御"""
from flask import Blueprint, render_template

bp = Blueprint("index", __name__)

@bp.route("/")
def index():
    """①初期画面制御"""
    return render_template("index.html")
