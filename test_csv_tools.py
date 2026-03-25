import os
import sys
import json

# Add project root to path
sys.path.append(os.getcwd())

from app.agent.agent_service import agent_service

def test_csv_integration():
    session_id = "csv_test_user"
    
    # Test 1: Fetch details for a specific course from CSV
    q1 = "What are the fees for the Cyber Security course and what is the schedule?"
    print(f"\n[User]: {q1}")
    r1 = agent_service.run(q1, session_id=session_id)
    print(f"[Counselor]: {r1}")

    # Test 2: Partial match and placement assurance
    q2 = "Is the UI/UX course open and does it guarantee placement?"
    print(f"\n[User]: {q2}")
    r2 = agent_service.run(q2, session_id=session_id)
    print(f"[Counselor]: {r2}")

    # Test 3: Complex query combining data
    q3 = "Can you give me the full details for the Python Full Stack course? Fee for 3 months, timing, and format please."
    print(f"\n[User]: {q3}")
    r3 = agent_service.run(q3, session_id=session_id)
    print(f"[Counselor]: {r3}")

if __name__ == "__main__":
    try:
        test_csv_integration()
    except Exception as e:
        print(f"ERROR: {e}")
