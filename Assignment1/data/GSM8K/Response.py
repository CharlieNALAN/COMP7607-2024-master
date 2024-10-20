from openai import OpenAI

from Assignment1.data.GSM8K.baseline import nshot_chats, nshot_chats_taril

client = OpenAI(base_url="https://api.sambanova.ai/v1", api_key="5bd891fa-0f99-4f8c-8166-659ae73f3f35")

completion = client.chat.completions.create(
    model="Meta-Llama-3.1-8B-Instruct",
    messages=nshot_chats_taril(8,'A merchant wants to make a choice of purchase between 2 purchase plans: jewelry worth $5,000 or electronic gadgets worth $8,000. His financial advisor speculates that the jewelry market will go up 2.5% while the electronic gadgets market will rise 1.2% within the same month. If the merchant is looking to maximize profit at the end of this month by making a choice, how much profit would this be?'),
    stream=True,
    stop="#### [value]"
)

full_response = ""

for chunk in completion:
    delta = chunk.choices[0].delta
    if hasattr(delta, 'content'):
        full_response += delta.content

print(full_response)