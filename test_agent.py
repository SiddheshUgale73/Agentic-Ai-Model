import requests
import json

url = "http://localhost:8000/agent/chat"
headers = {"Content-Type": "application/json"}
data = {"question": "What time is it?"}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
