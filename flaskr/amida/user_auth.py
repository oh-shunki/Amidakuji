"""ユーザ認証制御"""
import functools

from werkzeug.security import check_password_hash
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for, abort
    )

from .. import db
from ..utils import amida_id_to_b62, amida_id_b62_to_uuid

bp = Blueprint("user_auth", __name__)

@bp.route("/", methods=("GET", "POST"))
def user_auth(amida_id_b62):
    """④ユーザ認証画面制御"""
    try:
        amida_id = amida_id_b62_to_uuid(amida_id_b62)
    except ValueError:
        # このIDのはBase62型ではない
        abort(404)

    amida = db.get_amida(amida_id)

    # このIDは存在していない
    if amida is None:
        abort(404)

    user_password_hash = db.get_user_password_hash_from_amida(amida_id)

    if user_password_hash is None:
        abort(404)

    # すでに認証済みの場合
    if user_password_hash == "" or session.get(f"{amida_id_b62}_user_auth"):
        return redirect(url_for("amida.main", amida_id_b62=amida_id_b62))

    # 認証送信
    if request.method == "POST":
        user_password = request.form.get("user_password")

        if check_password_hash(user_password_hash, user_password):
            session[f"{amida_id_b62}_user_auth"] = True

            # 認証成功
            next_url = request.args.get("next_url")
            return redirect(next_url or url_for("amida.main", amida_id_b62=amida_id_b62))

        # 認証エラー
        flash("パスワードが正しくありません")
        return render_template("amida/user_auth.html",
                               amida_id_b62=amida_id_b62,
                               title=amida.get("title"))

    # 認証ページ
    return render_template("amida/user_auth.html",
                           amida_id_b62=amida_id_b62,
                           title=amida.get("title"))

def user_auth_required(view):
    """ユーザ認証制御関数"""
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        amida_id_b62 = kwargs.get("amida_id_b62")
        try:
            amida_id = amida_id_b62_to_uuid(amida_id_b62)
        except ValueError:
            # このIDのはBase62型ではない
            abort(404)

        user_password_hash = db.get_user_password_hash_from_amida(amida_id)
        if user_password_hash:
            if not session.get(f"{amida_id_b62}_user_auth"):
                return redirect(url_for("amida.user_auth.user_auth",
                                        amida_id_b62=amida_id_b62,
                                        next_url=request.url))

        return view(*args, **kwargs)

    return wrapped_view
