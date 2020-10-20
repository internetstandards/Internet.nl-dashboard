import json


def get_text_file(filepath: str):
    with open(filepath, "r") as f:
        data = f.read()
    return data


def get_json_file(filepath: str):
    with open(filepath, "r") as f:
        data = json.load(f)
    return data
