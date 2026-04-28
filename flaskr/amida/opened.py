"""あみだくじ（開封済）制御"""
from flask import flash, redirect, request, url_for, abort

from .. import db

def opened(amida):
    """⑨あみだくじ（開封済）画面制御"""
    amida_id = amida.get("amida_id")

    results = {}

    return results

