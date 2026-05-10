import re
from flask import Flask, redirect, render_template, request
from werkzeug.exceptions import HTTPException

from . import config
from . import db
from .utils import amida_id_b62_to_uuid

def create_app():
    app = Flask(__name__)
    app.config.from_object(config.Config)

    # Blueprintの登録
    from . import index
    app.register_blueprint(index.bp)

    from . import amida
    app.register_blueprint(amida.bp, url_prefix="/<string:amida_id_b62>")

    from . import create 
    app.register_blueprint(create.bp, url_prefix="/create")

    app.teardown_appcontext(db.close_db)

    # エラーハンドラー
    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        if isinstance(e, HTTPException):
            error = {"code": e.code, "description": e.description}
        else:
            error = {"code": 500, "description": "予期せぬエラーが発生しました"}

        view_args = request.view_args or {}
        amida_id_b62 = view_args.get("amida_id_b62")

        parts = request.path.split("/")
        if not amida_id_b62 and len(parts) >= 2:
            amida_id_b62 = parts[1]

        if amida_id_b62:
            if re.fullmatch(r'[a-zA-Z0-9]{20,22}', amida_id_b62):
                try:
                    amida_id_b62_to_uuid(amida_id_b62)
                except (ValueError, TypeError):
                    amida_id_b62 = None
            else:
                amida_id_b62 = None

        return render_template("error.html", error=error, amida_id_b62=amida_id_b62), error["code"]

    return app
