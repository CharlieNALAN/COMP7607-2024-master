import json
import time

from openai import OpenAI
from tqdm import tqdm

from Assignment1.data.GSM8K.SKiC import organize_prompt

from Assignment1.data.GSM8K.baseline import nshot_chats
from Assignment1.data.GSM8K.evaluation import convert, acc_eval
system_prompt_content = [
    "Please rewrite the following mathematical question to be more understandable and easy to answer. Ensure all numbers and key information are retained, and maintain the original meaning. Just output the new question, do not provide the answer.",
    "Please rewrite the following mathematical question to be more understandable and easy to answer. Ensure key information are retained, maintain the original meaning, and try to reorder conditions for clarity. Just output the new question, do not provide the answer."
]
client = OpenAI(base_url="https://api.sambanova.ai/v1", api_key="5bd891fa-0f99-4f8c-8166-659ae73f3f35")

def statistic():
    global cur_prompt_tokens,cur_completion_tokens,cur_tokens,cur_time_latency,prompt_tokens,completion_tokens,current_tokens,time_latency
    cur_prompt_tokens +=prompt_tokens
    cur_completion_tokens +=completion_tokens
    cur_tokens +=current_tokens
    cur_time_latency +=time_latency

def generate_one_new_question(question, client , times):

    try:

        completion = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=[
                {"role": "system", "content": system_prompt_content[times-1]},
                {"role": "user", "content": question},
            ],
            stream=True,
            stream_options = {"include_usage": True},
            temperature= 0.5,
            top_p= 1

        )
        full_response = ""
        for chunk in completion:
            if chunk.usage is not None:
                prompt_tokens = chunk.usage.prompt_tokens
                completion_tokens = chunk.usage.completion_tokens
                current_tokens = chunk.usage.total_tokens
                time_latency = chunk.usage.model_extra['total_latency']
                break
            delta = chunk.choices[0].delta
            if hasattr(delta, 'content'):
                full_response += delta.content
        # print("new problem:{}".format(full_response))
        time.sleep(0.3)
    except Exception as e:
        print(f"An error occurred: {e}")
        change_api()
        completion = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=[
                {"role": "system", "content": system_prompt_content[times-1]},
                {"role": "user", "content": question},
            ],
            stream=True,
            stream_options = {"include_usage": True},
            temperature= 0.5,
            top_p= 1

        )
        full_response = ""
        for chunk in completion:
            if chunk.usage is not None:
                prompt_tokens = chunk.usage.prompt_tokens
                completion_tokens = chunk.usage.completion_tokens
                current_tokens = chunk.usage.total_tokens
                time_latency = chunk.usage.model_extra['total_latency']
                break
            delta = chunk.choices[0].delta
            if hasattr(delta, 'content'):
                full_response += delta.content
        # print("new problem:{}".format(full_response))
        time.sleep(0.3)

    return full_response,prompt_tokens,completion_tokens,current_tokens,time_latency


def request(client,msg ):

    try:
        completion = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=msg,
            stream=True,
            stream_options = {"include_usage": True},
            stop="#### [value]",
            temperature= 0.5,
            top_p= 1
        )
        full_response = ""
        for chunk in completion:
            if chunk.usage is not None:
                prompt_tokens = chunk.usage.prompt_tokens
                completion_tokens = chunk.usage.completion_tokens
                current_tokens = chunk.usage.total_tokens
                time_latency = chunk.usage.model_extra['total_latency']
                break
            delta = chunk.choices[0].delta
            if hasattr(delta, 'content'):
                full_response += delta.content
        time.sleep(0.3)
    except Exception as e:
        print(f"An error occurred: {e}")
        print("change api")
        change_api()
        completion = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=msg,
            stream=True,
            stream_options = {"include_usage": True},
            stop="#### [value]",
            temperature= 0.5,
            top_p= 1
        )
        full_response = ""
        for chunk in completion:
            if chunk.usage is not None:
                prompt_tokens = chunk.usage.prompt_tokens
                completion_tokens = chunk.usage.completion_tokens
                current_tokens = chunk.usage.total_tokens
                time_latency = chunk.usage.model_extra['total_latency']
                break
            delta = chunk.choices[0].delta
            if hasattr(delta, 'content'):
                full_response += delta.content
        time.sleep(0.3)
    return full_response,prompt_tokens,completion_tokens,current_tokens,time_latency
client = OpenAI(base_url="https://api.sambanova.ai/v1", api_key="5bd891fa-0f99-4f8c-8166-659ae73f3f35")

def change_api():
    global client
    if client.api_key == "5bd891fa-0f99-4f8c-8166-659ae73f3f35":
        client.api_key = "f855bbcc-3914-4107-9386-7647d3c1f31c"
    else:
        client.api_key = "5bd891fa-0f99-4f8c-8166-659ae73f3f35"

