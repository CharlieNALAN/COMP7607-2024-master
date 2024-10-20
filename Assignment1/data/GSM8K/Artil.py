import json
import time

from openai import OpenAI

from Assignment1.data.GSM8K.baseline import nshot_chats_taril
from Assignment1.data.GSM8K.evaluation import acc_eval


def request(client,msg ):
    try:
        completion = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=msg,
            stream=True,
            stream_options = {"include_usage": True},
            stop="#### [value]"
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
        print("Sleeping for 10 seconds...")
        time.sleep(20)
        completion = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=msg,
            stream=True,
            stream_options = {"include_usage": True},
            stop="#### [value]"
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

if __name__ == '__main__':
    total_num=0
    acc_num=0

    client = OpenAI(base_url="https://api.sambanova.ai/v1", api_key="5bd891fa-0f99-4f8c-8166-659ae73f3f35")
    with open('test.jsonl', 'r', encoding="utf-8") as f,open('atril.jsonl', 'a', encoding="utf-8") as output_file:
        for line in f:
            total_num+=1
            data=json.loads(line)
            question = nshot_chats_taril(8,data['question'])
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
                "prompt": "Your task is to solve a series of math word problems by providing the final answer. "
                          "Use the format #### [value] to highlight your answer. For example, if the answer is 560,"
                          " you should write #### 560. Make sure there always an #### [value] at the end, and don't "
                          "add any extra things behind ####, just the answer number. If the calculation is easy, do "
                          "it directly and use <NONALGO> at the top of the answer. If the calculation calculates more "
                          "bits or is more difficult, calculate it using the algorithm I gave you and put <ALGO> at the"
                          " front of the question. It is recommended to use this algorithm only for addition!"
            }
            output_file.write(json.dumps(output_data) + "\n")
