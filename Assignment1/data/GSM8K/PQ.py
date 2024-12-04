import json
import time
from typing import Optional

from openai import OpenAI

from Assignment1.data.GSM8K.Prompts.prompt_type import std, CoT, CoT_with_invalid_reasoning, \
    no_coherence_for_bridging_object, no_relevance_for_bridging_object, no_coherence_for_language_template, \
    no_relevance_for_language_template, no_coherence, no_relevance, CoT_simple, CoT_complex, CoT_more_complex, \
    DiVE_prompts, AQUA_RAT_prompts
from Assignment1.data.GSM8K.evaluation import acc_eval, read_and_compare, token_and_time_eval


def request(client,msg ):

    try:
        completion = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=msg,
            stream=True,
            stream_options = {"include_usage": True},
            stop="#### [value]",
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


def organize_prompt_by_type(model_type, n: int = 5, question: str = "") -> dict:
    def question_prompt(s):
        return f'Question: {s}'

    def answer_prompt(s):
        return f"Answer:\n{s}"


    chats = [
        {"role": "system", "content": "Your task is to solve a series of math word problems by providing the final answer. Use the format #### [value] to highlight your answer. For example, if the answer is 560, you should write #### 560. Make sure there always an #### [value] at the end, and don't add any extra things behind ####, just the answer number"}
    ]

    for q, a in model_type[:n]:
        chats.append(
            {"role": "user", "content": question_prompt(q)})
        chats.append(
            {"role": "assistant", "content": answer_prompt(a)})

    chats.append({"role": "user", "content": question_prompt(question)})
    return chats

if __name__ == '__main__':
    total_num=0
    acc_num=0
    file_save_name='PD_AQUA_RAT_prompts.jsonl'  # don't forget to change the question!!!
    with open('random_sampled_test.jsonl', 'r', encoding="utf-8") as f,open(file_save_name, 'a', encoding="utf-8") as output_file:
        # for line in f:
        # for line_number, line in enumerate(tqdm(f, desc="Processing lines", unit="line",total=1319,leave=True)):            # if program break, set the checkpoint and run again
        #     if line_number < 296:                         # change number
        #         continue
        for line_number, line in enumerate(f):
            if line_number < -1:
                continue
            total_num+=1
            data=json.loads(line)
            question = organize_prompt_by_type(AQUA_RAT_prompts,n=8,question=data['question'])
            full_response,prompt_tokens,completion_tokens,current_tokens,time_latency = request(client,question)
            if acc_eval(full_response,data['answer'],acc_num,total_num):
                acc_num+=1
            print(f'prompt_tokens: {prompt_tokens},completion_tokens: {completion_tokens},total_tokens:{current_tokens},time_latency: {time_latency}')

            output_data = {
                "question": data['question'],
                "answer": full_response,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": current_tokens,
                "time": time_latency,
            }
            output_file.write(json.dumps(output_data) + "\n")
    read_and_compare(file_save_name,'random_sampled_test.jsonl')
    token_and_time_eval(file_save_name)