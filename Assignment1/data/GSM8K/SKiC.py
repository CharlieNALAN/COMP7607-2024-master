import json
import time

from openai import OpenAI

from Assignment1.data.GSM8K.evaluation import acc_eval

skills=[
    'Skill <extract_digits>: Extract the digits in a number to a list. For example, extract digits in 123 to D=[1,2,3]. Extract digits in 7654 to D=[7,6,5,4]',
    'Skill <list_length>: Get the number of elements in a list. For example, D=[1,2,3], len(D)=3. A=[1,2,4,5,6], len(A)=5.',
    'Skill <add_two_single_digit_number>: Add two single-digit numbers. For example, 0+0=0 0+1=1 0+2=2 0+3=3 0+4=4 0+5=5 0+6=6 0+7=7 0+8=8 0+9=9',
    'Skill <sub_two_single_digit_number>: Subtract two single-digit numbers. For example, 0-0=0 0-1=-1 0-2=-2 0-3=-3 0-4=-4 0-5=-5 0-6=-6 0-7=-7 0-8=-8 0-9=-9',
    'Skill <sub_10>: Subtract 10 from a given number. 10-10=0 11-10=1 12-10=2 13-10=3 14-10=4 15-10=5 16-10=6 17-10=7 18-10=8 19-10=9',
    'Skill <add_10>: Add 10 to a given number. -10+10=0 -9+10=1 -8+10=2 -7+10=3 -6+10=4 -5+10=5 -4+10=6 -3+10=7 -2+10=8 -1+10=9',
    'Skill <compare_0>: Compare a number with 0. 10>0 9>0 8>0 7>0 6>0 5>0 4>0 3>0 2>0 1>0 0=0 -1>0 -2>0 -3>0 -4>0 -5>0 -6>0 -7>0 -8>0 -9>0',
    'Skill <compare_10>: Compare a number with 10. 0<10 1<10 2<10 3<10 4<10 5<10 6<10 7<10 8<10 9<10 10=10 11>10 12>10 13>10 14>10 15>10 16>10 17>10 18>10 19>10',
    'Skill <mul_two_single_digit_number>: Multiply two single-digit numbers. For example, 4*1=4 4*2=8 4*3=12 4*4=16 4*5=20 4*6=24 4*7=28 4*8=32 4*9=36',
    'Skill <add_multiple_numbers>: Add multiple numbers such as m+n+p:\n'
    '1. Add the first two numbers m+n and get the result r1=m+n.\n'
    '2. Add the third number p to r1 and get the result r2=r1+p.',
    'Skill <add>: Use the skills to add two numbers. For example, calculate 86+964 [The steps to perform the add]',
    'Skill <mul>: Use the skills to multiply two numbers. For example, calculate 86*964 [The steps to perform the multiplication]',
    'Skill <sub>: Use the skills to subtract a number from another number. For example, calculate 964-86 [The steps to perform the subtractraction]',
    'Skill <age>: Describe the age of a person. If a person is P years old, Q years ago, the person was P-Q years old. If a person is P years old, in Q years,'
    ' the person will be P+Q years old. If person A is P years old, person B is Q years old, and person A is R years older than person B, then P=Q+R. If person A is P years old, '
    'person B is Q years old, and person A is R years younger than person B, then P=Q-R.',
    'Skill <solve_equation>: Solve an equation. When subtracting or adding the same number from both sides of the equation, '
    'the equation is still true. When moving a number from one side of the equation to the other side, the sign of the number changes. '
    'When moving a multiplication from one side of the equation to the other side, the sign of the multiplication changes. '
    'When moving a division from one side of the equation to the other side, the sign of the division changes.'
]

