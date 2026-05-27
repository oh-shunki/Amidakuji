"""モデル"""
import json
import uuid

from enum import Enum

import pymysql

from flask import current_app, g, abort

# ----- 基盤 -----

def get_db():
    """dbを取得"""
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
    """dbを切断"""
    db = g.pop("db", None)

    if db is not None:
        db.close()

class LineStatus(Enum):
    """線の状態クラス"""
    READY = "ready"
    DRAWN = "drawn"
    CANCELED = "canceled"

# ----- あみだくじ amidas テーブル 操作関数 -----

def create_amida(amida: dict, amida_items: list) -> uuid.UUID:
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
    amida_map = amida.get("amida_map")

    db = get_db()
    try:
        with db.cursor() as cursor:
            # あみだくじ情報の登録
            cursor.execute("""
                    INSERT INTO amidas (amida_id, title, line_count,
                        option_auto_open, option_hide_items,
                        admin_password_hash, user_password_hash,
                        is_opened, amida_map)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (amida_id, title, line_count,
                        option_auto_open, option_hide_items,
                        admin_password_hash, user_password_hash,
                        is_opened, amida_map)
            )

            for no in range(line_count):
                # 線作成
                cursor.execute("""
                        INSERT INTO amida_lines (amida_id, line_no)
                        VALUES (%s, %s)
                        """, (amida_id, no)
                )

                # アイテム作成
                item = amida_items[no]
                cursor.execute("""
                        INSERT INTO amida_items (amida_id, item_no, title)
                        VALUES (%s, %s, %s)
                        """, (amida_id, no, item)
                )

        db.commit()
        return amida_id

    except pymysql.Error:
        db.rollback()
        return None

def update_amida(amida: dict, amida_items: list) -> bool:
    """あみだくじの設定変更
    Return
        成功：True
        失敗：False
    """
    amida_id = amida.get("amida_id")
    title = amida.get("title")
    option_auto_open = amida.get("option_auto_open", False)
    admin_password_hash = amida.get("admin_password_hash")
    user_password_hash = amida.get("user_password_hash")

    if not amida_id:
        return False

    db = get_db()
    try:
        with db.cursor() as cursor:
            # 開封状態チェック & ロック
            cursor.execute(
                    "SELECT is_opened FROM amidas WHERE amida_id = %s FOR UPDATE",
                    (amida_id,)
            )
            result = cursor.fetchone()
            if not result or result.get("is_opened"):
                return False

            # あみだくじ情報の更新
            cursor.execute("""
                    UPDATE amidas
                    SET title = %s, option_auto_open = %s
                    WHERE amida_id = %s
                    """, (title, option_auto_open, amida_id)
            )

            # 管理パスワードハッシュある時のみ更新
            if admin_password_hash:
                cursor.execute("""
                        UPDATE amidas SET admin_password_hash = %s
                        WHERE amida_id = %s
                        """, (admin_password_hash, amida_id)
                )

            # 利用パスワードハッシュある時のみ更新
            if user_password_hash:
                cursor.execute("""
                        UPDATE amidas SET user_password_hash = %s
                        WHERE amida_id = %s
                        """, (user_password_hash, amida_id)
                )

            # アイテムが変更された時のみ再作成
            if amida_items:
                # 旧アイテム削除
                cursor.execute(
                        "DELETE FROM amida_items WHERE amida_id = %s", (amida_id,)
                )

                # 新アイテム作成
                line_count = get_line_count_from_amida(amida_id)
                for n in range(line_count):
                    item = amida_items[n]
                    cursor.execute("""
                            INSERT INTO amida_items (amida_id, item_no, title)
                            VALUES (%s, %s, %s)
                            """, (amida_id, n, item)
                    )

        db.commit()
        return True

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
            # あみだくじIDの特定 & ロック
            cursor.execute(
                    "SELECT 1 FROM amidas WHERE amida_id = %s FOR UPDATE",
                    (amida_id,)
            )
            result = cursor.fetchone()
            if not result:
                return False

            # あみだくじの削除
            # amida_lines, amida_items, amida_draws は DB 制約で自動的に消える
            cursor.execute(
                    "DELETE FROM amidas WHERE amida_id = %s", (amida_id,)
            )

        db.commit()
        return True

    except pymysql.Error:
        db.rollback()
        return False

# ----- あみだくじ amidas テーブル 情報取得関数 -----

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

            if result:
                # あみだマップを Python リストへ変換
                result["amida_map"] = json.loads(result["amida_map"])

            return result

    except pymysql.Error:
        return None

def get_line_count_from_amida(amida_id) -> int:
    """あみだくじに線の本数を取得
    Return
        成功：線の本数
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT line_count FROM amidas WHERE amida_id = %s",
                (amida_id,)
            )
            result = cursor.fetchone()
            return result["line_count"] if result  else None

    except pymysql.Error:
        return None

