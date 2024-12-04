import json
import random
from idlelib.iomenu import encoding


def sample(n,file):
    i=0
    with open(file,'r',encoding='utf-8') as f,open(f"../samepled_SKiC.jsonl",'w',encoding='utf-8') as g:
        for line in f:
            i += 1
            data=json.loads(line)
            g.write(json.dumps(data)+"\n")
            if i >= n:
                break

    print("sample  success")

def random_sample(n, input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 确保 n 不超过文件中的行数
    n = min(n, len(lines))

    # 从文件中随机选择 n 行
    sampled_lines = random.sample(lines, n)

    # 解析每一行的 JSON 数据
    sampled_data = [json.loads(line) for line in sampled_lines]

    # 将采样的数据写入到输出文件
    with open("../random_sampled_test.jsonl", 'w', encoding='utf-8') as f:
        for item in sampled_data:
            f.write(json.dumps(item) + '\n')


if __name__ == '__main__':
    random_sample(500,"../test.jsonl")