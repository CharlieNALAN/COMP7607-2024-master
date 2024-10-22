import json
import time

from openai import OpenAI

from Assignment1.data.GSM8K.SKiC import change_api
from Assignment1.data.GSM8K.baseline import nshot_chats
from Assignment1.data.GSM8K.evaluation import convert, acc_eval


def request(client,msg ):
    completion = client.chat.completions.create(
        model="Meta-Llama-3.1-8B-Instruct",
        messages=msg,
        stream=True,
        stream_options = {"include_usage": True}
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

# system_prompt_content=[
#     "Please rewrite new versions of the original mathematical question to be more understandable and easy to answer. Don't omit any useful information, especially the numbers, and please maintain their original meaning when polysemous words appear. Just output the new question end with ? don't give me answer",
#     "Please rewrite new versions of the original mathematical question to be more understandable and easy to answer. Don't omit any useful information, especially the numbers, and please maintain their original meaning when polysemous words appear, and try to reorder conditions. Just output the new question end with ? don't give me answer"
# ]
system_prompt_content = [
    "Please rewrite the following mathematical question to be more understandable and easy to answer. Ensure all numbers and key information are retained, and maintain the original meaning. Just output the new question, do not provide the answer.",
    "Please rewrite the following mathematical question to be more understandable and easy to answer. Ensure key information are retained, maintain the original meaning, and try to reorder conditions for clarity. Just output the new question, do not provide the answer."
]


def generate_one_new_question(question, client , times):

    try:

        completion = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=[
                {"role": "system", "content": system_prompt_content[times-1]},
                {"role": "user", "content": question},
            ],
            stream=True,
            stream_options = {"include_usage": True}

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
            stream_options = {"include_usage": True}

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


if __name__ == '__main__':
    total_num=0
    acc_num=0

    total_prompt_tokens = 0
    total_completion_tokens=0
    total_tokens=0
    total_time=0

    client = OpenAI(base_url="https://api.sambanova.ai/v1", api_key="5bd891fa-0f99-4f8c-8166-659ae73f3f35")
    with open('test.jsonl', 'r', encoding="utf-8") as f,open('SP_fewshot_prompt_improved_v1.jsonl', 'a', encoding="utf-8") as output_file:
        # for line in f:
        for line_number, line in enumerate(f):            # if program break, set the checkpoint and run again
            if line_number < 1098:
                continue
            total_num+=1

            cur_prompt_tokens = 0
            cur_completion_tokens = 0
            cur_tokens = 0
            cur_time_latency = 0

            data=json.loads(line)
            zero_shot_prompt = nshot_chats(n=8,question=data['question'])

            try:
                full_response,prompt_tokens,completion_tokens,current_tokens,time_latency = request(client,zero_shot_prompt)
            except Exception as e:
                print(f"An error occurred: {e}")
                print("Sleeping for 10 seconds...")
                time.sleep(20)
                full_response,prompt_tokens,completion_tokens,current_tokens,time_latency = request(client,zero_shot_prompt)

            cur_prompt_tokens +=prompt_tokens
            cur_completion_tokens +=completion_tokens
            cur_tokens +=current_tokens
            cur_time_latency +=time_latency
            ans1 = convert(full_response)
            print(ans1,end="-")
            # DEBUG
            # output_data = {
            #     "question": data['question'],
            #     "answer": full_response,
            #     "prompt_tokens": cur_prompt_tokens,
            #     "completion_tokens": cur_completion_tokens,
            #     "total_tokens": cur_tokens,
            #     "time": cur_time_latency
            # }
            # output_file.write(json.dumps(output_data) + "\n")


            new_problem,prompt_tokens,completion_tokens,current_tokens,time_latency = generate_one_new_question(data['question'], client,1)


            cur_prompt_tokens +=prompt_tokens
            cur_completion_tokens +=completion_tokens
            cur_tokens +=current_tokens
            cur_time_latency +=time_latency
            zero_shot_prompt = nshot_chats(n=8,question=new_problem)

            try:
                full_response,prompt_tokens,completion_tokens,current_tokens,time_latency = request(client,zero_shot_prompt)
            except Exception as e:
                print(f"An error occurred: {e}")
                print("Sleeping for 20 seconds...")
                time.sleep(20)
                full_response,prompt_tokens,completion_tokens,current_tokens,time_latency = request(client,zero_shot_prompt)

            ans2 = convert(full_response)
            cur_prompt_tokens +=prompt_tokens
            cur_completion_tokens +=completion_tokens
            cur_tokens +=current_tokens
            cur_time_latency +=time_latency
            print(ans2,end="-")


            if ans1==ans2:
                print(convert(data['answer']),end='-')
                if acc_eval(ans2,data['answer'],acc_num,total_num):
                    acc_num+=1
                output_data = {
                    "question": data['question'],
                    "answer": full_response,
                    "prompt_tokens": cur_prompt_tokens,
                    "completion_tokens": cur_completion_tokens,
                    "total_tokens": cur_tokens,
                    "time": cur_time_latency,
                    "prompt": system_prompt_content[0]
                }
                output_file.write(json.dumps(output_data) + "\n")


            else:

                new_problem,prompt_tokens,completion_tokens,current_tokens,time_latency = generate_one_new_question(data['question'], client,2)

                zero_shot_prompt = nshot_chats(n=8,question=new_problem)
                cur_prompt_tokens +=prompt_tokens
                cur_completion_tokens +=completion_tokens
                cur_tokens +=current_tokens
                cur_time_latency +=time_latency
                try:
                    full_response,prompt_tokens,completion_tokens,current_tokens,time_latency = request(client,zero_shot_prompt)
                except Exception as e:
                    print(f"An error occurred: {e}")
                    print("Sleeping for 20 seconds...")
                    time.sleep(20)
                    full_response,prompt_tokens,completion_tokens,current_tokens,time_latency = request(client,zero_shot_prompt)
                ans3 = convert(full_response)
                cur_prompt_tokens +=prompt_tokens
                cur_completion_tokens +=completion_tokens
                cur_tokens +=current_tokens
                cur_time_latency +=time_latency
                print(ans3,end='-')
                print(convert(data['answer']),end='-')
                if acc_eval(ans3,data['answer'],acc_num,total_num):
                    acc_num+=1
                output_data = {
                    "question": data['question'],
                    "answer": full_response,
                    "prompt_tokens": cur_prompt_tokens,
                    "completion_tokens": cur_completion_tokens,
                    "total_tokens": cur_tokens,
                    "time": cur_time_latency,
                    "prompt":system_prompt_content[1]
                }
                output_file.write(json.dumps(output_data) + "\n")
            print(f'cur_prompt_tokens: {cur_prompt_tokens},cur_completion_tokens: {cur_completion_tokens},cur_tokens: {cur_tokens},time_latency: {cur_time_latency}')

            time.sleep(1)