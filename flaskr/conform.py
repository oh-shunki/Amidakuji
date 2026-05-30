"""③⑦⑪⑫⑬確認画面制御"""
from flask import render_template


def conform(amida_id_b62 = None, mode=None):
    """確認画面処理"""
    if amida_id_b62:
        # 循環インポート回避
        from .amida import validate_amida_id

        # amida_id_b62 ある場合は、検証をする
        validate_amida_id()

    return render_template("conform.html", amida_id_b62=amida_id_b62, mode=mode)
