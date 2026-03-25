import os
import sys
import json

# Add project root to path
sys.path.append(os.getcwd())

from app.agent.agent_service import agent_service

def test_counselor():
    session_id = "student_counseling_01"
    
    # Step 1: Student introducing self with background
    q1 = "Hello! I'm Raj, a final-year B.E. student. I'm interested in AI but don't know where to start. What do you suggest?"
    print(f"\n[Raj]: {q1}")
    r1 = agent_service.run(q1, session_id=session_id)
    print(f"[Counselor]: {r1}")

    # Step 2: Follow-up on schedule and fees
    q2 = "That sounds interesting. When are the AI batches and how much is the fee for 4 months?"
    print(f"\n[Raj]: {q2}")
    r2 = agent_service.run(q2, session_id=session_id)
    print(f"[Counselor]: {r2}")

    # Step 3: Interest in placement/enrollment
    q3 = "Does this lead to placement? I'd like to enroll if it does. My email is raj@example.com."
    print(f"\n[Raj]: {q3}")
    r3 = agent_service.run(q3, session_id=session_id)
    print(f"[Counselor]: {r3}")

if __name__ == "__main__":
    try:
        test_counselor()
    except Exception as e:
        print(f"ERROR: {e}")
