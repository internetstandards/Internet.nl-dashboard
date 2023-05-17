# SPDX-License-Identifier: Apache-2.0
import json


def get_text_file(filepath: str):
    with open(filepath, "r", encoding="UTF-8") as file_handle:
        data = file_handle.read()
    return data


def get_json_file(filepath: str):
    with open(filepath, "r", encoding="UTF-8") as file_handle:
        data = json.load(file_handle)
    return data
