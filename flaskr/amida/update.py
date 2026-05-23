from flask import render_template
from . import bp
from .user_auth import user_auth_required

@bp.route("/update")
@user_auth_required
def update(amida_id_b62):
    return render_template("amida/update.html")
