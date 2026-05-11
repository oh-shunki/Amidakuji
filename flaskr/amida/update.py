from flask import Blueprint, render_template

from . import bp
from .user_auth import user_auth_required

bp = Blueprint("update", __name__)

@bp.route("/update")
@user_auth_required
def update(amida_id_b62):
    return render_template("amida/update.html")
