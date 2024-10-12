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

def convert(output:str):
    output = re.findall('-?\d+(?:\.\d+)?(?:/\d+)?', output)[0]
    output = delete_extra_zero(output)
    output=int(output)
    return output

def acc_eval(output:str,ans:str, acc_num:int, total_num:int):
    output= extract_ans_from_response(output)
    if type(output) == str:
        output = convert(output)
    ans= extract_ans_from_response(ans)
    if type(ans) == str:
        ans = convert(ans)
    print(ans, "-", output,end="  ")
    if ans == output:
        print((acc_num+1)/total_num)
        return True
    else:
        print(acc_num/total_num)
        return False




# if __name__ == '__main__':
    # test_solution = "Anna has 2 more apples than Elsa. So Anna has 2 + 5 = 7 apples. Elsa and Anna have 5 + 7 = 12 apples together. #### 12 apples"
    # answer = extract_ans_from_response(test_solution)
    # answer = re.findall('-?\d+(?:\.\d+)?(?:/\d+)?', answer)[0]
    # answer = delete_extra_zero(answer)
    # answer = int(answer)
    # print(type(answer))