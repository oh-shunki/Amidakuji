"""あみだくじ（未開封）制御"""
from flask import flash, redirect, request, url_for, abort

from .. import db

def unopened(amida):
    """⑤あみだくじ（未開封）画面制御"""
    amida_id = amida.get("amida_id")

    results = {}
    results["option_hide_items"] = amida.get("option_hide_items")

    return results
