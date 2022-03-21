import re
from .constants import *


COLUMNS = {
    "А": 0,
    "Б": 1,
    "В": 2,
    "Г": 3,
    "Д": 4,
    "Е": 5,
    "Ж": 6,
    "З": 7,
    "И": 8,
    "К": 9,
    0: "А",
    1: "Б",
    2: "В",
    3: "Г",
    4: "Д",
    5: "Е",
    6: "Ж",
    7: "З",
    8: "И",
    9: "К",
}
pattern = re.compile(
    r"\b(([абвгдежзик])\s*(\d\d?)|(\d\d?)\s*([абвгдежзик]))\b", re.IGNORECASE
)


def parse_turn(turn):
    res = pattern.findall(turn)
    if len(res) != 1:
        return None, None
    m, col1, row1, row2, col2 = res[0]
    if col1 and row1:
        return int(row1) - 1, COLUMNS[col1.upper()]
    return int(row2) - 1, COLUMNS[col2.upper()]


MISS_WORDS = ["мимо", "промах", "мазал", "мазил"]
HIT_WORDS = ["ранил", "попал", "попадание", "ранен"]
SINK_WORDS = ["убил", "потопил", "потоплен"]


def parse_torpedo_result_response(response):
    response = response.lower()
    if any(word in response for word in MISS_WORDS):
        return MISS
    if any(word in response for word in HIT_WORDS):
        return HIT
    if any(word in response for word in SINK_WORDS):
        return SINK
    return WRONG


def stringify_turn(row, col):
    return f"{COLUMNS[col]}{row + 1}"
