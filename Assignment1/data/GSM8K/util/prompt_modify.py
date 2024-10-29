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

if __name__ == '__main__':
    files = "../SKiC_n=4.jsonl"
    modify_information(files,"prompt","Your task is to solve math word problems using the provided skills. These skills are just references; feel free to create your own skills as needed. Format your answer as #### [value] at the end, without any extra text.")
