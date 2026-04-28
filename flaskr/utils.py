import uuid
import base62

def amida_id_to_b62(amida_id: uuid.UUID) -> str:
    """amida_id を Base62文字列に変換する"""
    return base62.encode(amida_id.int)

def amida_id_b62_to_uuid(amida_id_b62 :str) -> uuid.UUID:
    """amida_id_b62 を UUID型に変換する"""
    return uuid.UUID(int=base62.decode(amida_id_b62))


if __name__ == "__main__":
    print("(1) UUIDv7 -> Base62")
    print("(2) Base62 -> UUIDv7")

    selected = input("-> ")
    if selected == "2":
        input_b62 = input("Base62: ")
        uuidv7_id = amida_id_b62_to_uuid(input_b62)
        print(f"UUIDv7: {uuidv7_id}")
    else :
        input_uuid = input("UUIDv7: ")
        b62_id = amida_id_to_b62(uuid.UUID(input_uuid))
        print(f"Base62: {b62_id}")

    """
    # 1. UUID v7 の生成
    original_u7 = uuid.uuid7()
    print(f"Original UUID v7: {original_u7}")

    # 2. Base62 に変換
    b62_id = amida_id_to_b62(original_u7)
    print(f"Short ID (Base62): {b62_id}")

    # 3. 復元
    restored_u7 = amida_id_b62_to_uuid(b62_id)
    print(f"Restored UUID v7: {restored_u7}")

    # 一致確認
    assert original_u7 == restored_u7
    """
