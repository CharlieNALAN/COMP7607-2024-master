import json


def modify_information(file, attribute, content):
    # Read the existing data
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Modify the data
    modified_lines = []
    for line in lines:
        data = json.loads(line)
        data[attribute] = content
        modified_lines.append(json.dumps(data))

    # Write the modified data back to the file
    with open(file, 'w', encoding='utf-8') as f:
        for line in modified_lines:
            f.write(line + '\n')

def add_attribute(file, attribute, content):
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()


    modified_lines = []
    for line in lines:
        data = json.loads(line)
        data[attribute] = content
        modified_lines.append(json.dumps(data))

    with open(file, 'w', encoding='utf-8') as f:
        for line in modified_lines:
            f.write(line + '\n')

if __name__ == '__main__':
    file="../fewshot.baseline.jsonl"
    add_attribute(file, "prompt", "Your task is to solve a series of math word problems by providing the final answer. Use the format #### [value] to highlight your answer. For example, if the answer is 560, you should write #### 560. Make sure there always an #### [value] at the end, and don't add any extra things behind ####, just the answer number")