def get_option_auto_open_from_amida(amida_id) -> bool:
    """あみだくじに自動開封設定を取得
    Return
        オン：True
        オフ：False
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
        オン：True
        オフ：False
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
        開封済：True
        未開封：False
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

def get_lines_status_str_from_amida(amida_id) -> list[str]:
    """あみだくじに線の状態を一括取得（line_no 順）
    Return
        成功：線の状態リスト
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                    SELECT status FROM amida_lines WHERE amida_id = %s
                    ORDER BY line_no ASC
                    """, (amida_id,)
            )
            results = cursor.fetchall()
            return [row["status"] for row in results] if results else []

    except pymysql.Error:
        return None

def get_remain_line_count_from_amida(amida_id) -> int:
    """あみだくじに余った線の数を取得
    Return
        成功：余った線の数
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                    SELECT COUNT(*) AS remain_line_count FROM amida_lines
                    WHERE amida_id = %s and status = 'ready'
                    """, (amida_id,)
            )
            result = cursor.fetchone()
            return result["remain_line_count"] if result else None

    except pymysql.Error:
        return None

def get_nicknames_from_amida(amida_id) -> list:
    """あみだくじに参加者のニックネームを一括取得（line_no 順）
    Return
        成功：参加者のニックネーム
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                    SELECT
                        d.nickname
                    FROM
                        amida_lines l
                    LEFT JOIN
                        amida_draws d
                        ON l.line_id = d.line_id AND l.amida_id = d.amida_id
                    WHERE
                        l.amida_id = %s
                    ORDER BY
                        l.line_no ASC
                    """, (amida_id,)
            )
            results = cursor.fetchall()
            return [row["nickname"] for row in results] if results else []

    except pymysql.Error:
        return None

# ----- 線 amida_lines 情報取得関数 ------

def get_lines_from_amida(amida_id) -> list:
    """あみだくじに線を一括取得（line_no 順）
    Return
        成功：あみだくじに線の情報
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT * FROM amida_lines WHERE amida_id = %s ORDER BY line_no ASC",
                    (amida_id,)
            )
            results = cursor.fetchall()
            return results if results else []

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
            return result

    except pymysql.Error:
        return None

def get_line_by_no_from_amida(amida_id, line_no) -> dict:
    """あみだくじに線の番号から情報を取得
    Return
        成功：線の情報
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT * FROM amida_lines WHERE amida_id = %s and line_no = %s",
                    (amida_id, line_no)
            )
            result = cursor.fetchone()
            return result

    except pymysql.Error:
        return None

def get_line_no_from_line(line_id) -> int:
    """線に線の番号を取得
    Return
        成功：線の番号
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT line_no FROM amida_lines WHERE line_id = %s",
                    (line_id,)
            )
            result = cursor.fetchone()
            return result["line_no"] if result else None

    except pymysql.Error:
        return None

def get_item_id_from_line(line_id) -> int:
    """線にアイテムIDを取得
    Return
        成功：アイテムID
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT item_id FROM amida_lines WHERE line_id = %s",
                    (line_id,)
            )
            result = cursor.fetchone()
            return result["item_id"] if result else None

    except pymysql.Error:
        return None

def get_line_status_from_line(line_id) -> LineStatus:
    """線に状態を取得
    Return
        成功：抽籤の情報
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT status FROM amida_lines WHERE line_id = %s",
                    (line_id,)
            )
            result = cursor.fetchone()
            return LineStatus(result["status"]) if result else None

    except pymysql.Error:
        return None

# ----- アイテム amida_items 情報取得関数 -----

