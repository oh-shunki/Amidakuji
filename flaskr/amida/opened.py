"""あみだくじ（開封済）制御"""
from flask import flash, redirect, request, url_for, abort

from .. import db

def opened(amida):
    """⑨あみだくじ（開封済）画面制御"""
    amida_id = amida.get("amida_id")

    db_lines = db.get_lines_from_amida(amida_id)
    db_items = db.get_items_from_amida(amida_id)

    items = db_items if db_items else []

    lines = []

    for line in db_lines:
        draw = db.get_draw_from_line(line["line_id"])

        if draw:
            nickname = draw["nickname"]
        else:
            nickname = "未抽籤"

        lines.append({
            "line_id": line["line_id"],
            "nickname": nickname
        })

    results = {}
    results["amida_id"] = amida_id
    results["amida_lines"] = lines
    results["amida_items"] = items

    return results
