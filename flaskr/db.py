"""モデル"""
import uuid
from enum import Enum

import pymysql

from flask import current_app, g, abort

def get_db():
    if "db" not in g:
        try:
            g.db = pymysql.connect(
                host=current_app.config["DB_HOST"],
                user=current_app.config["DB_USER"],
                password=current_app.config["DB_PASSWORD"],
                database=current_app.config["DB_NAME"],
                cursorclass=pymysql.cursors.DictCursor
            )
        except pymysql.Error:
            abort(500, description="データベース接続に失敗しました。")
    return g.db

def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()

# --- DB操作関数 ---

## ---- あみだくじ操作関数 ----

def create_amida(amida: dict, items: list) -> uuid.UUID:
    """あみだくじを作成
    Return
        成功：あみだくじID
        失敗：Noone
    """
    amida_id = uuid.uuid7()
    title = amida.get("title")
    line_count = amida.get("line_count")
    option_auto_open = amida.get("option_auto_open", False)
    option_hide_items = amida.get("option_hide_items", True)
    admin_password_hash = amida.get("admin_password_hash")
    user_password_hash = amida.get("user_password_hash", None)
    is_opened = False

    db = get_db()
    try:
        with db.cursor() as cursor:
            # あみだくじ作成
            cursor.execute("""
                    INSERT INTO amidas (amida_id, title, line_count,
                        option_auto_open, option_hide_items,
                        admin_password_hash, user_password_hash,
                        is_opened)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (amida_id, title, line_count,
                        option_auto_open, option_hide_items,
                        admin_password_hash, user_password_hash,
                        is_opened)
                    )

            # 線作成
            for line_no in range(line_count):
                cursor.execute(
                        "INSERT INTO amida_lines (amida_id, line_no)"
                        "VALUES (%s, %s)", (amida_id, line_no)
                        )

            # アイテム作成
            for item in items:
                cursor.execute(
                        "INSERT INTO amida_items (amida_id, title)"
                        "VALUES (%s, %s)", (amida_id, item)
                        )

            if len(items) < line_count:
                item = "はずれ"
                cursor.execute(
                        "INSERT INTO amida_items (amida_id, title)"
                        "VALUES (%s, %s)", (amida_id, item)
                        )

        db.commit()
        return amida_id

    except pymysql.Error:
        db.rollback()
        return None

def update_amida(amida_id, title, admin_password_hash, user_password_hash,
                 option_auto_open, option_hide_items) -> bool:
    """あみだくじを更新
    Return
        成功：True
        失敗：False
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("UPDATE ...")

        db.commit()
        rows_updated = cursor.rowcount
        return True if rows_updated > 0 else False

    except pymysql.Error:
        db.rollback()
        return False

def delete_amida(amida_id):
    """あみだくじを削除
    Return
        成功：True
        失敗：False
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("...")

        db.commit()
        return True

    except pymysql.Error:
        db.rollback()
        return False

def get_amida(amida_id) -> dict:
    """あみだくじを取得
    Return
        成功：あみだくじの情報
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT * FROM amidas WHERE amida_id = %s",
                    (amida_id,)
            )
            result = cursor.fetchone()
            return result if result else None

    except pymysql.Error:
        return None

def get_line_count_from_amida(amida_id) -> int:
    """あみだくじに線の本数を取得
    Return
        成功：本数
        失敗：0
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT line_count FROM amidas WHERE amida_id = %s",
                (amida_id,)
            )
            result = cursor.fetchone()
            if result is None:
                return 0

            line_count = result.get("line_count")
            return line_count if line_count is not None else 0

    except pymysql.Error:
        return None

def get_option_auto_open_from_amida(amida_id) -> bool:
    """あみだくじに自動開封設定を取得
    Return
        成功：bool
        失敗：False (Default)
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT option_auto_open FROM amidas WHERE amida_id = %s",
                (amida_id,)
            )
            result = cursor.fetchone()
            return result["option_auto_open"] if result else False

    except pymysql.Error:
        return False

