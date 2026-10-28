#! Python 3
# useful tools for plotting map
import math
import os
from decimal import ROUND_HALF_UP, Decimal
from matplotlib import collections

from ttt_research.plotting.colors import if_orange


def dms2deg(dms):
    # 度分秒から度への変換
    h = dms[0]
    m = dms[1]
    s = dms[2]
    deg = Decimal(str(h + (m / 60) + (s / 3600))).quantize(
        Decimal("0.0001"),
        rounding=ROUND_HALF_UP,
    )
    return deg


def deg2dms(deg):
    # 度から度分秒への変換
    h = math.modf(deg)[1]
    m = math.modf(math.modf(deg)[0] * 60)[1]
    s = math.modf(math.modf(deg)[0] * 60)[0] * 60
    sixty = 60
    if Decimal(str(s)).quantize(Decimal("0"), rounding=ROUND_HALF_UP) == sixty:
        s = 0
        m = m + 1
    if Decimal(str(m)).quantize(Decimal("0"), rounding=ROUND_HALF_UP) == sixty:
        m = 0
        h = h + 1
    dms_tap = (
        int(Decimal(h).quantize(Decimal("0"), rounding=ROUND_HALF_UP)),
        int(Decimal(m).quantize(Decimal("0"), rounding=ROUND_HALF_UP)),
        int(Decimal(s).quantize(Decimal("0"), rounding=ROUND_HALF_UP)),
    )
    return dms_tap


def read_grid_text(dir_path, file_name):
    file_path = os.path.join(dir_path, file_name)

    with open(file_path) as file:
        lines = file.readlines()

    lines_strip = [line.strip() for line in lines]
    list_split = [item.split() for item in lines_strip]
    himawari_grid = {}
    i = 0
    for item in list_split:
        if "grid" in item:
            grid = {}
            grid[item[1][:-1]] = item[2:]
        else:
            grid[item[0][:-1]] = item[1:]
            himawari_grid[f"Grid-{i}"] = grid
            i += 1

    return himawari_grid


def grid_collection(form, himawari_grid, color=if_orange):
    grid_collection = []
    for val in himawari_grid.values():
        line_1 = [
            (float(val["lon"][0]), float(val["lat"][0])),
            (float(val["lon"][1]), float(val["lat"][1])),
        ]
        line_2 = [
            (float(val["lon"][1]), float(val["lat"][1])),
            (float(val["lon"][2]), float(val["lat"][2])),
        ]
        line_3 = [
            (float(val["lon"][2]), float(val["lat"][2])),
            (float(val["lon"][3]), float(val["lat"][3])),
        ]
        line_4 = [
            (float(val["lon"][3]), float(val["lat"][3])),
            (float(val["lon"][0]), float(val["lat"][0])),
        ]

        grid_collection.append(
            collections.LineCollection(
                [line_1, line_2, line_3, line_4],
                transform=form,
                color=color,
            )
        )

    return grid_collection