def get_items_from_amida(amida_id) -> list:
    """あみだくじにアイテムを一括取得（item_no 順）
    Return
        成功：あみだくじにアイテムの情報
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT * FROM amida_items WHERE amida_id = %s ORDER BY item_no ASC",
                    (amida_id,)
            )
            results = cursor.fetchall()
            return results if results else []

    except pymysql.Error:
        return None

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
            return result

    except pymysql.Error:
        return None

def get_item_no_from_item(item_id) -> int:
    """アイテムの番号を取得
    Return
        成功：アイテムの番号
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT item_no FROM amida_items WHERE item_id = %s",
                    (item_id,)
            )
            result = cursor.fetchone()
            return result["item_no"] if result else None

    except pymysql.Error:
        return None

def get_title_from_item(item_id) -> str:
    """アイテムのタイトルを取得
    Return
        成功：アイテムのタイトル
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT title FROM amida_items WHERE item_id = %s",
                    (item_id,)
            )
            result = cursor.fetchone()
            return result["title"] if result else None

    except pymysql.Error:
        return None

# ----- 抽籤 amida_draws 情報取得関数 -----

def get_draws_from_amida(amida_id) -> list:
    """あみだくじに抽籤を一括取得
    Return
        成功：あみだくじに抽籤の情報
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT * FROM amida_draws WHERE amida_id = %s",
                    (amida_id,)
            )
            results = cursor.fetchall()
            return results if results else []

    except pymysql.Error:
        return None

def get_draw(draw_id) -> dict:
    """抽籤の情報を取得
    Return
        成功：抽籤の情報
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT * FROM amida_draws WHERE draw_id = %s",
                    (draw_id,)
            )
            result = cursor.fetchone()
            return result

    except pymysql.Error:
        return None

def get_draw_from_line(line_id) -> dict:
    """線に抽籤の情報を取得
    Return
        成功：抽籤の情報
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT * FROM amida_draws WHERE line_id = %s",
                    (line_id,)
            )
            result = cursor.fetchone()
            return result

    except pymysql.Error:
        return None

def get_line_id_from_draw(draw_id) -> int:
    """抽籤に線のIDを取得
    Return
        成功：線のID
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT line_id FROM amida_draws WHERE draw_id = %s",
                    (draw_id,)
            )
            result = cursor.fetchone()
            return result["line_id"] if result else None

    except pymysql.Error:
        return None

def get_line_no_from_draw(draw_id) -> int:
    """抽籤に線の番号を取得
    Return
        成功：線の番号
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                    SELECT l.line_no
                    FROM amida_lines l
                    INNER JOIN amida_draws d ON l.line_id = d.line_id
                    WHERE d.draw_id = %s
                    """, (draw_id,)
            )
            result = cursor.fetchone()
            return result["line_no"] if result else None

    except pymysql.Error:
        return None

def get_nickname_from_draw(draw_id) -> str:
    """抽籤に参加者のニックネームを取得
    Return
        成功：参加者のニックネーム
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT nickname FROM amida_draws WHERE draw_id = %s",
                    (draw_id,)
            )
            result = cursor.fetchone()
            return result["nickname"] if result else None

    except pymysql.Error:
        return None

def get_draw_nickname_from_line(line_id) -> str:
    """線に抽籤参加者のニックネームを取得
    Return
        成功：抽籤参加者のニックネーム
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT nickname FROM amida_draws WHERE line_id = %s",
                    (line_id,)
            )
            result = cursor.fetchone()
            return result["nickname"] if result else None

    except pymysql.Error:
        return None

def get_password_hash_from_draw(draw_id) -> str:
    """抽籤にパスワードハッシュを取得
    Return
        パスワードあり：パスワードハッシュ
        パスワードなし：空文字列
        失敗：None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT password_hash FROM amida_draws WHERE draw_id = %s",
                (draw_id,)
            )
            result = cursor.fetchone()
            if result is None:
                return None

            password_hash = result.get("password_hash")
            return password_hash if password_hash else ""

    except pymysql.Error:
        return None

# ----- ビジネスロジック・実行関数 -----

