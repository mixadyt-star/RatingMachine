from typing import NoReturn
import json
import os

def store(file: str, key: str, value: str) -> NoReturn:
    if (not os.path.exists(file)):
        with open(file, 'w') as f:
            f.write('{}')

    with open(file, 'r') as f:
        data = json.loads(f.read())

    data[key] = value

    with open(file, 'w') as f:
        f.write(json.dumps(data))

def get_value(file: str, key: str) -> str | None:
    if (os.path.exists(file)):
        with open(file, 'r') as f:
            data = json.loads(f.read())

        return data.get(key, None)
    else:
        return None