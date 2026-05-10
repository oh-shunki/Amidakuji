"""あみだくじ（開封済）制御"""
from flask import flash, redirect, request, url_for, abort

from .. import db

def opened(amida):
    """⑨あみだくじ（開封済）画面制御"""
    amida_id = amida.get("amida_id")

    print("opened.pyに入りました")
    print(amida)

    db_lines = db.get_lines_from_amida(amida_id)
    print("DBから取得したlines",db_lines)

    db_items = db.get_items_from_amida(amida_id)
    print("DBから取得したitems",db_items)

    # lines = db.get_lines_from_amida(amida_id)

    lines = []

    if db_lines:
        for line in db_lines:
            draw = db.get_draw_from_line(line["line_id"])
            print("線ごとの抽籤情報",draw)
                
            lines.append({
                "line_id": line["line_id"],
                "nickname":"未抽籤"
            })
    else:   
        lines = [
            {"line_id":1,"nickname":"Aさん"},
            {"line_id":2,"nickname":"Bさん"}
        ]

    results = {}
    results["amida_id"] = amida_id
    results["lines"] = lines

    return results

if __name__ == "__main__":
    test_amida={
        "amida_id": "test-id"
    }

    print(opened(test_amida))

