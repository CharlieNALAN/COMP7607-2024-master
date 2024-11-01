from openai import OpenAI

from Assignment1.data.GSM8K.SKiC import organize_prompt

client = OpenAI(base_url="https://api.sambanova.ai/v1", api_key="5bd891fa-0f99-4f8c-8166-659ae73f3f35")

completion = client.chat.completions.create(
    model="Meta-Llama-3.1-8B-Instruct",
    messages=organize_prompt(question='Carla is downloading a 200 GB file. Normally she can download 2 GB/minute, but 40% of the way through the download, Windows forces a restart to install updates, which takes 20 minutes. Then Carla has to restart the download from the beginning. How load does it take to download the file?'),
    stream=True,
    stop="#### [value]"
)

full_response = ""

for chunk in completion:
    delta = chunk.choices[0].delta
    if hasattr(delta, 'content'):
        full_response += delta.content

print(full_response)