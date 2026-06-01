"""あみだくじのフォーム制御"""

def validate_line_count(line_count):
    """線の本数の検証"""
    try:
        validated_count = int(line_count)
        if not 3 <= validated_count <= 20:
            raise ValueError("Invalid line_count")

    except (ValueError, TypeError):
        return False

    return True

def validate_password(password):
    """パスワードの検証"""
    return password.isascii() and 3 <= len(password) <= 20

def get_and_validate_form(form, mode, current_line_count=None):
    """ フォームの検証
    Return
        tuple: (errors, amida, amida_items)
    """

    # データの取得
    title = form.get("title", "").strip()
    title = title[:100]

    line_count = form.get("line_count")

    amida_items = form.get("items", "").splitlines()
    amida_items = [item.strip()[:20] for item in amida_items if item.strip()]

    option_auto_open = form.get("option_auto_open") == "on"
    option_hide_items = form.get("option_hide_items") == "on"

    admin_password = form.get("admin_password", "")
    admin_password_confirm = form.get("admin_password_confirm", "")

    user_password = form.get("user_password", "")
    user_password_confirm = form.get("user_password_confirm", "")

    # データの検証
    errors = {}
    if not title:
        errors["title"] = "タイトルは必ず入力して下さい"

    if mode == "create":
        if not line_count:
            errors["line_count"] = "本数を選択してください"
        elif not validate_line_count(line_count):
            line_count = None
            errors["line_count"] = "本数は3～20 の間で選択してください"
        else:
            line_count = int(line_count)
    else:
        line_count = current_line_count if current_line_count else None


    if not amida_items:
        errors["amida_items"] = "アイテムを入力してください"

    if not admin_password:
        if mode == "create":
            errors["admin_password"] = "管理パスワードを入力してください"
    else:
        if not validate_password(admin_password):
            errors["admin_password"] = "管理パスワードは 3 文字以上 20 文字以内で入力してください"
        elif admin_password != admin_password_confirm:
            errors["admin_password"] = "管理パスワードは、上段と下段で同じものを入力して下さい"

    if user_password:
        if not validate_password(user_password):
            errors["user_password"] = "利用パスワードは 3 文字以上 20 文字以内で入力してください"
        elif user_password != user_password_confirm:
            errors["user_password"] = "利用パスワードは、上段と下段で同じものを入力して下さい"

    raw_amida = {
            "title": title,
            "line_count": line_count,
            "option_auto_open": option_auto_open,
            "option_hide_items": option_hide_items,
            "admin_password": admin_password,
            "user_password": user_password
            }

    amida_items = amida_items[:line_count] if line_count else amida_items

    return errors, raw_amida, amida_items
