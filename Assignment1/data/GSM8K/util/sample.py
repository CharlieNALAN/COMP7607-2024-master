import json
from idlelib.iomenu import encoding


def sample(n,file):
    i=0
    with open(file,'r',encoding='utf-8') as f,open(f"../samepled_SP_fewshot_prompt_improved_v1.jsonl",'w',encoding='utf-8') as g:
        for line in f:
            i += 1
            data=json.loads(line)
            g.write(json.dumps(data)+"\n")
            if i >= n:
                break

    print("sample  success")

if __name__ == '__main__':
    sample(150,"../SP_fewshot_prompt_improved_v1.jsonl")