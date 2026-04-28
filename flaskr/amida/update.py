from flask import Blueprint, render_template
from . import bp

bp = Blueprint("update", __name__)

@bp.route("/update")
def update(amida_id_b62):
    return render_template("amida/update.html")
