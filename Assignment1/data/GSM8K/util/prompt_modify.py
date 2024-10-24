import json


def modify_information(file,attribute,content):
    with open(file,'r',encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            data[attribute] = content

    print("modified success!")


if __name__ == '__main__':
    files = ['../']  #TODO add all files need to be modified and finish other works
