from matplotlib.ticker import MaxNLocator
from typing import List
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import json
import re

def parse(stats_data: List[tuple], subject: str) -> dict:
    data = {}
    repeats = {}

    for child, form in stats_data:
        cls = re.search(r"[0-9]+", form)[0]
        data[cls] = data.get(cls, {})
        data[cls][form] = data[cls].get(form, 0)
        repeats[form] = repeats.get(form, [])

        marks = json.loads(child)
        if (len(marks) > 0):
            for mark in marks:
                if (json.loads(f'"{mark["subject"]}"') == subject and mark["date"] not in repeats[form]):
                    repeats[form].append(mark["date"])
                    data[cls][form] += 1

    return data

def plot(data: dict):
    bar_width = 0.15
    fig, ax = plt.subplots()

    max_y = 0
    xticks_pos = []
    xticks_names = []

    for i, cls in enumerate(data):
        for j, form in enumerate(data[cls]):
            color = "#cd0505" if j % 2 == 0 else "#254785"
            ax.bar(i + j * bar_width, data[cls][form], bar_width, color=color)
            xticks_pos.append(i + j * bar_width)
            xticks_names.append(form)
            max_y = max(max_y, data[cls][form])

    ax.set_xticks(xticks_pos, xticks_names)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_yticks(np.arange(0, max_y + 2))
    ax.set_ylabel("Количество проведённых тестов", fontsize=15)

    buf = BytesIO()
    plt.savefig(buf, format = 'jpg')

    return buf