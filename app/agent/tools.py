import datetime
import json
import os
import csv
from typing import List, Dict, Optional
from app.services import rag_pipeline

# --- Paths ---
COURSES_CSV = "data/courses.csv"
ENROLLMENT_DB = "data/enrollments.json"

# --- Data Loading Helpers ---

def _load_courses() -> List[Dict]:
    courses = []
    if os.path.exists(COURSES_CSV):
        try:
            with open(COURSES_CSV, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    courses.append(row)
        except Exception as e:
            print(f"Error loading CSV: {e}")
    return courses

def _find_course(query: str) -> Optional[Dict]:
    courses = _load_courses()
    query_lower = query.lower()
    # Try exact match first, then partial
    for c in courses:
        if query_lower == c['name'].lower() or query_lower == c['course_id'].lower():
            return c
    # Partial match
    for c in courses:
        if query_lower in c['name'].lower():
            return c
    return None

def _save_enrollment(data):
    if not os.path.exists("data"):
        os.makedirs("data")
    
    enrollments = []
    if os.path.exists(ENROLLMENT_DB):
        with open(ENROLLMENT_DB, "r") as f:
            enrollments = json.load(f)
    
    enrollments.append(data)
    with open(ENROLLMENT_DB, "w") as f:
        json.dump(enrollments, f, indent=2)

# --- Tool Functions ---

def get_institute_info(query: str) -> str:
    """Provides detailed information about the institute, general policies, and placement records from the knowledge base."""
    return rag_pipeline.ask(query)

def get_current_time() -> str:
    """Returns the current date and time."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_course_status(course_name: str) -> str:
    """Checks if a specific course is currently open for admissions using the official course database."""
    course = _find_course(course_name)
    if course:
        return f"The '{course['name']}' course status is: {course['status']}. Placement Assurance: {course['placement_assurance']}."
    else:
        # Fallback to search if not in CSV
        return f"I couldn't find an exact match for '{course_name}' in our primary list. Please check the main catalog or ask me for a list of courses."

def get_lecture_schedule(course_name: str) -> str:
    """Provides the exact batch timings and format (Online/Offline) for a specific course from the official database."""
    course = _find_course(course_name)
    if course:
        return f"Schedule for '{course['name']}': {course['schedule']} (Format: {course['format']})."
    else:
        return f"No specific schedule found for '{course_name}'. Generally, batches run Mornings (8-10 AM) and Evenings (6-8 PM)."

def calculate_fees(course_name: str, duration_months: Optional[int] = None) -> str:
    """Calculates the fees for a course. Uses official duration if not specified."""
    course = _find_course(course_name)
    if course:
        base_fee = float(course['base_fee'])
        official_duration = int(course['duration_months'])
        
        # If user asks for custom duration, use it, else use official
        duration = duration_months if duration_months else official_duration
        
        # Simple math: if user wants more/less than official, scale it roughly
        total = (base_fee / official_duration) * duration
        
        return f"The total fee for '{course['name']}' ({duration} months) is ₹{total:,.2f}. Official full course duration is {official_duration} months."
    else:
        return f"Course '{course_name}' not found in the fee list. Please ask about Python, Data Science, Java, etc."

def enroll_student(student_name: str, course_name: str, email: str) -> str:
    """Enrolls a student into a specific course and saves their details."""
    course = _find_course(course_name)
    final_course_name = course['name'] if course else course_name
    
    enrollment_data = {
        "student_name": student_name,
        "course_name": final_course_name,
        "email": email,
        "date": datetime.datetime.now().isoformat()
    }
    _save_enrollment(enrollment_data)
    return f"Registration SUCCESSFUL! {student_name}, you are now enrolled in the '{final_course_name}' course. A confirmation email has been sent to {email}."

# --- Groq Metadata ---

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_institute_info",
            "description": "Get general info about institute and placement records.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "General question."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_course_status",
            "description": "Check if a course is open for admission and placement status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_name": {"type": "string", "description": "Full or partial name of the course."}
                },
                "required": ["course_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_lecture_schedule",
            "description": "Get exact batch timings and format for a course.",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_name": {"type": "string", "description": "Full or partial name of the course."}
                },
                "required": ["course_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_fees",
            "description": "Calculate fees for a course using the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_name": {"type": "string", "description": "Course name."},
                    "duration_months": {"type": "integer", "description": "Optional custom duration."}
                },
                "required": ["course_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "enroll_student",
            "description": "Register a student for a course.",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_name": {"type": "string"},
                    "course_name": {"type": "string"},
                    "email": {"type": "string", "format": "email"}
                },
                "required": ["student_name", "course_name", "email"]
            }
        }
    }
]

TOOL_MAP = {
    "get_institute_info": get_institute_info,
    "get_course_status": get_course_status,
    "get_lecture_schedule": get_lecture_schedule,
    "calculate_fees": calculate_fees,
    "enroll_student": enroll_student
}
