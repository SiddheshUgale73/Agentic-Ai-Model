import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=key)

print(f"Testing Groq with key: {key[:5]}...{key[-5:]}")

try:
    response = client.chat.completions.create(
        model="llama3-8b-8192", # Testing with a standard stable model
        messages=[{"role": "user", "content": "Connect test"}],
        max_tokens=10
    )
    print("SUCCESS: Groq connection established.")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"FAILED: Groq Error - {str(e)}")