example=[
    (
        'Four years ago, Kody was only half as old as Mohamed. If Mohamed is currently twice 30 years old, how old is Kody?',
        '1. Mohamed is currently twice 30 years old. Using the Skill <mul>, Mohamed is currently 30*2 = 60 years old.\n'
        '2. Using Skill <age>, four years ago, Mohamed was 4 years younger than now. Using the Skill <sub>, Mohamed was 60-4 = 56 years old.\n'
        '3. Four years ago, Kody was only half as old as Mohamed. Using the Skill <div>, Kody was 56/2 = 28 years old.\n'
        '4. Using Skill <age>, currently, Kody is 4 years older than four years ago. Using the Skill <add>, Kody is currently 28+4 = 32 years old.\n'
        '5. The answer is 32.\n'
        '#### 32'
    ),
    (
        'The girls are trying to raise money for a carnival. Kim raises $320 more than Alexandra, who raises $430, and Maryam raises $400 more than Sarah, who raises $300. How much money, in dollars, did they all raise in total?',
        '1. Alexandra raises $430.\n'
        '2. Kim raises $320 more than Alexandra. Using the Skill <add>, Kim raises $430+$320=$750.\n'
        '3. Sarah raises $300.\n'
        '4. Maryam raises $400 more than Sarah. Using the Skill <add>, Maryam raises $300+$400=$700.\n'
        '5. Using the Skill <add>, they all raise $430+$750+$300+$700=$2180 in total.\n'
        '6. The answer is 2180.\n'
        '#### 2180'
    ),
    (
        'It’s strawberry-picking time on Grandma Concetta’s farm. Tony can pick 6 quarts of strawberries per hour, while Bobby picks one less quart of strawberries per hour than Tony. Kathy can pick twice as many strawberries per hour as Bobby, and Ricky picks two fewer quarts of strawberries per hour than does Kathy. In total, how many quarts of strawberries can Tony, Bobby, Ricky, and Kathy pick per hour on Grandma Concetta’s farm?',
        '1. Tony can pick 6 quarts of strawberries per hour.\n'
        '2. Bobby picks one less quart of strawberries per hour than Tony. Using the Skill <sub>, Bobby picks 6-1=5 quarts of strawberries per hour.\n'
        '3. Kathy can pick twice as many strawberries per hour as Bobby. Using the Skill <mul>, Kathy picks 5*2=10 quarts of strawberries per hour.\n'
        '4. Ricky picks two fewer quarts of strawberries per hour than does Kathy. Using the Skill <sub>, Ricky picks 10-2=8 quarts of strawberries per hour.\n'
        '5. In total, Tony, Bobby, Ricky, and Kathy can pick 6+5+10+8 quarts of strawberries per hour. Using the Skill <add_multiple_numbers>:\n'
        '   i. Add the first two numbers using Skill <add>: r1=6+5=11.\n'
        '   ii. Add the third number 10 to r1=11 using Skill <add>: r2=11+10=21.\n'
        '   iii. Add the fourth number 8 to r2=21 using Skill <add>: r3=21+8=29.\n'
        '6. So the answer is 29.\n'
        '#### 29'
    ),
    (
        'A merchant wants to make a choice of purchase between 2 purchase plans: jewelry worth $5,000 or electronic gadgets worth $8,000. His financial advisor speculates that the jewelry market will go up 2.5% while the electronic gadgets market will rise 1.2% within the same month. If the merchant is looking to maximize profit at the end of this month by making a choice, how much profit would this be?',
        '1. If the merchant buys jewelry worth $5,000 and the jewelry market goes up 2.5%, using the Skill <mul>, the value of the jewelry will increase by $5,000*2.5%= $125. Using Skill <add>, the value of the jewelry will be $5,000+$125=$5125.\n'
        '2. If the merchant buys electronic gadgets worth $8,000 and the electronic gadgets market goes up 1.2%, using the Skill <mul>, the value of the electronic gadgets will increase by $8,000*1.2%= $96. Using Skill <add>, the value of the electronic gadgets will be $8,000+$96=$8096.\n'
        '3. The merchant wants to maximize profit. Using the Skill <sub>, the profit from buying jewelry will be $5125-$5000=$125. The profit from buying electronic gadgets will be $8096-$8000=$96.\n'
        '4. Using the Skill <compare>, $125>$96, so the merchant should buy jewelry to maximize profit. The profit will be $125.\n'
        '5. The answer is 125.\n'
        '#### 125'
    ),
    (
        'Mr. Jackson’s fourth-grade class has 27 students. He wants to give each student 2 glue sticks. The glue sticks come in packs of 8. How many packs will Mr. Jackson need to buy so every student can have 2 glue sticks, assuming he can only buy whole packs and he expects to have some extra glue sticks left over?',
        '1. Mr. Jackson’s fourth-grade class has 27 students and he wants to give each student 2 glue sticks. Using the Skill <mul>, Mr. Jackson needs 27*2=54 glue sticks.\n'
        '2. The glue sticks come in packs of 8. Using the Skill <div>, Mr. Jackson needs 54/8=6.75 packs of glue sticks.\n'
        '3. Mr. Jackson can only buy whole packs. Using the Skill <round>, Mr. Jackson needs to buy 7 packs of glue sticks.\n'
        '4. The answer is 7.\n'
        '#### 7'
    )
]

def organize_prompt(n: int = 5, question: str = "") -> dict:
    def question_prompt(s):
        return f'Question: {s}'

    def answer_prompt(s):
        return f"Answer:\n{s}"


    chats = [
        {"role": "system", "content": "Your task is to solve math word problems using the provided skills. These skills are just references; feel free to create your own skills as needed. Format your answer as #### [value] at the end, without any extra text."}
    ]
    for skill in skills:
        chats.append(
            {"role":"assistant","content":skill}
        )

    for q, a in example[:n]:
        chats.append(
            {"role": "user", "content": question_prompt(q)})
        chats.append(
            {"role": "assistant", "content": answer_prompt(a)})

    chats.append({"role": "user", "content": question_prompt(question)})
    return chats

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
    with open('test.jsonl', 'r', encoding="utf-8") as f,open('SKiC.jsonl', 'a', encoding="utf-8") as output_file:
        # for line in f:
        for line_number, line in enumerate(f):            # if program break, set the checkpoint and run again
            if line_number < 150:                         # change number
                continue
            total_num+=1
            data=json.loads(line)
            question = organize_prompt(n=5,question=data['question'])
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
                "prompt": "Your task is to use the skills(The skills provided are not exhaustive, "
                          "you can create your own skills which you think is necessary to use) to solve a series of math word problems "
                          " Use the format #### [value] to highlight your answer. "
                          "For example, if the answer is 560, you should write #### 560. Don't add any extra "
                          "things behind ####, just the answer number"
            }
            output_file.write(json.dumps(output_data) + "\n")
