from flask import Blueprint, render_template

bp = Blueprint("cancel", __name__)

@bp.route("/cancel")
def cancel(amida_id_b62):
    return render_template("amida/cancel.html")
