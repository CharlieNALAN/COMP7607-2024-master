import json
import time

import tiktoken
from openai import OpenAI
from tiktoken import encoding_for_model
from evaluation import acc_eval
# from transformers import LlamaTokenizer

gsm8k_nshots = [
    (
        'There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?',
        'There are 15 trees originally. Then there were 21 trees after the Grove workers planted some more. So there must have been 21 - 15 = <<21-15=6>>6 trees that were planted.\n#### 6'
    ),
    (
        'If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?',
        'There are originally 3 cars. Then 2 more cars arrive. Now 3 + 2 = <<3+2=5>>5 cars are in the parking lot.\n#### 5'
    ),
    (
        'Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in total?',
        'Originally, Leah had 32 chocolates and her sister had 42. So in total they had 32 + 42 = <<32+42=74>>74. After eating 35, they had 74 - 35 = <<74-35=39>>39 pieces left in total.\n#### 39'
    ),
    (
        'Jason had 20 lollipops. He gave Denny some lollipops. Now Jason has 12 lollipops. How many lollipops did Jason give to Denny?',
        'Jason had 20 lollipops originally. Then he had 12 after giving some to Denny. So he gave Denny 20 - 12 = <<20-12=8>>8 lollipops.\n#### 8'
    ),
    (
        'Shawn has five toys. For Christmas, he got two toys each from his mom and dad. How many toys does he have now?',
        'Shawn started with 5 toys. He then got 2 toys each from his mom and dad. So he got 2 * 2 = <<2*2=4>>4 more toys. Now he has 5 + 4 = <<5+4=9>>9 toys.\n#### 9'
    ),
    (
        'There were nine computers in the server room. Five more computers were installed each day, from monday to thursday. How many computers are now in the server room?',
        'There were originally 9 computers. For each day from monday to thursday, 5 more computers were installed. So 4 * 5 = <<4*5=20>>20 computers were added. Now 9 + 20 = <<9+20=29>>29 computers are now in the server room.\n#### 29'
    ),
    (
        'Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many golf balls did he have at the end of wednesday?',
        'Michael started with 58 golf balls. He lost 23 on Tuesday, and lost 2 more on wednesday. So he had 58 - 23 = <<58-23=35>>35 at the end of Tuesday, and 35 - 2 = <<35-2=33>>33 at the end of wednesday.\n#### 33'
    ),
    (
        'Olivia has $23. She bought five bagels for $3 each. How much money does she have left?',
        'Olivia had 23 dollars. She bought 5 bagels for 3 dollars each. So she spent 5 * 3 = <<5*3=15>>15 dollars. Now she has 23 - 15 = <<23-15=8>>8 dollars left.\n#### 8'
    )
]


def nshot_chats(n: int, question: str) -> dict:
    def question_prompt(s):
        return f'Question: {s}'

    def answer_prompt(s):
        return f"Answer:\nLet's think step by step.\n{s}"

    chats = [
        {"role": "system", "content": "Your task is to solve a series of math word problems by providing the final answer. Use the format #### [value] to highlight your answer. For example, if the answer is 560, you should write #### 560."}
    ]

    for q, a in gsm8k_nshots[:n]:
        chats.append(
            {"role": "user", "content": question_prompt(q)})
        chats.append(
            {"role": "assistant", "content": answer_prompt(a)})

    chats.append({"role": "user", "content": question_prompt(question)})
    return chats

