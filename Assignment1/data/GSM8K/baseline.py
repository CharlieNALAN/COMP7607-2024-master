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

gsm8k_learning = [
    (
        '9980+29=',
        'Target:\n<scratch>\n9 9 8 0 + 2 9 , C: 0\n9 9 8 + 2 , 9 C: 0\n9 9 , 0 9 C: 1\n9 , 0 0 9 C: 1\n, 0 0 0 9 C: 1\n1 0 0 0 9\n</scratch>1 0 0 0 9.'
    ),
    (
        '9980+29=',
        'Explanation:\n'
        'The first number is 9980, FN=[9,9,8,0]. The second number is 29, SN=[2,9]. Since FN [9,9,8,0] has 4 digits, SN [2,9] has 2 digits, thus the maximum number of digits is 4. In each subsequent step, we remove one number from the end of FN and one from the end of SN. Length of FN is 4. FN=[9,9,8,0]. Length of SN is 2. SN=[2,9]. FN[4]=0. SN[4]=9. C[4]=0. Since 0+9+0=9, 9<10, 9%10=9. Length of A is 1. Thus A=[9]. Since (9-9)/10=0, C[3]=0. Length of FN is 3. FN=[9,9,8]. Length of SN is 1. SN=[2]. FN[3]=8. SN[3]=2. C[3]=0. Since 8+2+0=10, 10=10, 10%10=0. Length of A is 2. Thus A=[0,9]. Since (10-0)/10=1, C[2]=1. Length of FN is 2. FN=[9,9]. Length of SN is 0. SN=[]. FN[2]=9. SN is empty. C[2]=1. Since 9+0+1=10, 10=10, 10%10=0. Length of A is 3. Thus A=[0,0,9]. Since (10-0)/10=1, C[1]=1. Length of FN is 1. FN=[9]. Length of SN is 0. SN=[]. FN[1]=9. SN is empty. C[1]=1. Since 9+0+1=10, 10=10, 10%10=0. Length of A is 4. Thus A=[0,0,0,9]. Since (10-0)/10=1, C[0]=1. There are no more digits, but C[0]=1. Length of A is 5. Thus A=[1,0,0,0,9]. The final Answer is [1,0,0,0,9].'
    ),
    (
        '802+7145=',
        'Explanation:\n'
        'The first number is 802, FN=[8,0,2]. The second number is 7145, SN=[7,1,4,5]. Since FN=[8,0,2] has 3 digits, SN=[7,1,4,5] has 4 digits, thus the maximum number of digits is 4. In each subsequent step, we remove one number from the end of FN and one from the end of SN. Length of FN is 3. FN=[8,0,2]. Length of SN is 4. SN=[7,1,4,5]. FN[4]=2. SN[4]=5. C[4]=0. Since 2+5+0=7, 7<10, 7%10=7. Length of A is 1. Thus A=[7]. Since (7-7)/10=0, C[3]=0. Length of FN is 2. FN=[8,0]. Length of SN is 3. SN=[7,1,4]. FN[3]=0. SN[3]=4. C[3]=0. Since 0+4+0=4, 4<10, 4%10=4. Length of A is 2. Thus A=[4,7]. Since (4-4)/10=0, C[2]=0. Length of FN is 1. FN=[8]. Length of SN is 2. SN=[7,1]. FN[2]=8. SN[2]=1. C[2]=0. Since 8+1+0=9, 9<10, 9%10=9. Length of A is 3. Thus A=[9,4,7]. Since (9-9)/10=0, C[1]=0. Length of FN is 0. FN=[]. Length of SN is 1. SN=[7]. FN is empty. SN[1]=7. C[1]=0. Since 0+7+0=7, 7<10, 7%10=7. Length of A is 4. Thus A=[7,9,4,7]. Since (7-7)/10=0, C[0]=0. There are no more digits and C[0]=0. Thus the process is complete. Since there are no more operators, the problem is complete. The final Answer is [7,9,4,7].'
    ),
    (
        '483-389=',
        'Explanation:\n'
        'The first number is 483, adding commas between each number, FN=[4,8,3]. The second number is -389, adding commas between each number, SN=-[3,8,9]. FN [4,8,3] has 3 digits, SN -[3,8,9] has digits, max is 3.\n'
        'Len(FN)=3. FN=[4,8,3]. FN[3]=3. Len(SN)=3. SN=-[3,8,9]. SN[3]=-9. C[3]=0. Since 3-9+0=-6, -6<-10, -6%-10=-6. Len(A)=1. A=[-6]. Since (-6--6)/10=0, C[2]=0. Len(FN)=2. FN=[4,8]. FN[2]=8. Len(SN)=2. SN=-[3,8]. SN[2]=-8. C[2]=0. Since 8-8+0=0, 0<10, 0%10=0. Len(A)=2. A=[0,-6]. Since (0-0)/10=0, C[1]=0. Len(FN)=1. FN=[4]. FN[1]=4. Len(SN)=1. SN=-[3]. SN[1]=-3. C[1]=0. Since 4-3+0=1, 1<10, 1%10=1. Len(A)=3. A=[1,0,-6]. Since (1-1)/10=0, C[0]=0. Len(FN)=0. FN=[]. FN[0]=empty. Len(SN)=0. SN=-[]. SN[0]=empty. Since both FN and SN are empty, next. Since C[0]=0, the steps are done. Since there are - in A, we check the sign of the last step A[1]=1. Since 1 is non-neg, we process A from right to left. A=[1,0,-6]=[+1,+0,-6]. C[3]=0.'
        'Len(A)=3. A=[+1,+0,-6]. A[3]=-6. Since -6<0, B=10, C[2]=-1. Since C[3]=0, thus -6+10+0=4. Len(ANEW)=1. ANEW=[4]. C[2]=-1. Len(A)=2. A=[+1,+0]. A[2]=+0. Since +0 is 0, B=0, C[1]=0. Since C[2]=-1, thus 0+0-1=-1, which is neg, thus repeat with B=10, C[1]=-1. -1+10+0=9. Len(ANEW)=2. ANEW=[9,4]. C[1]=-1. Len(A)=1. A=[+1]. A[1]=+1. Since +1>0, B=0, C[0]=0. Since C[1]=-1, thus 1+0-1=0. Len(ANEW)=3. ANEW=[0,9,4]. C[0]=0. Len(A)=0. A=[]. Since A is empty, the problem is complete. The final Answer is [0,9,4].'
    ),
    # (
    #     '128*367=',
    #     '128*367=128*(300+60+7)\n128*367=128*300+128*60+128*7\n128*367=38400+7680+896\n128*367=46976\nnSo, 128*367=46976. The answer is 46976.'
    # ),
    (
        'Tommy has 3 toy cars. His neighbor, Jessie, has 3 cars too. Jessie’s older brother has 5 more cars than Tommy and Jessie. How many cars do the three of them have altogether?',
        ' <NONALGO> Tommy and Jessie have 3+3=6 cars. Jessie’s brother has 5+6=11 cars. Altogether,they have 6+11=17 cars. The answer is 17.\n#### 17'
    ),
    (
        ' An electronic shop offers smartphones for $467 each, PCs are $128 more expensive than smartphones, and advanced tablets are the prices of a smartphone and a PC combined. How much do you have to pay to buy one of each of the three mentioned products?',
        '<ALGO> To solve this problem, we need to find the prices of a PC and an advanced tablet. Then, we need to add the price of all three products together.\n '
        'The price of a PC is $128 more than a smartphone, thus the price of PC is 467+128. We use theaddition algorithm:\n'
        'Problem: 467+128=\n'
        'Explanation:\n'
        'The subproblems are 467+128=ANS1. There is 1 connecting operator.\n'
        'Subproblem: 467+128=ANS1\n'
        'The first number is 467, FN=[4,6,7]. The second number is 128, SN=[1,2,8]. Since FN [3,6,7] has 3 digits, SN [1,2,8] has 3 digits, thus the maximum number of digits is 3. In each subsequent step, we remove one number from the end of FN and one from the end of SN. Length of A is 0. Length of FN is 3. FN=[4,6,7]. FN[3]=7. Length of SN is 3. SN=[1,2,8]. SN[3]=8. C[3]=0.'
        'Since 7+8+0=15, 15>10, 15%10=5. Length of A is 1. Thus A=[5]. Since (15-5)/10=1, C[2]=1. Length of FN is 2. FN=[4,6]. FN[2]=6. Length of SN is 2. SN=[1,2]. SN[2]=2. C[2]=1. Since 6+2+1=9, 9<10, 9%10=9. Length of A is 2. Thus A=[9,5]. Since (9-9)/10=0, C[1]=0. Length of FN is 1. FN=[4]. FN[1]=4. Length of SN is 1. SN=[1]. SN[1]=1. C[1]=0. Since 4+1+0=5, 5<10, 5%10=5. '
        'Length of A is 3. Thus A=[5,9,5]. Since (5-5)/10=0, C[0]=0. There are no more digits and C[0]=0. Thus the process is complete. Since there is 1 operator and we processed up to ANS1, the problem is complete. The final Answer is [5,9,5]. Removing all 2 commas, we have 595\n'
        'The addition algorithm tells us that the price of a PC is 595. Since the price of an advanced tablet is the sum of a smartphone and a PC, its price is 467+595. We use the addition algorithm:\n'
        'Problem: 467+595=\n'
        'Explanation:\n'
        'The subproblems are 467+595=ANS1. There is 1 connecting operator.\n'
        'Subproblem: 467+595=ANS1\n'
        'The first number is 467, FN=[4,6,7]. The second number is 595, SN=[5,9,5]. Since FN [4,6,7] has 3 digits, SN [5,9,5] has 3 digits, thus the maximum number of digits is 3. In each subsequent step, we remove one number from the end of FN and one from the end of SN. Length of A is 0. Length of FN is 3. FN=[4,6,7]. FN[3]=7. Length of SN is 3. SN=[5,9,5]. SN[3]=5. C[3]=0.'
        ' Since 7+5+0=12, 12>10, 12%10=2. Length of A is 1. Thus A=[2]. Since (12-2)/10=1, C[2]=1. Length of FN is 2. FN=[4,6]. FN[2]=6. Length of SN is 2. SN=[5,9]. SN[2]=9. C[2]=1. Since 6+9+1=16, 16>10, 16%10=6. Length of A is 2. Thus A=[6,2]. Since (16-6)/10=1, C[1]=1. Length of FN is 1. FN=[4]. FN[1]=4. Length of SN is 1. SN=[5]. SN[1]=5. C[1]=1. Since 4+5+1=10, 10=10, 10%10=0.'
        ' Length of A is 3. Thus A=[0,6,2]. Since (10-0)/10=1, C[0]=1. There are no more digits, but C[0]=1. Length of A is 4. A=[1,0,6,2]. Thus the process is complete. Since there is 1 operator and we processed up to ANS1, the problem is complete. The final Answer is [1,0,6,2]. Removing all 3 commas, we have 1062.\n'
        'The addition algorithm tells us that the price of an advanced tablet is 1062. To buy one of each of these products, you would have to pay 467+595+1062. We use the addition algorithm: Problem: 467+595+1062=\n'
        'Explanation:\n'
        'The subproblems are 467+595=ANS1, ANS1+1062=ANS2. There are 2 connecting operators. Subproblem: 467+595=ANS1\n'
        'The first number is 467, FN=[4,6,7]. The second number is 595, SN=[5,9,5]. Since FN [4,6,7] has 3 digits, SN [5,9,5] has 3 digits, thus the maximum number of digits is 3. In each subsequent step, we remove one number from the end of FN and one from the end of SN.'
        ' Length of A is 0. Length of FN is 3. FN=[4,6,7]. FN[3]=7. Length of SN is 3. SN=[5,9,5]. SN[3]=5. C[3]=0. Since 7+5+0=12, 12>10, 12%10=2. Length of A is 1. Thus A=[2]. Since (12-2)/10=1, C[2]=1. Length of FN is 2. FN=[4,6]. FN[2]=6. Length of SN is 2. SN=[5,9]. '
        'SN[2]=9. C[2]=1. Since 6+9+1=16, 16>10, 16%10=6. Length of A is 2. Thus A=[6,2]. Since (16-6)/10=1, C[1]=1. Length of FN is 1. FN=[4]. FN[1]=4. Length of SN is 1. SN=[5]. SN[1]=5. C[1]=1. Since 4+5+1=10, 10=10, 10%10=0. Length of A is 3. Thus A=[0,6,2]. Since (10-0)/10=1, C[0]=1. '
        'There are no more digits, but C[0]=1. Length of A is 4. A=[1,0,6,2]. Thus the process is complete. Since there are 2 operators and we processed up to ANS1, there are more operators to process. The new FN is [1,0,6,2].\n'
        'Subproblem: ANS1+1062=ANS2\n'
        'The first number is ANS1, FN=[1,0,6,2]. The second number is 1062, SN=[1,0,6,2]. Since FN[1,0,6,2] has 4 digits, SN [1,0,6,2] has 4 digits, thus the maximum number of digits is 4. In each subsequent step, we remove one number from the end of FN and one from the end of SN. Length of A is 0.\n'
        'Length of FN is 4. FN=[1,0,6,2]. FN[4]=2. Length of SN is 4. SN=[1,0,6,2]. SN[4]=2. C[4]=0. Since 2+2+0=4, 4<10, 4%10=4. Length of A is 1. Thus A=[4]. Since (4-4)/10=0, C[3]=0. Length of FN is 3. FN=[1,0,6]. FN[3]=6. Length of SN is 3. SN=[1,0,6]. SN[3]=6. C[3]=0. Since 6+6+0=12, 12>10, 12%10=2. '
        'Length of A is 2. Thus A=[2,4]. Since (12-2)/10=1, C[2]=1. Length of FN is 2. FN=[1,0]. FN[2]=0. Length of SN is 2. SN=[1,0]. SN[2]=0. C[2]=1. Since 0+0+1=1, 1<10, 1%10=1. Length of A is 3. Thus A=[1,2,4]. Since (1-1)/10=0, C[1]=0. Length of FN is 1. FN=[1]. FN[1]=1. Length of SN is 1. SN=[1]. SN[1]=1. C[1]=0. '
        'Since 1+1+0=2, 2<10, 2%10=2. Length of A is 4. Thus A=[2,1,2,4]. Since (2-2)/10=0, C[0]=0. There are no more digits and C[0]=0. Thus the process is complete. Since there are 2 operators and we processed up to ANS2, the problem is complete. The final Answer is [2,1,2,4]. Removing all 3 commas, we have 2124.\n'
        'The addition algorithm tells us that the sum of all the products is 2124. The answer is 2124.\n#### 2124'
    ),
    (
        'Cally and Danny washed their clothes. Cally has 10 white shirts, 5 colored shirts, 7 pairs of shorts, and 6 pairs of pants, while Danny has 6 white shirts, 8 colored shirts, 10 shorts, and 6 pairs of pants. How many clothes did they wash?',
        '<NONALGO> They washed 10+6=16 white shirts. They washed 5+8=13 colored shirts. They washed 7+10=17 shorts. They washed 6+6=12 pants. Therefore, Cally and Danny washed a total of 16+13+17+12=58 clothes. The answer is 58.\n#### 58'
    ),
    (
        ' If there are four times as many red crayons as blue crayons in a box, and there are 3 blue crayons. How many crayons total are in the box?',
        ' <NONALGO> There are 4 times as many red crayons as blue crayons, which means there are 3+3+3+3=12 red crayons. Since there are 3 blue crayons and 12 red crayons, in total there are 12+3=15 crayons. The answer is 15.\n#### 15'
    )
]

