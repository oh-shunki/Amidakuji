from flask import Blueprint, render_template

from .user_auth import user_auth_required

bp = Blueprint("cancel", __name__)

@bp.route("/cancel")
@user_auth_required
def cancel(amida_id_b62):
    return render_template("amida/cancel.html")