time_random = 0
acc_num=0
total_num=0
total_time = 0
total_prompt_tokens=0
total_completion_tokens=0
total_tokens = 0
client = OpenAI(base_url="https://api.sambanova.ai/v1", api_key="5bd891fa-0f99-4f8c-8166-659ae73f3f35")
with open('test.jsonl', 'r', encoding="utf-8") as f, open('fewshot.baseline.jsonl', 'a', encoding="utf-8") as output_file:
    # for line in f:
    for line_number, line in enumerate(f):            # if program break, set the checkpoint and run again
        if line_number < 990:
            continue
        try:
            data = json.loads(line)
            # zero_shot_prompt = nshot_chats(n=0, question=data['question'])  # zero-shot
            few_shot_prompt = nshot_chats(n=8, question=data['question'])  # few-shot
            completion = client.chat.completions.create(
                model="Meta-Llama-3.1-8B-Instruct",
                messages=few_shot_prompt,
                stream=True,
                stream_options = {"include_usage": True}
            )
            full_response = ""
            for chunk in completion:
                if chunk.usage is not None:
                    total_prompt_tokens += chunk.usage.prompt_tokens
                    total_completion_tokens += chunk.usage.completion_tokens
                    total_tokens += chunk.usage.total_tokens
                    total_time +=chunk.usage.model_extra['total_latency']
                    prompt_tokens = chunk.usage.prompt_tokens
                    completion_tokens = chunk.usage.completion_tokens
                    current_tokens = chunk.usage.total_tokens
                    time_latency = chunk.usage.model_extra['total_latency']
                    break
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content'):
                    full_response += delta.content
            total_num +=1
            output_data = {
                "question": data['question'],
                "answer": full_response,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": current_tokens,
                "time": time_latency
            }
            output_file.write(json.dumps(output_data) + "\n")

            if acc_eval(full_response, data['answer'], acc_num, total_num):
                acc_num+=1
            print(f"total_time:{total_time:.4f}",end="   ")
            print(f"Total_prompt_tokens:{total_prompt_tokens}, total_completion_tokens:{total_completion_tokens}, total_tokens:{total_tokens}")
            time_random += 1
            time.sleep(0.5)
            if time_random == 10:
                print("Suspend for a little while")
                time_random = 0
                time.sleep(5)

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Sleeping for 10 seconds...")
            time.sleep(10)
            completion = client.chat.completions.create(
                model="Meta-Llama-3.1-8B-Instruct",
                messages=few_shot_prompt,
                stream=True
            )
            full_response = ""
            for chunk in completion:
                if chunk.usage is not None:
                    total_prompt_tokens += chunk.usage.prompt_tokens
                    total_completion_tokens += chunk.usage.completion_tokens
                    total_tokens += chunk.usage.total_tokens
                    total_time +=chunk.usage.model_extra['total_latency']
                    prompt_tokens = chunk.usage.prompt_tokens
                    completion_tokens = chunk.usage.completion_tokens
                    current_tokens = chunk.usage.total_tokens
                    time_latency = chunk.usage.model_extra['total_latency']
                    break
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content'):
                    full_response += delta.content
            total_num += 1
            output_data = {
                "question": data['question'],
                "answer": full_response,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": current_tokens,
                "time": time_latency
            }
            output_file.write(json.dumps(output_data) + "\n")
            if acc_eval(full_response, data['answer'], acc_num, total_num):
                acc_num+=1
            print(f"total_time:{total_time:.4f}",end="   ")
            print(f"Total_prompt_tokens:{total_prompt_tokens}, total_completion_tokens:{total_completion_tokens}, total_tokens:{total_tokens}")
            time_random += 1
            time.sleep(0.5)

# Calculate averages
average_time_per_question = total_time / total_num
average_total_tokens_per_question = total_tokens / total_num
average_completion_tokens_per_question = total_completion_tokens / total_num
average_prompt_tokens_per_question = total_prompt_tokens / total_num

print(f"Average Wall-Clock Time per Question: {average_time_per_question:.4f} seconds")
print(f"Average Number of Total Tokens per Question: {average_total_tokens_per_question:.4f}")
print(f"Average Number of Completion Tokens per Question: {average_completion_tokens_per_question:.4f}")
print(f"Average Number of Prompt Tokens per Question: {average_prompt_tokens_per_question:.4f}")
with open('zeroshot_inference.txt', 'w', encoding='utf-8') as result_file:
    result_file.write(f"Average Wall-Clock Time per Question: {average_time_per_question:.4f} seconds\n")
    result_file.write(f"Average Number of Total Tokens per Question: {average_total_tokens_per_question:.4f}\n")
    result_file.write(f"Average Number of Completion Tokens per Question: {average_completion_tokens_per_question:.4f}\n")
    result_file.write(f"Average Number of Prompt Tokens per Question: {average_prompt_tokens_per_question:.4f}\n")

print("Results have been written to inference_costs.txt")
#zero_shot_prompt = nshot_chats(n=0, question="Elsa has 5 apples. Anna has 2 more apples than Elsa. How many apples do they have together?")

#few_shot_prompt = nshot_chats(n=8, question="Elsa has 5 apples. Anna has 2 more apples than Elsa. How many apples do they have together?")  # todo: n is the number of demonstrations