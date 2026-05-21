"""あみだくじ（未開封）制御"""
from flask import flash, redirect, request, url_for, abort

from .. import db

def unopened(amida):
    """⑤あみだくじ（未開封）画面制御"""
    amida_id = amida.get("amida_id")

    results = {}
    amida_nicknames = db.get_nicknames_from_amida(amida_id) or []
    amida_items = db.get_items_from_amida(amida_id) or []

    results["amida_nicknames"] = amida_nicknames
    results["amida_items"] = amida_items

    return results
