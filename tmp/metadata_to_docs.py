import json

with open("metadata_web.json", "r") as read_file:
    data = json.load(read_file)

tests = data.keys()

# transform to list:
test_list = data.items()

# order the list:
test_list = sorted(test_list, key=lambda k: k[1]['hierarchy']['system'] if "hierarchy" in k[1] else [], reverse=False)


def hierarchy_to_indentation(hierarchy):
    return " " * len(hierarchy) * 4


for key, item in test_list:

    # not yet finished metadata
    if 'hierarchy' not in item:
        continue

    indent = hierarchy_to_indentation(item['hierarchy']['system'])
    print(f'{indent}{item["type"]}: {key}')
    print(f"{indent}- Description: {item['description']}")
    print(f"{indent}- Hierarchy: {item['hierarchy']['system']}")
    print(f"{indent}- Possible verdicts: {item['verdict_test_result_mapping'].keys()}")
    print(f"{indent}- Translation key: {item['translation']['key']}")
    print("")
