import os
import sys
import json

# Add project root to path
sys.path.append(os.getcwd())

from app.agent.agent_service import agent_service

def test_agent_v2():
    session_id = "test_user_123"
    
    # Step 1: Introduce self and ask about a course
    q1 = "Hi, I'm Alex. What is the current time and can you tell me if the Data Science course is open?"
    print(f"\n[Alex]: {q1}")
    r1 = agent_service.run(q1, session_id=session_id)
    print(f"[Agent]: {r1}")

    # Step 2: Ask about fees for a different course
    q2 = "Okay. How much does the Python course cost for 6 months?"
    print(f"\n[Alex]: {q2}")
    r2 = agent_service.run(q2, session_id=session_id)
    print(f"[Agent]: {r2}")

    # Step 3: Test memory and enrollment
    q3 = "That sounds good. Can you enroll me in that course? My email is alex@example.com."
    print(f"\n[Alex]: {q3}")
    r3 = agent_service.run(q3, session_id=session_id)
    print(f"[Agent]: {r3}")

    # Step 4: Final verification of memory
    q4 = "By the way, do you remember my name?"
    print(f"\n[Alex]: {q4}")
    r4 = agent_service.run(q4, session_id=session_id)
    print(f"[Agent]: {r4}")

if __name__ == "__main__":
    try:
        test_agent_v2()
    except Exception as e:
        print(f"ERROR: {e}")
