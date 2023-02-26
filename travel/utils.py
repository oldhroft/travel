import os
import json


def safe_mkdir(path: str):
    if not os.path.exists(path):
        os.mkdir(path)

def dump_json(data: list, path: str):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file)

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file) 
    return data