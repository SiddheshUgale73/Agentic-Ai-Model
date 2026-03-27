import difflib

# Mock courses for testing logic
mock_courses = [
    {"name": "Python Full Stack Web Development", "course_id": "PY-101"},
    {"name": "Data Science & AI Masterclass", "course_id": "DS-202"},
    {"name": "Cyber Security & Ethical Hacking", "course_id": "CY-303"},
    {"name": "Java Full Stack Engineering", "course_id": "JV-404"},
    {"name": "C++ Programming & DSA", "course_id": "CPP-505"}
]

def _find_course_logic(query: str, courses: list) -> dict:
    query_lower = query.lower()
    # 1. Exact Name/ID Match
    for c in courses:
        if query_lower == c['name'].lower() or query_lower == c['course_id'].lower():
            return c
            
    # 2. Fuzzy Match on the entire name
    names = [c['name'] for c in courses]
    matches = difflib.get_close_matches(query, names, n=1, cutoff=0.6)
    if matches:
        return next(c for c in courses if c['name'] == matches[0])

    # 3. Word-level Fuzzy Match
    query_words = query_lower.split()
    for c in courses:
        name_words = c['name'].lower().split()
        for qw in query_words:
            word_matches = difflib.get_close_matches(qw, name_words, n=1, cutoff=0.7)
            if word_matches:
                return c
                
    # 4. Word-by-word intersection (Fallback)
    for c in courses:
        name_lower = c['name'].lower()
        if all(word in name_lower for word in query_words):
            return c
            
    return None

def test_fuzzy_matching():
    print("--- Testing Fuzzy Matching Logic (Isolated) ---")
    test_cases = [
        ("Pyhthon", "Python Full Stack Web Development"),
        ("Data Scince", "Data Science & AI Masterclass"),
        ("Cybar Security", "Cyber Security & Ethical Hacking"),
        ("C++", "C++ Programming & DSA"),
        ("PY-101", "Python Full Stack Web Development")
    ]
    
    for query, expected in test_cases:
        match = _find_course_logic(query, mock_courses)
        result_name = match['name'] if match else "None"
        status = "PASSED" if result_name == expected else "FAILED"
        print(f"Query: '{query}' -> Match: '{result_name}' [{status}]")

if __name__ == "__main__":
    test_fuzzy_matching()
