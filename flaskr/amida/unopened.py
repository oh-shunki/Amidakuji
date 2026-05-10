"""あみだくじ（未開封）制御"""
from flask import flash, redirect, request, url_for, abort

from .. import db

def unopened(amida):
    """⑤あみだくじ（未開封）画面制御"""
    amida_id = amida.get("amida_id")

    db_lines = db.get_lines_from_amida(amida_id)
    results = {}
    results["amida_lines"] = []
    results["option_hide_items"] = amida.get("option_hide_items")

    for line in db_lines:
        status = db.LineStatus(line.get("status"))
        if status == db.LineStatus.READY:
            nickname = None
        else:
            nickname = db.get_draw_nickname_from_line(line.get("line_id"))

        results["amida_lines"].append(nickname)


    return results