def is_nickname_usable(amida_id, nickname) -> bool:
    """ニックネームが使用可能か（重複していないか）を確認
    Return
        使用可能（存在しない）: True
        使用不可（存在する）: False
        システムエラー: None
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT 1 FROM amida_draws WHERE amida_id = %s and nickname = %s",
                    (amida_id, nickname)
            )
            result = cursor.fetchone()
            return result is None

    except pymysql.Error:
        return None

def do_draw(amida_id, line_no, nickname, password_hash) -> bool:
    """抽籤をする
    Return
        成功：True
        失敗：False
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            # 開封状態チェック & ロック
            cursor.execute(
                    "SELECT is_opened FROM amidas WHERE amida_id = %s FOR UPDATE",
                    (amida_id,)
            )
            result = cursor.fetchone()
            if not result or result.get("is_opened"):
                return False

            # 線の情報を取得
            cursor.execute("""
                    SELECT line_id, status FROM amida_lines
                    WHERE amida_id = %s AND line_no = %s
                    """, (amida_id, line_no)
            )
            result = cursor.fetchone()
            if not result:
                return False

            line_id = result.get("line_id")
            line_status = LineStatus(result.get("status"))

            # 線の状態チェック
            if line_status != LineStatus.READY:
                return False

            # ニックネームチェック
            if not is_nickname_usable(amida_id, nickname):
                return False

            # 参加者情報記入
            cursor.execute("""
                    INSERT INTO amida_draws (amida_id, line_id, nickname, password_hash)
                    VALUES (%s, %s, %s, %s)
                    """, (amida_id, line_id, nickname, password_hash)
            )

            # 線の状態を更新
            cursor.execute(
                    "UPDATE amida_lines SET status = 'drawn' WHERE line_id = %s",
                    (line_id,)
            )

        db.commit()
        return True

    except pymysql.Error:
        db.rollback()
        return False

def do_cancel(amida_id, line_no) -> bool:
    """抽籤取消をする
    Return
        成功：True
        失敗：False
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            # 開封状態チェック & ロック
            cursor.execute(
                    "SELECT is_opened FROM amidas WHERE amida_id = %s FOR UPDATE",
                    (amida_id,)
            )
            result = cursor.fetchone()
            if not result or result.get("is_opened"):
                return False

            # 線の情報を取得
            cursor.execute("""
                    SELECT line_id, status FROM amida_lines
                    WHERE amida_id = %s AND line_no = %s
                    """, (amida_id, line_no)
            )
            result = cursor.fetchone()
            if not result:
                return False

            line_id = result.get("line_id")
            line_status = LineStatus(result.get("status"))

            # 線の状態チェック
            if line_status != LineStatus.DRAWN:
                return False

            # 参加者情報を削除
            cursor.execute(
                    "DELETE FROM amida_draws WHERE amida_id = %s AND line_id = %s",
                    (amida_id, line_id)
            )

            # 線の状態を更新
            cursor.execute(
                    "UPDATE amida_lines SET status = 'canceled' WHERE line_id = %s",
                    (line_id,)
            )

        db.commit()
        return True

    except pymysql.Error:
        db.rollback()
        return False

def do_open(amida_id, goals) -> bool:
    """あみだくじを開封する
    Return
        成功：True
        失敗：False
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                    "SELECT is_opened FROM amidas WHERE amida_id = %s FOR UPDATE",
                     (amida_id,)
            )
            result = cursor.fetchone()
            if not result or result["is_opened"]:
                return False

            # アイテムID一括取得（item_no 順）
            cursor.execute("""
                    SELECT item_id FROM amida_items WHERE amida_id = %s
                    ORDER BY item_no ASC
                    """, (amida_id,)
            )
            results = cursor.fetchall()
            item_ids = [row["item_id"] for row in results]

            # 線ID一括取得（line_no 順）
            cursor.execute("""
                    SELECT line_id FROM amida_lines WHERE amida_id = %s
                    ORDER BY line_no ASC
                    """, (amida_id,)
            )
            results = cursor.fetchall()
            line_ids = [row["line_id"] for row in results]

            # amida_lines にゴールを記入
            for line_no, item_no in enumerate(goals):
                item_id = item_ids[item_no]
                line_id = line_ids[line_no]

                cursor.execute(
                        "UPDATE amida_lines SET item_id = %s WHERE line_id = %s",
                        (item_id, line_id)
                )

            # 開封状態を切り替える
            cursor.execute(
                    "UPDATE amidas SET is_opened = True WHERE amida_id = %s",
                    (amida_id,)
            )

        db.commit()
        return True

    except pymysql.Error:
        db.rollback()
        return False
