from typing import NoReturn
import json
import os

def store(file: str, key: str, value: str) -> NoReturn:
    if (not os.path.exists(file)):
        with open(file, 'w', encoding = "utf-8") as f:
            f.write('{}')

    with open(file, 'r', encoding = "utf-8") as f:
        data = json.loads(f.read())

    data[key] = value

    with open(file, 'w') as f:
        f.write(json.dumps(data))

def get_data(file: str) -> dict | None:
    if (os.path.exists(file)):
        with open(file, 'r', encoding = "utf-8") as f:
            data = json.loads(f.read())

        return data
    else:
        return None