def nshot_chats(n: int, question: str) -> dict:
    def question_prompt(s):
        return f'Question: {s}'

    def answer_prompt(s):
        return f"Answer:\nLet's think step by step.\n{s}"

    chats = [
        {"role": "system", "content": "Your task is to solve a series of math word problems by providing the final answer. Use the format #### [value] to highlight your answer. For example, if the answer is 560, you should write #### 560. Make sure there always an #### [value] at the end, and don't add any extra things behind ####, just the answer number"}
    ]

    for q, a in gsm8k_nshots[:n]:
        chats.append(
            {"role": "user", "content": question_prompt(q)})
        chats.append(
            {"role": "assistant", "content": answer_prompt(a)})

    chats.append({"role": "user", "content": question_prompt(question)})
    return chats



if __name__ == '__main__':

    time_random = 0
    acc_num=0
    total_num=0
    total_time = 0
    total_prompt_tokens=0
    total_completion_tokens=0
    total_tokens = 0
    client = OpenAI(base_url="https://api.sambanova.ai/v1", api_key="5bd891fa-0f99-4f8c-8166-659ae73f3f35")
    with open('test.jsonl', 'r', encoding="utf-8") as f, open('fewshot.baseline.jsonl', 'a', encoding="utf-8") as output_file:
        for line in f:
        # for line_number, line in enumerate(f):            # if program break, set the checkpoint and run again
        #     if line_number < 990:
        #         continue
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