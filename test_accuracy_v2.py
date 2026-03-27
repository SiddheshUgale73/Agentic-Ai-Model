import sys
import os
import difflib

# Add current directory to path
sys.path.append(os.getcwd())

from app.agent import _find_course
from app.services import rag_pipeline

def test_fuzzy_matching():
    print("--- Testing Fuzzy Matching ---")
    test_cases = [
        ("Pyhthon", "Python Full Stack Web Development"),
        ("Data Scince", "Data Science & AI Masterclass"),
        ("Cybar Security", "Cyber Security & Ethical Hacking"),
        ("C++", "C++ Programming & DSA"),
        ("Java script", "Java Full Stack Engineering") # Might match Java, let's see
    ]
    
    for query, expected in test_cases:
        match = _find_course(query)
        result_name = match['name'] if match else "None"
        status = "PASSED" if result_name == expected else "FAILED"
        print(f"Query: '{query}' -> Match: '{result_name}' [{status}]")

def test_rag_retrieval():
    print("\n--- Testing RAG Retrieval ---")
    # Verify that we get 5 chunks
    chunks = rag_pipeline.vector_store.query("Tell me about placement assistance", top_k=5)
    print(f"Retrieved {len(chunks)} chunks.")
    for i, c in enumerate(chunks):
        print(f"Chunk {i+1} length: {len(c.split())} words")

if __name__ == "__main__":
    try:
        test_fuzzy_matching()
        test_rag_retrieval()
    except Exception as e:
        print(f"Error during verification: {e}")
