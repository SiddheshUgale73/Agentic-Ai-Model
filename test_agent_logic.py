import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from app.agent.agent_service import agent_service

# Test query that should trigger tool calling (current time)
query = "What is the current date and time?"
print(f"Testing Query: {query}")
try:
    response = agent_service.run(query)
    print(f"Agent Response: {response}")
except Exception as e:
    print(f"Error: {e}")

print("-" * 30)

# Test query that should trigger RAG tool
query = "How do I apply for a course at the institute?"
print(f"Testing Query: {query}")
try:
    response = agent_service.run(query)
    print(f"Agent Response: {response}")
except Exception as e:
    print(f"Error: {e}")