def get_option_hide_items_from_amida(amida_id) -> bool:
    """あみだくじに線の隠す設定を取得
    Return
        成功：bool
        失敗：True (Default)
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT option_hide_items FROM amidas WHERE amida_id = %s",
                (amida_id,)
            )
            result = cursor.fetchone()

            return result["option_hide_items"] if result else True

    except pymysql.Error:
        return True

def get_admin_password_hash_from_amida(amida_id) -> str:
    """あみだくじに管理者パスワードハッシュを取得
    Return
        パスワードあり：パスワードハッシュ
        パスワードなし：空文字列
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT admin_password_hash FROM amidas WHERE amida_id = %s",
                (amida_id,)
            )
            result = cursor.fetchone()
            if result is None:
                return None

            admin_password_hash = result.get("admin_password_hash")
            return admin_password_hash if admin_password_hash else ""

    except pymysql.Error:
        return None

def get_user_password_hash_from_amida(amida_id) -> str:
    """あみだくじに利用者パスワードハッシュを取得
    Return
        パスワードあり：パスワードハッシュ
        パスワードなし：空文字列
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT user_password_hash FROM amidas WHERE amida_id = %s",
                (amida_id,)
            )
            result = cursor.fetchone()
            if result is None:
                return None

            user_password_hash = result.get("user_password_hash")
            return user_password_hash if user_password_hash else ""

    except pymysql.Error:
        return None

def get_is_opened_from_amida(amida_id) -> bool:
    """あみだくじに開封状態を取得
    Return
        成功：bool
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT is_opened FROM amidas WHERE amida_id = %s",
                (amida_id,),
            )
            result = cursor.fetchone()
            return result["is_opened"] if result else None

    except pymysql.Error:
        return None

## ---- 線操作関数 ----
class LineStatus(Enum):
    """線の状態クラス"""
    READY = "ready"
    DRAWEN = "drawn"
    CANCELED = "canceled"

def get_lines_from_amida(amida_id) -> list:
    """あみだくじに線を一括取得
    Return
        成功：あみだくじに線の情報
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT * FROM amida_lines WHERE amida_id = %s",
                    (amida_id,)
            )
            result = cursor.fetchall()
            return result if result else None

    except pymysql.Error:
        return None


def get_line(line_id) -> dict:
    """線の情報を取得
    Return
        成功：線の情報
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT * FROM amida_lines WHERE line_id = %s",
                    (line_id,)
            )
            result = cursor.fetchone()
            return result if result else None

    except pymysql.Error:
        return None

def get_line_no_from_line(line_id):
    """線にアイテム番号を取得"""

def get_item_id_from_line(line_id):
    """線にアイテム番号を取得"""

def get_line_status_from_line(line_id) -> LineStatus:
    """線に状態を取得"""



## ---- アイテム操作関数 ----

def add_items(amida_id, *items) -> bool:
    """アイテムを登録
    Return
        成功：True
        失敗：False
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            # アイテムを入れる
            for item in items:
                cursor.execute("INSERT ...")
            # ハズレを入れる
            cursor.execute("INSERT ...")

        db.commit()
        return True

    except pymysql.Error:
        db.rollback()
        return False

def get_item(item_id) -> dict:
    """アイテムの情報を取得
    Return
        成功：線の情報
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT * FROM amida_items WHERE item_id = %s",
                    (item_id,)
            )
            result = cursor.fetchone()
            return result if result else None

    except pymysql.Error:
        return None

def get_items_from_amida(amida_id) -> list:
    """あみだくじにアイテムを一括取得
    Return
        成功：あみだくじにアイテムの情報
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT * FROM amida_items WHERE amida_id = %s",
                    (amida_id,)
            )
            result = cursor.fetchall()
            return result if result else None

    except pymysql.Error:
        return None

## ---- 抽籤関数 ----

def do_draw(amida_id, line_no, nickname, password_hash) -> bool:
    """抽籤をする
    Return
        成功：True
        失敗：False
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT ...")
            line_id = cursor.fetchone()

            # line.status のチェック
            return False

            cursor.execute("INSERT ...")
            # UPDATE line.status = LineStatus(DRAWN)
        db.commit()
        return True

    except pymysql.Error:
        db.rollback()
        return False

## ---- 開封関数 ----
def do_open(amida_id) -> bool:
    """あみだくじを開封する
    Return
        成功：True
        失敗：False
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT ...")
            result = cursor.fetchone()

            cursor.execute("INSERT ...")
            # UPDATE amida.is_opened = True
        db.commit()

    except pymysql.Error:
        db.rollback()
        return False
