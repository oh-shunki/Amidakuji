"""あみだくじマップ処理"""
import random

HEIGHT = 20

HORIZONTAL_LINES_MIN = 5
HORIZONTAL_LINES_MAX = 7

EMPTY = 0
RIGHT = 1
LEFT = -1

random.seed()

def generate_map(line_count) -> list:
    """ランダムにあみだくじのマップを生成"""
    if line_count < 2:
        return None

    amida_map = [[EMPTY] * HEIGHT for _ in range(line_count)]

    for line_no in range(line_count - 1):
        y_counts = random.randint(HORIZONTAL_LINES_MIN, HORIZONTAL_LINES_MAX)
        empty_ys = [y for y in range(1, HEIGHT - 1) if amida_map[line_no][y] == EMPTY]
        ys = random.sample(empty_ys, k=y_counts)

        for y in ys:
            amida_map[line_no][y] = RIGHT
            amida_map[line_no + 1][y] = LEFT

    return amida_map

def get_goal(amida_map, line_no) -> int:
    """ゴールを取得"""
    height = len(amida_map[0])
    for y in range(height):
        if amida_map[line_no][y] == RIGHT:
            line_no += 1
        elif amida_map[line_no][y] == LEFT:
            line_no -= 1

    return line_no

def get_goals(amida_map) -> list:
    """ゴールを一括取得"""
    line_count = len(amida_map)
    goals = []
    for line_no in range(line_count):
        goal = get_goal(amida_map, line_no)
        goals.append(goal)

    return goals


if __name__ == "__main__":
    new_map = generate_map(6)
    print(new_map)
    print(get_goals(new_map))
