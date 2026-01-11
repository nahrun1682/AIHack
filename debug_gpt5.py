import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

model = "gpt-5"
messages = [{"role": "user", "content": "Hello, are you working?"}]

print(f"--- Testing {model} Non-Streaming ---")
try:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_completion_tokens=100
    )
    print("Full Response Object:")
    print(response)
    print("\nContent:", response.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")

print(f"\n--- Testing {model} Streaming ---")
try:
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        max_completion_tokens=100,
        stream=True
    )
    print("Stream Chunks:")
    count = 0
    for chunk in stream:
        print(chunk)
        if chunk.choices[0].delta.content:
            count += 1
    print(f"\nYielded content chunks: {count}")
except Exception as e:
    print(f"Error: {e}")
