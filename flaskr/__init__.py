from flask import Flask, redirect, render_template

from . import config
from . import db

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
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("500.html", error=e), 500

    return app
