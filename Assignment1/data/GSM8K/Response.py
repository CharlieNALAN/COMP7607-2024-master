from openai import OpenAI
from baseline import few_shot_prompt, zero_shot_prompt
client = OpenAI(base_url="https://api.sambanova.ai/v1", api_key="5bd891fa-0f99-4f8c-8166-659ae73f3f35")

completion = client.chat.completions.create(
    model="Meta-Llama-3.1-8B-Instruct",
    messages=zero_shot_prompt,
    stream=True
)

full_response = ""

for chunk in completion:
    delta = chunk.choices[0].delta
    if hasattr(delta, 'content'):
        full_response += delta.content

print(full_response)