if __name__ == '__main__':
    total_num=0
    acc_num=0


    with open('test.jsonl', 'r', encoding="utf-8") as f,open('combine_test_origin_optimization.jsonl', 'a', encoding="utf-8") as output_file1,open('combine_test_SKic_optimization.jsonl', 'a', encoding="utf-8") as output_file2:
        progress_bar = tqdm(total=1319, unit="line", leave=True,dynamic_ncols=True)
        for line_number, line in enumerate(f):
            if line_number < 1298:
                progress_bar.update(1)
                continue

            cur_prompt_tokens = 0
            cur_completion_tokens = 0
            cur_tokens = 0
            cur_time_latency = 0
            total_num+=1

            data=json.loads(line)
            # Round 1 -- origin answer compared with SKiC answer
            few_shot = nshot_chats(8,data['question'])
            SKiC = organize_prompt(4,data['question'])
            response_few_shot,prompt_tokens,completion_tokens,current_tokens,time_latency = request(client, few_shot)
            statistic()
            response_SKiC, prompt_tokens,completion_tokens,current_tokens,time_latency= request(client,SKiC)
            statistic()
            ans1_few_shot,ans1_SKic = convert(response_few_shot),convert(response_SKiC)
            print(ans1_few_shot,"-",ans1_SKic,end="-",sep="")
            if ans1_few_shot==ans1_SKic:      # if the 2 answers are the same
                print(convert(data['answer']),end="   ")
                if acc_eval(ans1_SKic,data['answer'],acc_num, total_num):
                    acc_num+=1
            else: # Round 2 -- Rewrite problem -> compare answer again
                # Rewrite the problem
                new_problem,prompt_tokens,completion_tokens,current_tokens,time_latency = generate_one_new_question(data['question'], client,1)
                statistic()
                few_shot = nshot_chats(8, new_problem)
                SKiC = organize_prompt(4,new_problem)
                response_few_shot,prompt_tokens,completion_tokens,current_tokens,time_latency = request(client, few_shot)
                statistic()
                response_SKiC, prompt_tokens,completion_tokens,current_tokens,time_latency= request(client,SKiC)
                statistic()
                ans2_few_shot,ans2_SKic = convert(response_few_shot),convert(response_SKiC)
                print(ans2_few_shot,"-",ans2_SKic,end="-",sep="")
                if ans2_few_shot==ans2_SKic or ans1_SKic == ans2_SKic:      # if the 2 answers are the same
                    print(convert(data['answer']),end="   ")
                    if acc_eval(ans2_SKic,data['answer'],acc_num, total_num):
                        acc_num+=1
                else:# Round 3 (last) -- Rewrite again -> compare again (But if not same, no iter anymore)
                    new_problem,prompt_tokens,completion_tokens,current_tokens,time_latency = generate_one_new_question(data['question'], client,2)
                    statistic()
                    few_shot = nshot_chats(8, new_problem)
                    SKiC = organize_prompt(4,new_problem)
                    response_few_shot,prompt_tokens,completion_tokens,current_tokens,time_latency = request(client, few_shot)
                    statistic()
                    response_SKiC, prompt_tokens,completion_tokens,current_tokens,time_latency= request(client,SKiC)
                    statistic()
                    ans_few_shot,ans_SKic = convert(response_few_shot),convert(response_SKiC)
                    print(ans_few_shot,"-",ans_SKic,end="-",sep="")
                    print(convert(data['answer']),end="   ")
                    if acc_eval(ans_SKic,data['answer'],acc_num, total_num):
                        acc_num+=1
            output_data1 = {
                "question": data['question'],
                "answer": response_few_shot,
                "prompt_tokens": cur_prompt_tokens,
                "completion_tokens": cur_completion_tokens,
                "total_tokens": cur_tokens,
                "time": cur_time_latency,
                "prompt":"Your task is to solve a series of math word problems by providing the final answer. "
                         "Use the format #### [value] to highlight your answer. For example, if the answer is 560, "
                         "you should write #### 560. Make sure there always an #### [value] at the end, and don't add "
                         "any extra things behind ####, just the answer number"
            }
            output_data2 = {
                "question": data['question'],
                "answer": response_SKiC,
                "prompt_tokens": cur_prompt_tokens,
                "completion_tokens": cur_completion_tokens,
                "total_tokens": cur_tokens,
                "time": cur_time_latency,
                "prompt":"Your task is to solve math word problems using the provided skills. "
                         "These skills are just references; feel free to create your own skills as needed. "
                         "Format your answer as #### [value] at the end, without any extra text."
            }
            output_file1.write(json.dumps(output_data1)+"\n")
            output_file2.write(json.dumps(output_data2)+"\n")
            time.sleep(0.5)
            print()
            progress_bar.update(1)








