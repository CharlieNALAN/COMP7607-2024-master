import json
import re




def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def delete_extra_zero(n):
    '''Delete the extra 0 after the decimal point'''
    try:
        n=float(n)
    except:
        # print("None {}".format(n))
        return n
    if isinstance(n, int):
        return str(n)
    if isinstance(n, float):
        n = str(n).rstrip('0')  # 删除小数点后多余的0
        n = int(n.rstrip('.')) if n.endswith('.') else float(n)  # 只剩小数点直接转int，否则转回float
        n=str(n)
        return n


def extract_ans_from_response(answer: str, eos=None):
    '''
    :param answer: model-predicted solution or golden answer string
    :param eos: stop token
    :return:
    '''
    if eos:
        answer = answer.split(eos)[0].strip()

    answer = answer.split('####')[-1].strip()

    for remove_char in [',', '$', '%', 'g']:
        answer = answer.replace(remove_char, '')

    try:
        return int(answer)
    except ValueError:
        return answer

# convert output to str() and modify it
def convert(output:str):
    output = str(output)
    output = re.findall('-?\d+(?:\.\d+)?(?:/\d+)?', output)[0]
    output = delete_extra_zero(output)
    return output

# default: decide whether print the information
def acc_eval(output:str,ans:str, acc_num:int, total_num:int, default = True):
    if default:
        print("No.",total_num,sep="",end=":")
    output= extract_ans_from_response(output)
    output = convert(output)
    ans= extract_ans_from_response(ans)
    ans = convert(ans)
    if default:
        print(ans, "-", output,end="  ")
    if ans == output:
        if default:
            print((acc_num+1)/total_num,end=" ")
        return True
    else:
        if default:
            print(acc_num/total_num,end=" ")
        return False

# compare each answer
def read_and_compare(file1, file2):
    total_num = 0
    acc_num = 0
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        for line1, line2 in zip(f1, f2):
            data1 = json.loads(line1)
            data2 = json.loads(line2)
            total_num += 1
            if acc_eval(data1['answer'],data2['answer'],acc_num,total_num,default = False):
                acc_num += 1
        percentage = (acc_num / total_num) * 100
        formatted_output = f"{percentage:.6f}%"
        print("The overall accuracy of zero shot baseline is:",formatted_output)
    with open("fewshot_inference.txt","a",encoding='utf-8') as f:
        f.write(f"The overall accuracy of baseline is:{formatted_output}\n")

def token_and_time_eval(file):
    total_time = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_tokens = 0
    total_num = 0
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            total_prompt_tokens += data['prompt_tokens']
            total_completion_tokens += data['completion_tokens']
            total_tokens += data['total_tokens']
            total_num += 1
            total_time += data['time']
    print(f"toal_prompt_tokens: {total_prompt_tokens}, total_completion_tokens: {total_completion_tokens}, total_tokens: {total_tokens}, total_time: {total_time}")
    avg_time = total_time/total_num
    avg_prompt_time = total_prompt_tokens/total_num
    avg_completion_time = total_completion_tokens/total_num
    avg_total_token = total_tokens/total_num
    print(f"avg_prompt_tokens:{avg_prompt_time}, avg_completion_tokens:{avg_completion_time}, avg_total_token:{avg_total_token}, avg_total_time:{avg_time}")

    with open('fewshot_inference.txt', 'a', encoding='utf-8') as result_file:
        result_file.write(f"Average Wall-Clock Time per Question: {avg_time:.4f} seconds\n")
        result_file.write(f"Average Number of Total Tokens per Question: {avg_total_token:.4f}\n")
        result_file.write(f"Average Number of Completion Tokens per Question: {avg_completion_time:.4f}\n")
        result_file.write(f"Average Number of Prompt Tokens per Question: {avg_prompt_time:.4f}\n")
    print("save success!")





if __name__ == '__main__':
    read_and_compare('fewshot.baseline.jsonl','test.jsonl')
    token_and_time_eval('fewshot.baseline.jsonl')


# if __name__ == '__main__':
#     test_solution = "Anna has 2 more apples than Elsa. So Anna has 2 + 5 = 7 apples. Elsa and Anna have 5 + 7 = 12 apples together. #### 12.00 apples"
#     answer = extract_ans_from_response(test_solution)
#     answer = re.findall('-?\d+(?:\.\d+)?(?:/\d+)?', answer)[0]
#     answer = delete_extra_zero(answer)
#     # answer = int(answer)
#     print(answer)