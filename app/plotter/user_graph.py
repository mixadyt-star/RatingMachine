from matplotlib.ticker import MaxNLocator
from typing import List
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import datetime
import json
import re

def parse(user_data: List[tuple], subject: str) -> dict:
    data = {}

    marks = json.loads(user_data[3])
    if (len(marks) > 0):
        for mark in marks:
            if (json.loads(f'"{mark["subject"]}"') == subject and mark["date"]):
                data[mark["date"]] = [mark["mark"]]

    return data

def plot(data: dict):
    fig, ax = plt.subplots()

    xticks_pos = []
    xticks_names = []

    x = []
    y = []

    for j, date in enumerate(data):
        x.append(j)
        y.append(data[date])
        xticks_pos.append(j)
        xticks_names.append(date)
        
    plt.plot(x, y, 'o-', color="#cd0505")

    dates = [datetime.datetime.strptime(ts, "%d.%m.%Y") for ts in list(set(xticks_names))]
    dates.sort()
    ax.set_xticks(list(set(xticks_pos)), [datetime.datetime.strftime(ts, "%d.%m.%Y") for ts in dates])
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_yticks(np.arange(0, 6))
    ax.set_ylabel("Оценка", fontsize=15)
    
    buf = BytesIO()
    plt.savefig(buf, format = 'jpg')
    plt.close()

    return buf