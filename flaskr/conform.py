"""③⑦⑪⑫⑬確認画面制御"""
from flask import render_template, abort

from . import db
from .utils import amida_id_b62_to_uuid

def conform(amida_id_b62 = None, mode=None):
    """確認画面処理"""
    if amida_id_b62:
        try:
            amida_id = amida_id_b62_to_uuid(amida_id_b62)
        except ValueError:
            # このIDのはBase62型ではない
            abort(404)

        amida = db.get_amida(amida_id)

        # このIDは存在していない
        if amida is None:
            abort(404)

    return render_template("conform.html", amida_id_b62=amida_id_b62, mode=mode)
