import requests
import json

# Test adding enrollment
url = "http://localhost:8000/api/enrollments"
headers = {"Content-Type": "application/json"}
data = {
    "student_name": "Jane Doe",
    "course_name": "Python Programming",
    "email": "jane@example.com",
    "phone": "+1234567890"
}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test getting enrollments
url_get = "http://localhost:8000/api/enrollments"
try:
    response = requests.get(url_get)
    print(f"Enrollments: {response.json()}")
except Exception as e:
    print(f"Error: {e}")