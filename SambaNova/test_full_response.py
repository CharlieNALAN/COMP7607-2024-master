from openai import OpenAI
client = OpenAI(base_url="https://api.sambanova.ai/v1", api_key="5bd891fa-0f99-4f8c-8166-659ae73f3f35")

completion = client.chat.completions.create(
    model="Meta-Llama-3.1-8B-Instruct",
    messages=[
        {"role": "system", "content": "Your task is to solve a series of math word problems by providing the final answer. Use the format #### [value] to highlight your answer. For example, if the answer is 560, you should write #### 560."},
        {"role": "user", "content": "There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?"},
    ],
    stream=True
)

full_response = ""

for chunk in completion:
    delta = chunk.choices[0].delta
    if hasattr(delta, 'content'):
        full_response += delta.content


print(full_response)


# If you are using the original script in the .pdf, you can set streaming to false, then print(completion.choices[0].message.content)