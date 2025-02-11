from matplotlib.ticker import MaxNLocator
from typing import List
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import datetime
import json
import re

def parse(stats_data: List[tuple], subject: str, class_: int) -> dict:
    data = {}
    repeats = {}

    for child, form in stats_data:
        cls = re.search(r"[0-9]+", form)[0]
        if (cls == class_):
            data[form] = data.get(form, {})

            marks = json.loads(child)
            if (len(marks) > 0):
                for mark in marks:
                    if (json.loads(f'"{mark["subject"]}"') == subject and mark["date"]):
                        n, mean = data[form].get(mark["date"], [0, 0])
                        data[form][mark["date"]] = [n + 1, (mean * n + int(mark["mark"])) / (n + 1)]

    return data

def plot(data: dict):
    fig, ax = plt.subplots()

    xticks_pos = []
    xticks_names = []

    for i, form in enumerate(data):
        color = "#cd0505" if i % 2 == 0 else "#254785"

        x = []
        y = []

        

        for j, date in enumerate(data[form]):
            x.append(j)
            y.append(data[form][date][1])
            xticks_pos.append(j)
            xticks_names.append(date)
        
        plt.plot(x, y, 'o-', color=color, label=form)

    dates = [datetime.datetime.strptime(ts, "%d.%m.%Y") for ts in list(set(xticks_names))]
    dates.sort()
    ax.set_xticks(list(set(xticks_pos)), [datetime.datetime.strftime(ts, "%d.%m.%Y") for ts in dates])
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_yticks(np.arange(0, 6))
    ax.set_ylabel("Средний балл по параллели\n в разрезе тестов", fontsize=15)
    plt.legend(loc="lower right")
    
    buf = BytesIO()
    plt.savefig(buf, format = 'jpg')

    return buf